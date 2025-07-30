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
        const { conversation_content, aiRecommendedSlides, conversation_history } = input;

        if (!conversation_content) {
            throw new Error('ClarificationQuestionGenerator requires conversation_content');
        }

        // Create system prompt for question generation
        const systemPrompt = this.createQuestionGenerationSystemPrompt();

        // Create user prompt with content analysis
        const userPrompt = this.createQuestionGenerationUserPrompt({
            conversation_content,
            aiRecommendedSlides,
            conversation_history
        });

        const messages = [
            this.createSystemMessage(systemPrompt),
            this.createUserMessage(userPrompt)
        ];

        // Call AI service
        const aiResponse = await this.callAI(messages);
        const result = this.parseAIResponse(aiResponse.content);

        // Add slide count question with AI recommendation
        const questions = this.addSlideCountQuestion(result.questions, aiRecommendedSlides);

        return {
            questions: questions,
            content_analysis: result.content_analysis,
            reasoning: result.reasoning
        };
    }

    createQuestionGenerationSystemPrompt() {
        return `You are a ClarificationQuestionGenerator that creates contextual questions to customize PowerPoint presentations.

## Core Requirements:
- Generate 3-4 contextual clarification questions (excluding slide count)
- Questions must be either 'select' (dropdown) or 'boolean' (true/false) field types ONLY
- NO number inputs, text inputs, or other field types allowed
- Questions should be highly relevant to the conversation content
- Provide 3-5 meaningful options for each 'select' question

## Question Categories to Consider:
1. **Audience Level**: Technical expertise, business level, educational background
2. **Content Focus**: Which aspects to emphasize from the conversation
3. **Presentation Style**: Format, depth, visual approach
4. **Content Inclusion**: Examples, case studies, detailed analysis
5. **Contextual Preferences**: Based on detected content type (business/technical/educational)

## Content Analysis Guidelines:
- **Business Content**: Focus on strategic level, audience role, implementation vs overview
- **Technical Content**: Focus on technical depth, implementation detail, audience expertise
- **Educational Content**: Focus on learning objectives, complexity level, practical examples
- **Multi-topic Content**: Focus on primary emphasis, topic prioritization
- **Process/Procedure Content**: Focus on detail level, step-by-step vs overview

## Field Type Rules:
- **select**: Dropdown with 3-5 predefined options
- **boolean**: True/false questions for yes/no preferences
- Each question must have 'required: true'
- Select questions must have meaningful default_value
- Boolean questions default to true or false based on common preference

## Output Format:
Return JSON with:
{
    "questions": [
        {
            "id": "unique_question_id",
            "question": "Clear question text with context",
            "field_type": "select" | "boolean",
            "options": ["option1", "option2", "option3"] // for select only
            "required": true,
            "default_value": "default_option_or_boolean"
        }
    ],
    "content_analysis": "Brief analysis of content type and detected themes",
    "reasoning": "Why these specific questions were chosen for this content"
}`;
    }

    createQuestionGenerationUserPrompt({ conversation_content, aiRecommendedSlides, conversation_history }) {
        return `Analyze this conversation content and generate 3-4 contextual clarification questions:

## Conversation Content:
${conversation_content}

## Context:
- AI recommended slides: ${aiRecommendedSlides || 'Not provided'}
- Content source: Conversation history with user

## Your Task:
1. Analyze the content type, themes, and complexity
2. Identify what customization options would be most valuable
3. Generate 3-4 highly relevant questions (select/boolean only)
4. Ensure questions help customize the presentation for maximum value

## Examples of Good Questions:

**For Business Content:**
- "What's your primary audience role?" (select: ["C-level executives", "Middle management", "Department teams", "Mixed audience"])
- "Should we focus on strategic overview or implementation details?" (select: ["Strategic overview", "Implementation roadmap", "Balanced approach", "Deep implementation"])

**For Technical Content:**
- "What's the technical expertise of your audience?" (select: ["Beginner", "Intermediate", "Advanced", "Mixed levels"])
- "Should we include code examples and technical demos?" (boolean: true)

**For Educational Content:**
- "What's the primary learning objective?" (select: ["Awareness building", "Skill development", "Comprehensive training", "Quick reference"])
- "Should we include hands-on exercises and examples?" (boolean: true)

Remember: NO number inputs, only select dropdowns and boolean toggles!`;
    }

    addSlideCountQuestion(generatedQuestions, aiRecommendedSlides) {
        // Generate slide count range around AI recommendation
        const slideRange = this.generateSlideRange(aiRecommendedSlides || PRESENTATION_CONFIG.default_slides);
        
        const slideCountQuestion = {
            id: "slide_count",
            question: `How many slides would you like in your presentation? (Recommended: ${aiRecommendedSlides || PRESENTATION_CONFIG.default_slides} slides based on AI analysis)`,
            field_type: "select",
            options: slideRange,
            required: true,
            default_value: aiRecommendedSlides || PRESENTATION_CONFIG.default_slides,
            validation: { 
                min: PRESENTATION_CONFIG.min_slides, 
                max: PRESENTATION_CONFIG.max_slides 
            },
            recommendation: aiRecommendedSlides || PRESENTATION_CONFIG.default_slides,
            recommendation_source: aiRecommendedSlides ? "AI analysis of your content" : "default recommendation",
            ai_generated: !!aiRecommendedSlides
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