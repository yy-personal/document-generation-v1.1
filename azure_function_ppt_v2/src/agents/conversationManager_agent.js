const { BaseAgent } = require('./core/baseAgent');
const { PRESENTATION_CONFIG } = require('../config/config');

/**
 * ConversationManager Agent
 * Handles conversation flow, user intent analysis, and context management
 */
class ConversationManager extends BaseAgent {
    constructor() {
        super('ConversationManager');
    }

    async process(input) {
        this.validateInput(input, ['user_message']);

        const { user_message, session_id, conversation_history = [], entra_id } = input;

        // Check for exact bracket triggers first
        const bracketTrigger = this.detectBracketTriggers(user_message);
        
        if (bracketTrigger) {
            return this.handleBracketTrigger(bracketTrigger, input);
        }

        // Extract document content if present
        const documentInfo = this.extractDocumentContent(user_message);

        // Create system prompt for conversation management
        const systemPrompt = this.createConversationSystemPrompt();

        // Create user prompt with context
        const userPrompt = this.createConversationUserPrompt({
            user_message: documentInfo.user_text,
            has_document: documentInfo.has_document,
            document_content: documentInfo.document_content,
            conversation_history,
            session_id
        });

        const messages = [
            this.createSystemMessage(systemPrompt),
            this.createUserMessage(userPrompt)
        ];

        // Call AI service
        const aiResponse = await this.callAI(messages);
        const result = this.parseAIResponse(aiResponse.content);

        // Add document content to result if present in current message
        if (documentInfo.has_document) {
            result.document_content = documentInfo.document_content;
            result.has_document_content = true;
            result.content_source = result.content_source || 'document';
        } else {
            // Check if document content exists in conversation history
            const documentFromHistory = this.extractDocumentFromHistory(conversation_history);
            if (documentFromHistory) {
                result.document_content = documentFromHistory;
                result.has_document_content = true;
                result.content_source = result.content_source || 'document';
            } else {
                result.has_document_content = false;
                // If no document but conversation_content exists, set content source
                if (result.conversation_content && result.conversation_content.trim()) {
                    result.content_source = result.content_source || 'conversation';
                }
            }
        }

        return result;
    }

    createConversationSystemPrompt() {
        return `You are a ConversationManager for a PowerPoint generation service. Your role is to:

1. **Analyze user intent** - Determine what the user wants to do
2. **Manage conversation flow** - Handle follow-up questions and clarifications
3. **Detect generation requests** - Identify when user wants to create a presentation
4. **Provide helpful responses** - Guide users through the process
5. **Extract content from conversations** - Build presentation content from user messages

## User Intent Categories:
- **CLARIFICATION**: User asking questions about their document or process
- **CONTEXT_ADDITION**: User providing additional context or requirements
- **PRESENTATION_INITIATE**: User clicked "Create Presentation" - needs slide recommendation
- **PRESENTATION_GENERATE**: User confirmed slide count - ready to generate PowerPoint
- **GENERAL_INQUIRY**: General questions about the service
- **CONTENT_BUILDING**: User providing topic details for presentation

## Content Sources:
- **Documents**: Provided with [document_start] and [document_end] tags containing base64 or text content
- **Conversation Content**: Topics, details, and requirements provided through conversation
- **Mixed Approach**: Combination of documents and conversational context
- **Document-Free**: Presentations built entirely from conversation content

## Two-Stage Workflow:

**Stage 1: PRESENTATION_INITIATE** (Frontend "Create Presentation" button)
- User clicks "Create Presentation" button on frontend
- Message: "INITIATE_PRESENTATION_REQUEST" 
- Response: Show slide recommendation with popup
- Set "should_generate_presentation": false
- Set "show_slide_recommendation": true

**Stage 2: PRESENTATION_GENERATE** (User confirms slide count)
- User confirms slide count from popup
- Message: "GENERATE_PRESENTATION_WITH_X_SLIDES" (e.g., "GENERATE_PRESENTATION_WITH_12_SLIDES")
- Response: Generate actual PowerPoint
- Set "should_generate_presentation": true
- Set "requested_slide_count": X

## Exact Trigger Patterns:
- **Stage 1**: "[create_presentation]" - Frontend "Create Presentation" button
- **Stage 2**: "[slide_number_input]15" - User selects 15 slides from popup (number appended)

## Detection Logic:
- Look for exact "[create_presentation]" in user_message → set show_slide_recommendation: true
- Look for "[slide_number_input]" followed by number → extract number and set should_generate_presentation: true

## Content Extraction:
When no document is provided, extract presentation content from:
- User-specified topics and subtopics
- Details provided in conversation
- Requirements and preferences mentioned
- Previous conversation context

## Response Format:
Return JSON with:
{
    "intent": "CLARIFICATION|CONTEXT_ADDITION|PRESENTATION_INITIATE|PRESENTATION_GENERATE|GENERAL_INQUIRY|CONTENT_BUILDING",
    "should_generate_presentation": boolean,
    "show_slide_recommendation": boolean,
    "user_context": "summary of user's specific requirements or questions",
    "conversation_content": "extracted content for presentation (when no document)",
    "content_source": "document|conversation|mixed",
    "response_text": "your response to the user",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of your decision",
    "requested_slide_count": "number if user specified slide count, null otherwise"
}

Be conversational, helpful, and guide users through the presentation creation process.`;
    }

