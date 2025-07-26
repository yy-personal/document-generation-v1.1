const { OpenAI } = require('openai');
const { getOpenAIConfig, getAgentConfig } = require('../config/config');

/**
 * Base Agent class for all PowerPoint generation agents
 * Provides common functionality for AI service interaction
 */
class BaseAgent {
    constructor(agentName) {
        this.agentName = agentName;
        this.config = getAgentConfig(agentName);
        
        // Initialize OpenAI client
        const openaiConfig = getOpenAIConfig();
        this.openai = new OpenAI({
            apiKey: openaiConfig.apiKey,
            baseURL: `${openaiConfig.endpoint}/openai/deployments/${openaiConfig.deployment}`,
            defaultQuery: { 'api-version': openaiConfig.apiVersion },
            defaultHeaders: {
                'api-key': openaiConfig.apiKey,
            }
        });
        
        console.log(`Initialized ${agentName} with config:`, {
            max_tokens: this.config.max_tokens,
            temperature: this.config.temperature,
            purpose: this.config.purpose
        });
    }

    /**
     * Make a call to the AI service with the given messages
     * @param {Array} messages - Array of message objects
     * @param {Object} overrides - Optional parameter overrides
     * @returns {Object} AI response
     */
    async callAI(messages, overrides = {}) {
        try {
            const params = {
                messages: messages,
                max_tokens: overrides.max_tokens || this.config.max_tokens,
                temperature: overrides.temperature || this.config.temperature,
                top_p: overrides.top_p || 1.0,
                frequency_penalty: overrides.frequency_penalty || 0.0,
                presence_penalty: overrides.presence_penalty || 0.0
            };

            console.log(`[${this.agentName}] Making AI call with ${messages.length} messages`);
            
            const response = await this.openai.chat.completions.create(params);
            
            const result = {
                content: response.choices[0].message.content,
                usage: response.usage,
                model: response.model
            };

            console.log(`[${this.agentName}] AI call completed. Tokens used: ${response.usage.total_tokens}`);
            
            return result;

        } catch (error) {
            console.error(`[${this.agentName}] AI call failed:`, error);
            throw new Error(`AI service call failed for ${this.agentName}: ${error.message}`);
        }
    }

    /**
     * Parse JSON response from AI, with error handling
     * @param {string} content - JSON string from AI
     * @returns {Object} Parsed JSON object
     */
    parseAIResponse(content) {
        try {
            // Remove any markdown code blocks if present
            const cleanContent = content.replace(/```json\n?|\n?```/g, '').trim();
            return JSON.parse(cleanContent);
        } catch (error) {
            console.error(`[${this.agentName}] Failed to parse AI response as JSON:`, content);
            throw new Error(`Invalid JSON response from ${this.agentName}: ${error.message}`);
        }
    }

    /**
     * Create system message for the agent
     * @param {string} systemPrompt - System prompt content
     * @returns {Object} System message object
     */
    createSystemMessage(systemPrompt) {
        return {
            role: 'system',
            content: systemPrompt
        };
    }

    /**
     * Create user message
     * @param {string} userContent - User message content
     * @returns {Object} User message object
     */
    createUserMessage(userContent) {
        return {
            role: 'user',
            content: userContent
        };
    }

    /**
     * Abstract method - must be implemented by subclasses
     * @param {Object} input - Input data for processing
     * @returns {Object} Processed result
     */
    async process(input) {
        throw new Error(`process() method must be implemented by ${this.agentName}`);
    }

    /**
     * Extract document content from various input formats
     * @param {string} userMessage - User message that may contain document tags
     * @returns {Object} Extracted document info
     */
    extractDocumentContent(userMessage) {
        // Look for [document] tags
        const documentMatch = userMessage.match(/\[document\](.+)/s);
        
        if (documentMatch) {
            return {
                has_document: true,
                document_content: documentMatch[1].trim(),
                user_text: userMessage.replace(/\[document\].+/s, '').trim()
            };
        }

        return {
            has_document: false,
            document_content: null,
            user_text: userMessage
        };
    }

    /**
     * Validate required input fields
     * @param {Object} input - Input object to validate
     * @param {Array} requiredFields - Array of required field names
     */
    validateInput(input, requiredFields) {
        for (const field of requiredFields) {
            if (!input[field]) {
                throw new Error(`Missing required field '${field}' for ${this.agentName}`);
            }
        }
    }
}

module.exports = { BaseAgent };