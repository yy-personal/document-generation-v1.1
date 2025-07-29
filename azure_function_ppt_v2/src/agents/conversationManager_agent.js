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
- **GENERATION_REQUEST**: User explicitly requesting presentation creation
- **GENERAL_INQUIRY**: General questions about the service
- **CONTENT_BUILDING**: User providing topic details for presentation

## Content Sources:
- **Documents**: Provided with [document_start] and [document_end] tags containing base64 or text content
- **Conversation Content**: Topics, details, and requirements provided through conversation
- **Mixed Approach**: Combination of documents and conversational context
- **Document-Free**: Presentations built entirely from conversation content

## Generation Decision Logic:
- Set "should_generate_presentation": true ONLY when:
  * User explicitly says "create presentation", "generate powerpoint", etc.
  * User says they're ready to proceed with generation
  * User confirms they want to create the presentation
  * Sufficient content is available (either from document OR conversation)
- Set "should_generate_presentation": false for:
  * Questions about the document/topic
  * Requests for more information
  * General conversation
  * Adding context or clarifications
  * Insufficient content for presentation

## Content Extraction:
When no document is provided, extract presentation content from:
- User-specified topics and subtopics
- Details provided in conversation
- Requirements and preferences mentioned
- Previous conversation context

## Response Format:
Return JSON with:
{
    "intent": "CLARIFICATION|CONTEXT_ADDITION|GENERATION_REQUEST|GENERAL_INQUIRY|CONTENT_BUILDING",
    "should_generate_presentation": boolean,
    "user_context": "summary of user's specific requirements or questions",
    "conversation_content": "extracted content for presentation (when no document)",
    "content_source": "document|conversation|mixed",
    "response_text": "your response to the user",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of your decision"
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
            
            // Include last few messages for context
            const recentHistory = conversation_history.slice(-6);
            recentHistory.forEach((msg, index) => {
                prompt += `\n${msg.role}: ${msg.content}`;
            });
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
}

module.exports = { ConversationManager };