    createConversationUserPrompt({ user_message, has_document, document_content, conversation_history, session_id }) {
        let prompt = `## Current User Message:
"${user_message}"

## Document Status:
${has_document ? 'Document provided: Yes' : 'Document provided: No'}

## Session Context:
Session ID: ${session_id || 'New session'}`;

        if (conversation_history && conversation_history.length > 0) {
            prompt += `\n\n## Conversation History:`;
            
            // Handle different conversation history formats
            if (Array.isArray(conversation_history) && conversation_history.length > 0) {
                // Check if it's the new format with conversation object
                if (conversation_history[0].conversation) {
                    // New format: extract Q&A pairs from conversation array
                    const conversations = conversation_history[0].conversation;
                    conversations.forEach((conv, index) => {
                        prompt += `\nQuestion ${index + 1}: ${conv.question}`;
                        prompt += `\nResponse ${index + 1}: ${conv.response}`;
                    });
                } else {
                    // Standard format: include last few messages for context
                    const recentHistory = conversation_history.slice(-6);
                    recentHistory.forEach((msg, index) => {
                        prompt += `\n${msg.role}: ${msg.content}`;
                    });
                }
            }
        }

        if (has_document && document_content) {
            // Include first part of document for context
            const docPreview = document_content.length > 500 
                ? document_content.substring(0, 500) + '...' 
                : document_content;
            
            prompt += `\n\n## Document Content Preview:
${docPreview}`;
        }

        prompt += `\n\n## Task:
Analyze the user's message in context and determine their intent. Decide whether they want to generate a presentation or are having a conversation about their document/requirements.

Provide a helpful response and indicate whether presentation generation should proceed.`;

        return prompt;
    }

    /**
     * Extract document content from conversation history
     * @param {Array} conversationHistory - Array of conversation messages
     * @returns {string|null} Document content if found, null otherwise
     */
    extractDocumentFromHistory(conversationHistory) {
        if (!conversationHistory || conversationHistory.length === 0) {
            return null;
        }

        // Look through conversation history for document content
        for (const message of conversationHistory) {
            if (message.role === 'user' && message.content) {
                const documentInfo = this.extractDocumentContent(message.content);
                if (documentInfo.has_document) {
                    console.log('[ConversationManager] Found document content in conversation history');
                    return documentInfo.document_content;
                }
            }
        }

        return null;
    }

