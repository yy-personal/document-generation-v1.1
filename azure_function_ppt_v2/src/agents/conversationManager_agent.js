const { BaseAgent } = require('./core/baseAgent');

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

        console.log('[ConversationManager] Processing user_message:', JSON.stringify(user_message));

        // Check for exact bracket triggers first
        const bracketTrigger = this.detectBracketTriggers(user_message);
        console.log('[ConversationManager] Bracket trigger detected:', bracketTrigger);
        
        if (bracketTrigger) {
            console.log('[ConversationManager] Using bracket trigger handler');
            return this.handleBracketTrigger(bracketTrigger, input);
        }

        console.log('[ConversationManager] No bracket trigger found, proceeding with AI processing');

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
            // Stage 1: Generate clarification questions for popup
            const clarificationQuestions = this.generateClarificationQuestions(conversation_history);
            
            return {
                intent: "PRESENTATION_INITIATE",
                should_generate_presentation: false,
                show_clarification_questions: true,
                clarification_questions: clarificationQuestions,
                user_context: "User clicked Create Presentation button",
                conversation_content: this.extractConversationContent(conversation_history),
                content_source: "conversation",
                response_text: "Please answer these questions to customize your presentation:",
                confidence: 1.0,
                reasoning: "Frontend create presentation button triggered - showing clarification questions",
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
     * @returns {Array} Array of question objects with field types
     */
    generateClarificationQuestions(conversationHistory) {
        // Analyze conversation to determine relevant questions
        const conversationContent = this.extractConversationContent(conversationHistory);
        const hasMultipleTopics = this.detectMultipleTopics(conversationHistory);
        const topics = this.extractTopics(conversationHistory);

        const questions = [];

        // Question 1: Slide count (always included)
        questions.push({
            id: "slide_count",
            question: "How many slides would you like in your presentation?",
            field_type: "number",
            placeholder: "12",
            required: true,
            default_value: 12,
            validation: { min: 5, max: 50 }
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
}

module.exports = { ConversationManager };