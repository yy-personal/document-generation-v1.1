const { BaseAgent } = require('./core/baseAgent');
const { PRESENTATION_CONFIG } = require('../config/config');
const { promptLoader } = require('../utils/promptLoader');

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

        const { user_message, session_id, conversation_history = [], entra_id, clarification_answers } = input;

        // Special: Consolidate info trigger
        if (user_message && user_message.trim().startsWith('[consolidate_info]')) {
            // Load consolidation system prompt from file
            const systemPrompt = promptLoader.loadPrompt('consolidation_system');

            // Build user prompt
            let userPrompt = `## Conversation History:\n`;
            if (Array.isArray(conversation_history) && conversation_history.length > 0 && conversation_history[0].conversation) {
                conversation_history[0].conversation.forEach((conv, idx) => {
                    userPrompt += `Q${idx + 1}: ${conv.question}\nA${idx + 1}: ${conv.response}\n`;
                });
            } else {
                conversation_history.forEach((msg, idx) => {
                    if (msg.role === 'user') userPrompt += `Q${idx + 1}: ${msg.content}\n`;
                    if (msg.role === 'assistant') userPrompt += `A${idx + 1}: ${msg.content}\n`;
                });
            }
            userPrompt += `\n## Clarified Presentation Preferences:\n`;
            if (clarification_answers && typeof clarification_answers === 'object') {
                Object.entries(clarification_answers).forEach(([key, value]) => {
                    userPrompt += `- ${key}: ${value}\n`;
                });
            }

            userPrompt += `\n## Task:\nWrite a single, well-structured summary that combines the above into a clear set of presentation requirements.`;

            const messages = [
                this.createSystemMessage(systemPrompt),
                this.createUserMessage(userPrompt)
            ];

            const aiResponse = await this.callAI(messages);
            // Return as { consolidated_summary: ... }
            return { consolidated_summary: aiResponse.content };
        }

        // Check for exact bracket triggers first
        const bracketTrigger = this.detectBracketTriggers(user_message);
        
        if (bracketTrigger) {
            return this.handleBracketTrigger(bracketTrigger, input);
        }

        // Extract document content if present
        const documentInfo = this.extractDocumentContent(user_message);

        // Load system prompt from centralized prompt management
        const systemPrompt = promptLoader.loadPrompt('conversation_manager_system');

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
            const rawJsonString = answersMatch[1];
            const answers = this.parseAnswersWithTolerance(rawJsonString);
            
            if (answers) {
                return {
                    type: 'clarification_answers',
                    stage: 2,
                    answers: answers
                };
            } else {
                console.error('Failed to parse clarification answers after all attempts');
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
     * Parse clarification answers with error tolerance and automatic repair
     * @param {string} rawJsonString - Raw JSON string from user message
     * @returns {object|null} Parsed answers object or null if parsing fails
     */
    parseAnswersWithTolerance(rawJsonString) {
        // Strategy 1: Try direct parsing first
        try {
            const answers = JSON.parse(rawJsonString);
            return answers;
        } catch (error) {
        }

        // Strategy 2: Clean and repair common JSON issues
        let cleanedJson = rawJsonString.trim();
        
        // Remove leading/trailing whitespace and quotes
        if ((cleanedJson.startsWith('"') && cleanedJson.endsWith('"')) || 
            (cleanedJson.startsWith("'") && cleanedJson.endsWith("'"))) {
            cleanedJson = cleanedJson.slice(1, -1);
        }

        // Fix common issues:
        // 1. Extra closing braces/commas at the end
        cleanedJson = cleanedJson.replace(/[,}]+$/, '');
        
        // 2. Ensure proper closing brace
        if (!cleanedJson.endsWith('}')) {
            cleanedJson += '}';
        }

        // 3. Fix unescaped quotes in values (basic attempt)
        cleanedJson = cleanedJson.replace(/: "([^"]*)"([^,}]*)"([^,}]*)/g, ': "$1\\"$2\\"$3');

        try {
            const answers = JSON.parse(cleanedJson);
            return answers;
        } catch (error) {
        }

        // Strategy 3: Extract key-value pairs using regex (last resort)
        try {
            const answers = {};
            
            // Extract key-value pairs using regex
            const keyValuePattern = /"([^"]+)":\s*("([^"]*)"|(true|false|\d+))/g;
            let match;
            
            while ((match = keyValuePattern.exec(rawJsonString)) !== null) {
                const key = match[1];
                let value = match[3] || match[4]; // String value or boolean/number
                
                // Convert boolean and number strings
                if (value === 'true') value = true;
                else if (value === 'false') value = false;
                else if (/^\d+$/.test(value)) value = parseInt(value);
                
                answers[key] = value;
            }
            
            if (Object.keys(answers).length > 0) {
                return answers;
            }
        } catch (error) {
        }

        console.error('[ConversationManager] All parsing strategies failed for:', rawJsonString);
        return null;
    }

    /**
     * Parse AI response content with error handling
     * @param {string} content - Raw AI response content
     * @returns {Object} Parsed response object
     */
    parseAIResponse(content) {
        try {
            // Try to parse as JSON first
            const parsed = JSON.parse(content);
            return parsed;
        } catch (error) {
            console.warn('[ConversationManager] Failed to parse AI response as JSON:', error.message);
            
            // Fallback: Try to extract JSON from markdown code blocks
            const jsonMatch = content.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
            if (jsonMatch) {
                try {
                    const parsed = JSON.parse(jsonMatch[1]);
                    return parsed;
                } catch (codeBlockError) {
                    console.warn('[ConversationManager] Failed to parse JSON from code block:', codeBlockError.message);
                }
            }
            
            // Fallback 2: Try to extract response_text from malformed JSON
            let extractedResponseText = "I understand your message. Please let me know if you'd like to create a presentation.";
            const responseTextMatch = content.match(/"response_text":\s*"([^"]*(?:\\.[^"]*)*)"/);
            if (responseTextMatch) {
                extractedResponseText = responseTextMatch[1].replace(/\\n/g, '\n').replace(/\\"/g, '"');
            }
            
            // Ultimate fallback: Return a clean default structure
            console.warn('[ConversationManager] Using fallback response structure');
            return {
                should_generate_presentation: false,
                show_slide_recommendation: false,
                show_clarification_questions: false,
                need_slide_estimation: false,
                clarification_answers: null,
                has_document_content: false,
                conversation_content: "User provided conversation history about stock market topics",
                user_context: "User is building content for potential presentation",
                content_source: 'conversation',
                response_text: extractedResponseText,
                error_info: {
                    original_error: error.message,
                    parsing_fallback_used: true,
                    fallback_strategy: 'clean_default'
                }
            };
        }
    }

}

module.exports = { ConversationManager };
