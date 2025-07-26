const { BaseAgent } = require('./core/baseAgent');
const { PRESENTATION_CONFIG } = require('../config/config');

/**
 * SlideEstimator Agent
 * Analyzes content complexity and estimates optimal slide count
 */
class SlideEstimator extends BaseAgent {
    constructor() {
        super('SlideEstimator');
    }

    async process(input) {
        // Can work with just document content or with processed content
        const { document_content, processed_content, user_context } = input;

        if (!document_content && !processed_content) {
            throw new Error('SlideEstimator requires either document_content or processed_content');
        }

        // Create system prompt for slide estimation
        const systemPrompt = this.createSlideEstimationSystemPrompt();

        // Create user prompt
        const userPrompt = this.createSlideEstimationUserPrompt({
            document_content,
            processed_content,
            user_context
        });

        const messages = [
            this.createSystemMessage(systemPrompt),
            this.createUserMessage(userPrompt)
        ];

        // Call AI service
        const aiResponse = await this.callAI(messages);
        const result = this.parseAIResponse(aiResponse.content);

        // Ensure slide count is within bounds
        result.estimated_slides = Math.max(
            PRESENTATION_CONFIG.min_slides,
            Math.min(PRESENTATION_CONFIG.max_slides, result.estimated_slides)
        );

        return result;
    }

    createSlideEstimationSystemPrompt() {
        return `You are a SlideEstimator that determines optimal slide count for PowerPoint presentations.

## Slide Count Guidelines:
- **Minimum**: ${PRESENTATION_CONFIG.min_slides} slides (for any presentation)
- **Maximum**: ${PRESENTATION_CONFIG.max_slides} slides (hard limit)
- **Default**: ${PRESENTATION_CONFIG.default_slides} slides (for medium complexity)

## Estimation Factors:
1. **Content Volume**: How much information needs to be presented
2. **Topic Complexity**: How detailed each topic needs to be
3. **Content Types**: Different content types require different slide counts
4. **Presentation Flow**: Need for transitions, summaries, conclusions

## Slide Allocation Strategy:
- **Title Slide**: Always 1 slide
- **Agenda/Overview**: 1-2 slides depending on complexity
- **Main Content**: Based on topics and complexity
- **Supporting Content**: Tables, procedures, detailed analysis
- **Conclusion/Summary**: 1-2 slides
- **Thank You/Next Steps**: 1 slide

## Content Type Slide Requirements:
- **Simple Topic**: 1 slide
- **Complex Topic**: 2-3 slides
- **Data/Table Content**: 1-2 slides per table
- **Procedure/Process**: 1 slide per 3-5 steps
- **Comparison**: 1-2 slides depending on items compared

## Output Format:
Return JSON with:
{
    "estimated_slides": number,
    "content_complexity": "low|medium|high",
    "slide_breakdown": {
        "title_slide": 1,
        "agenda_slides": number,
        "content_slides": number,
        "conclusion_slides": number,
        "total": number
    },
    "complexity_factors": ["factor1", "factor2", ...],
    "reasoning": "explanation of slide count decision",
    "user_feedback": "message to show user about estimated slides"
}

Be precise with slide estimation - users need accurate expectations.`;
    }

    createSlideEstimationUserPrompt({ document_content, processed_content, user_context }) {
        let prompt = `## Slide Count Estimation Task:

Analyze the content and estimate the optimal number of slides for a professional PowerPoint presentation.

## Configuration Limits:
- Minimum slides: ${PRESENTATION_CONFIG.min_slides}
- Maximum slides: ${PRESENTATION_CONFIG.max_slides}
- Target range: ${PRESENTATION_CONFIG.min_slides}-${PRESENTATION_CONFIG.default_slides} for most presentations`;

        if (processed_content) {
            prompt += `\n\n## Processed Content Analysis:
Document Type: ${processed_content.document_type}
Content Complexity: ${processed_content.content_complexity}
Main Topics Count: ${processed_content.main_topics?.length || 0}

Topics:`;
            if (processed_content.main_topics) {
                processed_content.main_topics.forEach((topic, index) => {
                    prompt += `\n${index + 1}. ${topic.topic} (${topic.importance} importance, ${topic.key_points?.length || 0} key points)`;
                });
            }

            if (processed_content.special_content) {
                prompt += `\n\nSpecial Content:`;
                if (processed_content.special_content.tables?.length > 0) {
                    prompt += `\n- Tables: ${processed_content.special_content.tables.length}`;
                }
                if (processed_content.special_content.procedures?.length > 0) {
                    prompt += `\n- Procedures: ${processed_content.special_content.procedures.length}`;
                }
            }
        } else if (document_content) {
            // Working with raw document content
            const contentPreview = document_content.length > 1000 
                ? document_content.substring(0, 1000) + '...' 
                : document_content;
            
            prompt += `\n\n## Raw Document Content:
${contentPreview}`;
        }

        if (user_context && user_context.trim()) {
            prompt += `\n\n## User Context:
${user_context}`;
        }

        prompt += `\n\n## Estimation Requirements:
1. Count distinct topics that need separate slides
2. Consider content complexity and detail level required
3. Account for standard presentation structure (title, agenda, conclusion)
4. Factor in special content types (tables, procedures, comparisons)
5. Ensure slide count is within configured limits

Provide a precise slide count estimate with clear reasoning.`;

        return prompt;
    }
}

module.exports = { SlideEstimator };