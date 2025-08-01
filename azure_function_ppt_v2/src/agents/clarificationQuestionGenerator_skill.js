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
        const systemPromptTemplate = promptLoader.loadPrompt('clarification_question_generator_system');
        
        // Extract only the system instructions (everything before User Prompt Template)
        const systemPromptMatch = systemPromptTemplate.match(/([\s\S]*?)(?=## User Prompt Template:|$)/);
        const systemPrompt = systemPromptMatch ? systemPromptMatch[1].trim() : systemPromptTemplate;

        // Create user prompt with content analysis using template
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
        
        // Enhanced JSON parsing with validation for this specific agent
        let result;
        try {
            result = this.parseAIResponse(aiResponse.content);
            
            // Validate required fields for ClarificationQuestionGenerator
            if (!result.estimated_slides || !result.questions || !Array.isArray(result.questions)) {
                throw new Error('Missing required fields: estimated_slides or questions array');
            }
            
        } catch (error) {
            console.error('[ClarificationQuestionGenerator] AI Response parsing failed:', error.message);
            console.error('[ClarificationQuestionGenerator] Raw AI Response:', aiResponse.content.substring(0, 1000));
            
            // Create fallback response
            result = {
                estimated_slides: PRESENTATION_CONFIG.default_slides,
                content_complexity: "medium",
                slide_breakdown: {
                    title_slide: 1,
                    agenda_slides: 1,
                    content_slides: PRESENTATION_CONFIG.default_slides - 3,
                    conclusion_slides: 1,
                    total: PRESENTATION_CONFIG.default_slides
                },
                complexity_factors: ["content_volume", "technical_complexity"],
                reasoning: "Fallback estimation due to AI response parsing error",
                confidence: 0.5,
                questions: [
                    {
                        id: "audience_level",
                        question: "What is the expertise level of your audience?",
                        field_type: "select",
                        options: ["Let agent decide", "Beginner", "Intermediate", "Advanced"],
                        required: true,
                        default_value: "Let agent decide"
                    }
                ],
                content_analysis: "Unable to analyze due to parsing error - using default settings"
            };
        }

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
        // Load user prompt template from external file
        const userPromptTemplate = promptLoader.loadPrompt('clarification_question_generator_system');
        
        // Extract user prompt section from the system prompt file
        const userPromptMatch = userPromptTemplate.match(/## User Prompt Template:\s*([\s\S]*?)(?=## Output Format:|$)/);
        if (!userPromptMatch) {
            throw new Error('User prompt template not found in clarification_question_generator_system.txt');
        }
        
        let userPrompt = userPromptMatch[1].trim();
        
        // Prepare content section
        let contentSection = '';
        if (conversation_content) {
            contentSection += `## Conversation Content:\n${conversation_content}\n\n`;
        }
        if (document_content) {
            contentSection += `## Document Content:\n${document_content}\n\n`;
        }
        
        // Prepare content source description
        let contentSource = '';
        if (conversation_content && document_content) {
            contentSource = 'Conversation history and document content';
        } else if (conversation_content) {
            contentSource = 'Conversation history';
        } else if (document_content) {
            contentSource = 'Document content';
        } else {
            contentSource = 'No content provided';
        }
        
        // Replace template variables
        userPrompt = userPrompt.replace('{CONTENT_SECTION}', contentSection);
        userPrompt = userPrompt.replace('{CONTENT_SOURCE}', contentSource);
        
        return userPrompt;
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