    /**
     * Detect exact bracket triggers in user message
     * @param {string} userMessage - The user's message
     * @returns {object|null} Trigger info if found, null otherwise
     */
    detectBracketTriggers(userMessage) {
        if (!userMessage) return null;

        // Normalize the message by trimming whitespace
        const normalizedMessage = userMessage.trim();

        // Stage 1: [create_presentation]
        if (normalizedMessage.includes('[create_presentation]')) {
            return {
                type: 'create_presentation',
                stage: 1
            };
        }

        // Stage 2: [clarification_answers]{JSON_answers}
        const answersMatch = normalizedMessage.match(/\[clarification_answers\](.+)/);
        if (answersMatch) {
            try {
                const answers = JSON.parse(answersMatch[1]);
                return {
                    type: 'clarification_answers',
                    stage: 2,
                    answers: answers
                };
            } catch (error) {
                console.error('Failed to parse clarification answers:', error);
                return null;
            }
        }

        return null;
    }

    /**
     * Handle bracket triggers without AI processing
     * @param {object} trigger - Trigger information
     * @param {object} input - Original input data
     * @returns {object} Response for the trigger
     */
    handleBracketTrigger(trigger, input) {
        const { conversation_history = [] } = input;

        if (trigger.type === 'create_presentation') {
            // Stage 1: Need AI slide estimation first, then generate questions
            return {
                intent: "PRESENTATION_INITIATE",
                should_generate_presentation: false,
                show_clarification_questions: true,
                need_slide_estimation: true, // Flag to call SlideEstimator first
                user_context: "User clicked Create Presentation button",
                conversation_content: this.extractConversationContent(conversation_history),
                content_source: "conversation",
                response_text: "Analyzing your content to recommend optimal slide count...",
                confidence: 1.0,
                reasoning: "Frontend create presentation button triggered - need AI slide estimation",
                requested_slide_count: null,
                has_document_content: false
            };
        }

        if (trigger.type === 'clarification_answers') {
            // Stage 2: Return generation request with clarification answers
            return {
                intent: "PRESENTATION_GENERATE",
                should_generate_presentation: true,
                show_clarification_questions: false,
                clarification_answers: trigger.answers,
                user_context: "User provided clarification answers for presentation customization",
                conversation_content: this.extractConversationContent(conversation_history),
                content_source: "conversation",
                response_text: "Generating customized presentation based on your answers...",
                confidence: 1.0,
                reasoning: "User provided clarification answers from popup",
                requested_slide_count: trigger.answers.slide_count || null,
                has_document_content: false
            };
        }

        return null;
    }

    /**
     * Extract content from conversation history for presentation
     * @param {Array} conversationHistory - Array of conversation messages
     * @returns {string} Extracted conversation content
     */
    extractConversationContent(conversationHistory) {
        if (!conversationHistory || conversationHistory.length === 0) {
            return "";
        }

        // Handle new conversation format with Q&A pairs
        if (conversationHistory[0] && conversationHistory[0].conversation) {
            const conversations = conversationHistory[0].conversation;
            let content = "Presentation content based on conversation:\n\n";
            
            conversations.forEach((conv, index) => {
                content += `Topic ${index + 1}: ${conv.question}\n`;
                content += `Details: ${conv.response}\n\n`;
            });
            
            return content;
        }

        // Handle standard conversation format
        let content = "Presentation content based on conversation:\n\n";
        conversationHistory.forEach((msg, index) => {
            if (msg.role === 'user') {
                content += `User Input ${index + 1}: ${msg.content}\n`;
            } else if (msg.role === 'assistant') {
                content += `Response ${index + 1}: ${msg.content}\n\n`;
            }
        });

        return content;
    }

