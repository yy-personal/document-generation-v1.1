const { BaseAgent } = require('./core/baseAgent');
const { SLIDE_LAYOUTS, CONTENT_TYPES } = require('../config/config');

/**
 * ContentStructurer Agent
 * Structures processed content into detailed slide-by-slide format
 */
class ContentStructurer extends BaseAgent {
    constructor() {
        super('ContentStructurer');
    }

    async process(input) {
        this.validateInput(input, ['processed_content', 'slide_estimate']);

        const { processed_content, slide_estimate, user_context } = input;

        // Create system prompt for content structuring
        const systemPrompt = this.createContentStructuringSystemPrompt();

        // Create user prompt
        const userPrompt = this.createContentStructuringUserPrompt({
            processed_content,
            slide_estimate,
            user_context
        });

        const messages = [
            this.createSystemMessage(systemPrompt),
            this.createUserMessage(userPrompt)
        ];

        // Call AI service with higher token limit for detailed structuring
        const aiResponse = await this.callAI(messages, { max_tokens: 12000 });
        const result = this.parseAIResponse(aiResponse.content);

        // Validate slide count matches estimate
        if (result.slides && result.slides.length !== slide_estimate.estimated_slides) {
            console.warn(`Slide count mismatch: structured ${result.slides.length}, estimated ${slide_estimate.estimated_slides}`);
        }

        return result;
    }

    createContentStructuringSystemPrompt() {
        const layoutDescriptions = Object.entries(SLIDE_LAYOUTS)
            .map(([key, desc]) => `- **${key}**: ${desc}`)
            .join('\n');

        const contentTypeDescriptions = Object.entries(CONTENT_TYPES)
            .map(([key, value]) => `- **${key}**: ${value}`)
            .join('\n');

        return `You are a ContentStructurer that creates detailed slide-by-slide structures for PowerPoint presentations.

## Available Slide Layouts:
${layoutDescriptions}

## Content Types:
${contentTypeDescriptions}

## Structuring Principles:
1. **Flow Logic**: Create logical progression from overview to details to conclusions
2. **Content Balance**: Distribute content evenly across slides (5-7 bullets max per slide)
3. **Visual Hierarchy**: Use appropriate layouts for different content types
4. **Engagement**: Mix content types to maintain audience interest
5. **Professional Standards**: Follow business presentation best practices

## Slide Structure Rules:
- **Title Slide**: Company info, presentation title, date, presenter
- **Agenda Slide**: 3-8 main topics, clear navigation
- **Content Slides**: 
  * Clear, descriptive titles
  * 3-7 bullet points maximum
  * Consistent formatting
  * Logical content grouping
- **Table Slides**: Use when comparing data or showing structured information
- **Two-Column Slides**: Use for comparisons, before/after, pros/cons
- **Summary Slide**: 3-6 key takeaways maximum

## Content Formatting Guidelines:
- **Bullet Points**: Concise, parallel structure, action-oriented
- **Titles**: Descriptive, not generic (e.g., "Q3 Revenue Analysis" not "Results")
- **Tables**: Clear headers, aligned data, maximum 6 columns
- **Text Length**: Keep bullet points to 1-2 lines each

## Output Format:
Return JSON with:
{
    "total_slides": number,
    "presentation_theme": "brief description of overall theme/approach",
    "slides": [
        {
            "slide_number": number,
            "layout": "SLIDE_LAYOUT_TYPE",
            "title": "slide title",
            "content_type": "CONTENT_TYPE",
            "content": {
                "bullets": ["bullet1", "bullet2", ...] // for bullet content
                OR
                "table": {
                    "headers": ["col1", "col2", ...],
                    "rows": [["row1col1", "row1col2", ...], ...]
                } // for table content
                OR
                "columns": {
                    "left": ["item1", "item2", ...],
                    "right": ["item1", "item2", ...]
                } // for two-column content
            },
            "notes": "presenter notes if relevant"
        }
    ],
    "design_guidance": "suggestions for visual design and formatting"
}

Create engaging, professional slide structures that effectively communicate the content.`;
    }

    createContentStructuringUserPrompt({ processed_content, slide_estimate, user_context }) {
        let prompt = `## Content Structuring Task:

Create a detailed slide-by-slide structure for a ${slide_estimate.estimated_slides}-slide PowerPoint presentation.

## Processed Content:
Document Type: ${processed_content.document_type}
Content Complexity: ${processed_content.content_complexity}
Executive Summary: ${processed_content.executive_summary}

## Main Topics (${processed_content.main_topics?.length || 0} topics):`;

        if (processed_content.main_topics) {
            processed_content.main_topics.forEach((topic, index) => {
                prompt += `\n\n${index + 1}. **${topic.topic}** (${topic.importance} importance)
   - Content Type: ${topic.content_type}
   - Key Points: ${topic.key_points?.join(', ') || 'None'}
   - Supporting Details: ${topic.supporting_details?.join(', ') || 'None'}
   - Estimated Slides: ${topic.estimated_slides || 1}`;
            });
        }

        if (processed_content.special_content) {
            prompt += `\n\n## Special Content:`;
            
            if (processed_content.special_content.tables?.length > 0) {
                prompt += `\n- Tables: ${processed_content.special_content.tables.join('; ')}`;
            }
            
            if (processed_content.special_content.procedures?.length > 0) {
                prompt += `\n- Procedures: ${processed_content.special_content.procedures.join('; ')}`;
            }
            
            if (processed_content.special_content.data_points?.length > 0) {
                prompt += `\n- Key Data: ${processed_content.special_content.data_points.join('; ')}`;
            }
        }

        if (user_context && user_context.trim()) {
            prompt += `\n\n## User Requirements:
${user_context}`;
        }

        prompt += `\n\n## Slide Count Breakdown:
${JSON.stringify(slide_estimate.slide_breakdown, null, 2)}

## Structuring Instructions:
1. Create exactly ${slide_estimate.estimated_slides} slides
2. Follow the slide breakdown provided by the estimator
3. Distribute main topics logically across content slides
4. Use appropriate layouts for different content types
5. Ensure each slide has focused, digestible content
6. Create smooth flow between slides
7. Include presenter notes where helpful

Design a professional, engaging presentation structure that effectively communicates all the important content.`;

        return prompt;
    }
}

module.exports = { ContentStructurer };