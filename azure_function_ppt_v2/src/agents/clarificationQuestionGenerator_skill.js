const { BaseAgent } = require('./core/baseAgent');
const { PRESENTATION_CONFIG } = require('../config/config');
const { promptLoader } = require('../utils/promptLoader');

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

        // Load system prompt from centralized prompt management
        const systemPrompt = promptLoader.loadPrompt('clarification_question_generator_system');

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
        const spread = 5; // ±5*step slides around recommendation (increased for more options)
        const step = 3;   // Step of 3 slides between options

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

        // Ensure we have at least 11 options by adding more if needed
        if (uniqueRange.length < 11) {
            // Add more incremental options around the existing range
            const minRange = Math.min(...uniqueRange);
            const maxRange = Math.max(...uniqueRange);
            
            // Add options before min range
            for (let i = minRange - step; i >= PRESENTATION_CONFIG.min_slides && uniqueRange.length < 11; i -= step) {
                uniqueRange.unshift(i);
            }
            
            // Add options after max range
            for (let i = maxRange + step; i <= PRESENTATION_CONFIG.max_slides && uniqueRange.length < 11; i += step) {
                uniqueRange.push(i);
            }
            
            // Sort again after adding new options
            uniqueRange.sort((a, b) => a - b);
        }

        return uniqueRange;
    }
}

module.exports = { ClarificationQuestionGenerator };