    /**
     * Generate up to 5 clarification questions for PowerPoint customization
     * @param {Array} conversationHistory - Array of conversation messages
     * @param {number} aiRecommendedSlides - AI-recommended slide count from SlideEstimator
     * @returns {Array} Array of question objects with field types
     */
    generateClarificationQuestions(conversationHistory, aiRecommendedSlides = null) {
        // Analyze conversation to determine relevant questions
        const conversationContent = this.extractConversationContent(conversationHistory);
        const hasMultipleTopics = this.detectMultipleTopics(conversationHistory);
        const topics = this.extractTopics(conversationHistory);

        // Use AI recommendation if provided, otherwise fallback to simple calculation
        const recommendedSlides = aiRecommendedSlides || this.calculateRecommendedSlides(conversationContent, hasMultipleTopics);
        const recommendationSource = aiRecommendedSlides ? "AI analysis of your content" : "content analysis";

        const questions = [];

        // Question 1: Slide count with AI recommendation as dropdown range (always included)
        const slideRange = this.generateSlideRange(recommendedSlides);
        questions.push({
            id: "slide_count",
            question: `How many slides would you like in your presentation? (Recommended: ${recommendedSlides} slides based on ${recommendationSource})`,
            field_type: "select",
            options: slideRange,
            required: true,
            default_value: recommendedSlides,
            validation: { min: PRESENTATION_CONFIG.min_slides, max: PRESENTATION_CONFIG.max_slides },
            recommendation: recommendedSlides,
            recommendation_source: recommendationSource,
            ai_generated: !!aiRecommendedSlides
        });

        // Question 2: Presentation focus (if multiple topics detected)
        if (hasMultipleTopics && topics.length > 1) {
            questions.push({
                id: "focus_area",
                question: "Which topic should be the main focus of your presentation?",
                field_type: "select",
                options: topics.slice(0, 4), // Limit to 4 options
                required: true,
                default_value: topics[0]
            });
        }

        // Question 3: Audience level
        questions.push({
            id: "audience_level",
            question: "What is the technical level of your audience?",
            field_type: "select",
            options: ["Beginner", "Intermediate", "Advanced", "Mixed audience"],
            required: true,
            default_value: "Intermediate"
        });

        // Question 4: Include detailed examples
        questions.push({
            id: "include_examples",
            question: "Would you like detailed examples and case studies included?",
            field_type: "boolean",
            required: true,
            default_value: true
        });

        // Question 5: Presentation style (context-dependent)
        if (this.isBusinessContent(conversationContent)) {
            questions.push({
                id: "business_style",
                question: "What type of business presentation format do you prefer?",
                field_type: "select",
                options: ["Executive Summary", "Detailed Analysis", "Strategic Overview", "Training Material"],
                required: true,
                default_value: "Strategic Overview"
            });
        } else if (this.isTechnicalContent(conversationContent)) {
            questions.push({
                id: "technical_depth",
                question: "How much technical detail should be included?",
                field_type: "select",
                options: ["High-level overview", "Moderate detail", "Deep technical dive", "Implementation focused"],
                required: true,
                default_value: "Moderate detail"
            });
        } else {
            questions.push({
                id: "visual_style",
                question: "Would you like more visual elements (charts, diagrams) or text-based content?",
                field_type: "select",
                options: ["More visuals", "Balanced", "More text", "Minimal design"],
                required: true,
                default_value: "Balanced"
            });
        }

        // Return up to 5 questions
        return questions.slice(0, 5);
    }

    /**
     * Generate slide count range around AI recommendation for dropdown
     * @param {number} recommendedSlides - AI recommended slide count
     * @returns {Array} Array of slide count options
     */
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

    /**
     * Detect if conversation has multiple distinct topics
     * @param {Array} conversationHistory - Array of conversation messages
     * @returns {boolean} True if multiple topics detected
     */
    detectMultipleTopics(conversationHistory) {
        if (!conversationHistory[0] || !conversationHistory[0].conversation) return false;
        return conversationHistory[0].conversation.length > 1;
    }

