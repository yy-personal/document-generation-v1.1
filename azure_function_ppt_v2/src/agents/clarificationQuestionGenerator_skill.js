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
        const { conversation_content, conversation_history, requested_slide_count, document_content } = input;

        if (!conversation_content && !document_content) {
            throw new Error('ClarificationQuestionGenerator requires conversation_content or document_content');
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
            document_content,
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
3. **Content Depth**: Level of detail, overview vs detailed analysis
4. **Content Inclusion**: Examples, case studies, detailed explanations
5. **Contextual Preferences**: Based on detected content type (business/technical/educational)

### Content Format Constraints:
- Only bullet points and table formats are supported
- NO visual style or design-related questions
- Focus on content structure and information depth only

### Content Analysis Guidelines:
- **Business Content**: Focus on strategic level, audience role, implementation vs overview, depth of analysis
- **Technical Content**: Focus on technical depth, implementation detail, audience expertise, level of explanation
- **Educational Content**: Focus on learning objectives, complexity level, practical examples, step-by-step detail
- **Multi-topic Content**: Focus on primary emphasis, topic prioritization, content balance
- **Process/Procedure Content**: Focus on detail level, step-by-step vs overview, supporting explanations

### Question Focus Areas (NO Visual Style Questions):
- Content depth and detail level
- Audience understanding and expertise
- Information prioritization and emphasis
- Supporting materials (examples, case studies)
- Content organization and structure

### Field Type Rules:
- **select**: Dropdown with 3-5 predefined options + "Let agent decide" as fallback option
- **boolean**: True/false questions for yes/no preferences
- Each question must have 'required: true'
- Select questions must include "Let agent decide" as the FIRST option and default_value
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
            "options": ["Let agent decide", "option1", "option2", "option3"], // for select only - ALWAYS include "Let agent decide" as first option
            "required": true,
            "default_value": "Let agent decide" // for select questions, "default_option_or_boolean" for boolean
        }
    ],
    "content_analysis": "Brief analysis of content type and detected themes"
}`;
    }

    createCombinedUserPrompt({ conversation_content, document_content, conversation_history }) {
        let contentSection = '';
        
        if (conversation_content) {
            contentSection += `## Conversation Content:\n${conversation_content}\n\n`;
        }
        
        if (document_content) {
            contentSection += `## Document Content:\n${document_content}\n\n`;
        }
        
        return `Analyze this content and perform BOTH slide estimation AND question generation:

${contentSection}## Context:
- Content source: ${conversation_content ? 'Conversation history' : ''}${document_content ? 'Document content' : ''}${conversation_content && document_content ? ' and document content' : ''}
- Task: Provide both optimal slide count and relevant clarification questions

## Your Task:
1. **Slide Estimation**: Analyze content complexity, volume, and structure to determine optimal slide count
2. **Content Analysis**: Identify content type, themes, and complexity factors
3. **Question Generation**: Generate 3-4 highly relevant questions (select/boolean only) based on the content analysis
4. Ensure questions help customize the presentation for maximum value

## Examples of Analysis:

**For Business Content:**
- Slide Count: Consider strategic depth, implementation details, stakeholder levels
- Questions: "What's your primary audience role?" (select: ["Let agent decide", "C-level executives", "Middle management", "Department teams", "Mixed audience"])
- Content Focus: "What level of detail should we include?" (select: ["Let agent decide", "High-level overview", "Moderate detail", "Comprehensive analysis", "Executive summary"])

**For Technical Content:**
- Slide Count: Factor in technical complexity, implementation steps, supporting tables
- Questions: "What's the technical expertise of your audience?" (select: ["Let agent decide", "Beginner", "Intermediate", "Advanced", "Mixed levels"])
- Content Depth: "How much technical detail should we include?" (select: ["Let agent decide", "High-level concepts", "Moderate technical depth", "Detailed implementation", "Reference-level detail"])

**For Educational Content:**
- Slide Count: Consider learning objectives, example complexity, supporting materials
- Questions: "What's the primary learning objective?" (select: ["Let agent decide", "Awareness building", "Skill development", "Comprehensive training", "Quick reference"])
- Supporting Content: "Should we include detailed examples?" (boolean: default true)

**IMPORTANT**: ALWAYS include "Let agent decide" as the FIRST option in ALL select questions and set it as the default_value. This allows users to defer decisions to the AI when uncertain.

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
        const spread = 3; // ±3*step slides around recommendation
        const step = 3;

        // Find the nearest lower and upper multiples of step within bounds
        const min = Math.max(PRESENTATION_CONFIG.min_slides, recommendedSlides - spread * step);
        const max = Math.min(PRESENTATION_CONFIG.max_slides, recommendedSlides + spread * step);

        // Generate options in increments of step
        for (let i = min; i <= max; i += step) {
            range.push(i);
        }

        // Ensure recommendedSlides is included (in case it's not a multiple of 3)
        if (!range.includes(recommendedSlides) && recommendedSlides >= PRESENTATION_CONFIG.min_slides && recommendedSlides <= PRESENTATION_CONFIG.max_slides) {
            range.push(recommendedSlides);
        }

        // Remove duplicates and sort
        const uniqueRange = Array.from(new Set(range)).sort((a, b) => a - b);

        return uniqueRange;
    }
}

module.exports = { ClarificationQuestionGenerator };
