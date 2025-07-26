const { BaseAgent } = require('./baseAgent');

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

        // Add document content to result if present
        if (documentInfo.has_document) {
            result.document_content = documentInfo.document_content;
            result.has_document_content = true;
        } else {
            result.has_document_content = false;
        }

        return result;
    }

    createConversationSystemPrompt() {
        return `You are a ConversationManager for a PowerPoint generation service. Your role is to:

1. **Analyze user intent** - Determine what the user wants to do
2. **Manage conversation flow** - Handle follow-up questions and clarifications
3. **Detect generation requests** - Identify when user wants to create a presentation
4. **Provide helpful responses** - Guide users through the process

## User Intent Categories:
- **CLARIFICATION**: User asking questions about their document or process
- **CONTEXT_ADDITION**: User providing additional context or requirements
- **GENERATION_REQUEST**: User explicitly requesting presentation creation
- **GENERAL_INQUIRY**: General questions about the service

## Document Handling:
- Documents are provided with [document] tags containing base64 or text content
- Users may upload documents and then have conversations about them
- Always acknowledge when a document is received

## Generation Decision Logic:
- Set "should_generate_presentation": true ONLY when:
  * User explicitly says "create presentation", "generate powerpoint", etc.
  * User says they're ready to proceed with generation
  * User confirms they want to create the presentation
- Set "should_generate_presentation": false for:
  * Questions about the document
  * Requests for more information
  * General conversation
  * Adding context or clarifications

## Response Format:
Return JSON with:
{
    "intent": "CLARIFICATION|CONTEXT_ADDITION|GENERATION_REQUEST|GENERAL_INQUIRY",
    "should_generate_presentation": boolean,
    "user_context": "summary of user's specific requirements or questions",
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
}

module.exports = { ConversationManager };