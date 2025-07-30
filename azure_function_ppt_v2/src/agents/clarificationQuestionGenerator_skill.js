const { BaseAgent } = require('./core/baseAgent');
const { PRESENTATION_CONFIG } = require('../config/config');

/**
 * ClarificationQuestionGenerator Agent
 * Dynamically generates contextual clarification questions based on conversation content
 */
class ClarificationQuestionGenerator extends BaseAgent {
    constructor() {
        super('ClarificationQuestionGenerator');
    }

    async process(input) {
        const { conversation_content, conversation_history, requested_slide_count } = input;

        if (!conversation_content) {
            throw new Error('ClarificationQuestionGenerator requires conversation_content');
        }

        // If user specified slide count, use it (with bounds checking)
        if (requested_slide_count) {
            const slideCount = Math.max(
                PRESENTATION_CONFIG.min_slides,
                Math.min(PRESENTATION_CONFIG.max_slides, parseInt(requested_slide_count))
            );
            
            const questions = this.addSlideCountQuestion([], slideCount, true);
            
            return {
                estimated_slides: slideCount,
                content_complexity: "user_specified",
                reasoning: `User requested ${requested_slide_count} slides. Adjusted to ${slideCount} slides within system limits.`,
                confidence: 1.0,
                user_specified: true,
                questions: questions,
                content_analysis: "User-specified slide count"
            };
        }

        // Create combined system prompt for slide estimation AND question generation
        const systemPrompt = this.createCombinedSystemPrompt();

        // Create user prompt with content analysis
        const userPrompt = this.createCombinedUserPrompt({
            conversation_content,
            conversation_history
        });

        const messages = [
            this.createSystemMessage(systemPrompt),
            this.createUserMessage(userPrompt)
        ];

        // Call AI service ONCE for both slide estimation and question generation
        const aiResponse = await this.callAI(messages);
        const result = this.parseAIResponse(aiResponse.content);

        // Ensure slide count is within bounds
        result.estimated_slides = Math.max(
            PRESENTATION_CONFIG.min_slides,
            Math.min(PRESENTATION_CONFIG.max_slides, result.estimated_slides)
        );

        // Add slide count question with AI recommendation
        const questions = this.addSlideCountQuestion(result.questions, result.estimated_slides);

        return {
            estimated_slides: result.estimated_slides,
            content_complexity: result.content_complexity,
            slide_breakdown: result.slide_breakdown,
            complexity_factors: result.complexity_factors,
            reasoning: result.reasoning,
            confidence: result.confidence || 0.8,
            user_specified: false,
            questions: questions,
            content_analysis: result.content_analysis
        };
    }

    createCombinedSystemPrompt() {
        return `You are a ClarificationQuestionGenerator that performs TWO tasks in one analysis:
1. **Slide Count Estimation**: Determine optimal slide count based on content analysis
2. **Question Generation**: Create contextual clarification questions for presentation customization

## TASK 1: Slide Count Estimation

### Slide Count Guidelines:
- **Minimum**: ${PRESENTATION_CONFIG.min_slides} slides (for any presentation)
- **Maximum**: ${PRESENTATION_CONFIG.max_slides} slides (hard limit)
- **Default**: ${PRESENTATION_CONFIG.default_slides} slides (for medium complexity)

### Estimation Factors:
1. **Content Volume**: How much information needs to be presented
2. **Topic Complexity**: How detailed each topic needs to be
3. **Content Types**: Different content types require different slide counts
4. **Presentation Flow**: Need for transitions, summaries, conclusions

### Slide Allocation Strategy:
- **Title Slide**: Always 1 slide
- **Agenda/Overview**: 1-2 slides depending on complexity
- **Main Content**: Based on topics and complexity
- **Supporting Content**: Tables, procedures, detailed analysis
- **Conclusion/Summary**: 1-2 slides
- **Thank You/Next Steps**: 1 slide

### Content Type Slide Requirements:
- **Simple Topic**: 1 slide
- **Complex Topic**: 2-3 slides
- **Data/Table Content**: 1-2 slides per table
- **Procedure/Process**: 1 slide per 3-5 steps
- **Comparison**: 1-2 slides depending on items compared

## TASK 2: Question Generation

### Core Requirements:
- Generate 3-4 contextual clarification questions (excluding slide count)
- Questions must be either 'select' (dropdown) or 'boolean' (true/false) field types ONLY
- NO number inputs, text inputs, or other field types allowed
- Questions should be highly relevant to the conversation content
- Provide 3-5 meaningful options for each 'select' question

### Question Categories to Consider:
1. **Audience Level**: Technical expertise, business level, educational background
2. **Content Focus**: Which aspects to emphasize from the conversation
3. **Presentation Style**: Format, depth, visual approach
4. **Content Inclusion**: Examples, case studies, detailed analysis
5. **Contextual Preferences**: Based on detected content type (business/technical/educational)

### Content Analysis Guidelines:
- **Business Content**: Focus on strategic level, audience role, implementation vs overview
- **Technical Content**: Focus on technical depth, implementation detail, audience expertise
- **Educational Content**: Focus on learning objectives, complexity level, practical examples
- **Multi-topic Content**: Focus on primary emphasis, topic prioritization
- **Process/Procedure Content**: Focus on detail level, step-by-step vs overview

### Field Type Rules:
- **select**: Dropdown with 3-5 predefined options
- **boolean**: True/false questions for yes/no preferences
- Each question must have 'required: true'
- Select questions must have meaningful default_value
- Boolean questions default to true or false based on common preference

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
    "reasoning": "explanation of slide count decision and question selection",
    "confidence": number_between_0_and_1,
    "questions": [
        {
            "id": "unique_question_id",
            "question": "Clear question text with context",
            "field_type": "select" | "boolean",
            "options": ["option1", "option2", "option3"], // for select only
            "required": true,
            "default_value": "default_option_or_boolean"
        }
    ],
    "content_analysis": "Brief analysis of content type and detected themes"
}`;
    }

