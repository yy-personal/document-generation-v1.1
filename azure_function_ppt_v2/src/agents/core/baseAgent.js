const { OpenAI } = require('openai');
const { getOpenAIConfig, getAgentConfig } = require('../../config/config');

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

            
            const response = await this.openai.chat.completions.create(params);
            
            const result = {
                content: response.choices[0].message.content,
                usage: response.usage,
                model: response.model
            };

            
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
            // Strategy 1: Direct parse
            return JSON.parse(content);
        } catch (error) {
            // Strategy 2: Clean markdown and common formatting issues
            try {
                let cleanContent = content
                    .replace(/```json\n?|\n?```/g, '')  // Remove code blocks
                    .replace(/^[#*\-\s]*.*?\n/gm, '')   // Remove markdown headers/bullets
                    .replace(/^\s*[\w\s]*:\s*$/gm, '')  // Remove section headers
                    .trim();
                
                // Find JSON object boundaries
                const jsonStart = cleanContent.indexOf('{');
                const jsonEnd = cleanContent.lastIndexOf('}');
                
                if (jsonStart !== -1 && jsonEnd !== -1 && jsonEnd > jsonStart) {
                    cleanContent = cleanContent.substring(jsonStart, jsonEnd + 1);
                }
                
                return JSON.parse(cleanContent);
            } catch (secondError) {
                // Strategy 3: Extract JSON from mixed content
                try {
                    const jsonMatch = content.match(/\{[\s\S]*\}/);
                    if (jsonMatch) {
                        return JSON.parse(jsonMatch[0]);
                    }
                } catch (thirdError) {
                    // Final fallback - log and throw
                    console.error(`[${this.agentName}] All JSON parsing strategies failed:`);
                    console.error('Original content:', content.substring(0, 500));
                    throw new Error(`Invalid JSON response from ${this.agentName}: ${error.message}`);
                }
            }
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
        // Look for [document_start] and [document_end] tags
        const documentMatch = userMessage.match(/\[document_start\](.*?)\[document_end\]/s);
        
        if (documentMatch) {
            const documentContent = documentMatch[1].trim();
            const userText = userMessage
                .replace(/\[document_start\].*?\[document_end\]/s, '')
                .trim();
            
            return {
                has_document: true,
                document_content: documentContent,
                user_text: userText
            };
        }

        // Fallback: Look for legacy [document] tags for backward compatibility
        const legacyDocumentMatch = userMessage.match(/\[document\](.+)/s);
        
        if (legacyDocumentMatch) {
            return {
                has_document: true,
                document_content: legacyDocumentMatch[1].trim(),
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