    /**
     * Extract main topics from conversation
     * @param {Array} conversationHistory - Array of conversation messages
     * @returns {Array} Array of topic strings
     */
    extractTopics(conversationHistory) {
        if (!conversationHistory[0] || !conversationHistory[0].conversation) return ["General Topic"];
        
        return conversationHistory[0].conversation.map((conv, index) => {
            // Extract key terms from questions for topic identification
            const question = conv.question.toLowerCase();
            if (question.includes('history')) return 'Historical Context';
            if (question.includes('company') || question.includes('business')) return 'Business Applications';
            if (question.includes('workplace') || question.includes('work')) return 'Workplace Integration';
            if (question.includes('technology') || question.includes('tech')) return 'Technology Overview';
            return `Topic ${index + 1}`;
        });
    }

    /**
     * Detect if content is business-focused
     * @param {string} content - Conversation content
     * @returns {boolean} True if business content detected
     */
    isBusinessContent(content) {
        const businessKeywords = ['business', 'company', 'strategy', 'market', 'revenue', 'profit', 'management', 'enterprise'];
        const lowerContent = content.toLowerCase();
        return businessKeywords.some(keyword => lowerContent.includes(keyword));
    }

    /**
     * Detect if content is technical-focused
     * @param {string} content - Conversation content
     * @returns {boolean} True if technical content detected
     */
    isTechnicalContent(content) {
        const technicalKeywords = ['technology', 'technical', 'implementation', 'system', 'software', 'hardware', 'algorithm', 'programming'];
        const lowerContent = content.toLowerCase();
        return technicalKeywords.some(keyword => lowerContent.includes(keyword));
    }

    /**
     * Calculate recommended slide count based on content analysis
     * @param {string} content - Conversation content
     * @param {boolean} hasMultipleTopics - Whether multiple topics detected
     * @returns {number} Recommended slide count
     */
    calculateRecommendedSlides(content, hasMultipleTopics) {
        // Base slide calculation
        let recommendedSlides = 8; // Base minimum

        // Factor 1: Content length
        const contentLength = content.length;
        if (contentLength > 3000) {
            recommendedSlides += 6; // 14 slides for long content
        } else if (contentLength > 1500) {
            recommendedSlides += 4; // 12 slides for medium content
        } else {
            recommendedSlides += 2; // 10 slides for short content
        }

        // Factor 2: Multiple topics
        if (hasMultipleTopics) {
            recommendedSlides += 3; // Additional slides for topic coverage
        }

        // Factor 3: Content complexity
        const complexityWords = ['analysis', 'implementation', 'strategy', 'process', 'system', 'framework', 'methodology'];
        const complexityCount = complexityWords.filter(word => 
            content.toLowerCase().includes(word)
        ).length;
        
        if (complexityCount >= 3) {
            recommendedSlides += 2; // More slides for complex topics
        }

        // Factor 4: Business vs Technical content
        if (this.isBusinessContent(content)) {
            recommendedSlides += 1; // Business presentations often need more context
        }

        // Ensure within bounds
        return Math.max(8, Math.min(20, recommendedSlides)); // 8-20 range for recommendations
    }

    /**
     * Get explanation for slide recommendation
     * @param {string} content - Conversation content
     * @param {number} recommendedSlides - Recommended slide count
     * @returns {string} Explanation for the recommendation
     */
    getSlideRecommendationReason(content, recommendedSlides) {
        const contentLength = content.length;
        const reasons = [];

        if (contentLength > 3000) {
            reasons.push("extensive content coverage");
        } else if (contentLength > 1500) {
            reasons.push("moderate content depth");
        } else {
            reasons.push("focused content");
        }

        if (this.isBusinessContent(content)) {
            reasons.push("business context requirements");
        } else if (this.isTechnicalContent(content)) {
            reasons.push("technical detail needs");
        }

        const hasComplexity = ['analysis', 'implementation', 'strategy'].some(word => 
            content.toLowerCase().includes(word)
        );
        if (hasComplexity) {
            reasons.push("topic complexity");
        }

        return `Based on ${reasons.join(', ')}`;
    }
}

module.exports = { ConversationManager };