    createCombinedUserPrompt({ conversation_content, conversation_history }) {
        return `Analyze this conversation content and perform BOTH slide estimation AND question generation:

## Conversation Content:
${conversation_content}

## Context:
- Content source: Conversation history with user
- Task: Provide both optimal slide count and relevant clarification questions

## Your Task:
1. **Slide Estimation**: Analyze content complexity, volume, and structure to determine optimal slide count
2. **Content Analysis**: Identify content type, themes, and complexity factors
3. **Question Generation**: Generate 3-4 highly relevant questions (select/boolean only) based on the content analysis
4. Ensure questions help customize the presentation for maximum value

## Examples of Analysis:

**For Business Content:**
- Slide Count: Consider strategic depth, implementation details, stakeholder levels
- Questions: "What's your primary audience role?" (select: ["C-level executives", "Middle management", "Department teams", "Mixed audience"])

**For Technical Content:**
- Slide Count: Factor in technical complexity, code examples, implementation steps
- Questions: "What's the technical expertise of your audience?" (select: ["Beginner", "Intermediate", "Advanced", "Mixed levels"])

**For Educational Content:**
- Slide Count: Consider learning objectives, exercise time, example complexity
- Questions: "What's the primary learning objective?" (select: ["Awareness building", "Skill development", "Comprehensive training", "Quick reference"])

Perform both slide estimation and question generation in a single comprehensive analysis!`;
    }

    addSlideCountQuestion(generatedQuestions, aiRecommendedSlides, userSpecified = false) {
        // Generate slide count range around AI recommendation
        const slideRange = this.generateSlideRange(aiRecommendedSlides || PRESENTATION_CONFIG.default_slides);
        
        const recommendationSource = userSpecified ? "user specification" : 
                                    aiRecommendedSlides ? "AI analysis of your content" : "default recommendation";
        
        const slideCountQuestion = {
            id: "slide_count",
            question: `How many slides would you like in your presentation? (Recommended: ${aiRecommendedSlides || PRESENTATION_CONFIG.default_slides} slides based on ${recommendationSource})`,
            field_type: "select",
            options: slideRange,
            required: true,
            default_value: aiRecommendedSlides || PRESENTATION_CONFIG.default_slides,
            validation: { 
                min: PRESENTATION_CONFIG.min_slides, 
                max: PRESENTATION_CONFIG.max_slides 
            },
            recommendation: aiRecommendedSlides || PRESENTATION_CONFIG.default_slides,
            recommendation_source: recommendationSource,
            ai_generated: !!aiRecommendedSlides && !userSpecified
        };

        // Add slide count as first question, followed by generated questions
        return [slideCountQuestion, ...generatedQuestions];
    }

    generateSlideRange(recommendedSlides) {
        const range = [];
        const spread = 3; // ±3 slides around recommendation
        
        // Generate range around recommendation
        for (let i = recommendedSlides - spread; i <= recommendedSlides + spread; i++) {
            // Ensure within config limits
            if (i >= PRESENTATION_CONFIG.min_slides && i <= PRESENTATION_CONFIG.max_slides) {
                range.push(i);
            }
        }
        
        // Ensure minimum 5 options and add boundary values if needed
        if (range.length < 5) {
            // Add lower values if recommendation is high
            if (recommendedSlides > PRESENTATION_CONFIG.min_slides + 2) {
                for (let i = PRESENTATION_CONFIG.min_slides; i < range[0]; i++) {
                    range.unshift(i);
                    if (range.length >= 7) break; // Don't make dropdown too long
                }
            }
            
            // Add higher values if recommendation is low
            if (recommendedSlides < PRESENTATION_CONFIG.max_slides - 2) {
                for (let i = range[range.length - 1] + 1; i <= PRESENTATION_CONFIG.max_slides; i++) {
                    range.push(i);
                    if (range.length >= 7) break; // Don't make dropdown too long
                }
            }
        }
        
        return range.sort((a, b) => a - b);
    }
}

module.exports = { ClarificationQuestionGenerator };