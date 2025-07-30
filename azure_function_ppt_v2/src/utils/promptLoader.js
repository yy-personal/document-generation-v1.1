const fs = require('fs');
const path = require('path');
const { PRESENTATION_CONFIG } = require('../config/config');

/**
 * Centralized prompt management system
 * Loads system prompts from txt files in the prompts directory
 */
class PromptLoader {
    constructor() {
        this.promptsDir = path.join(__dirname, '..', 'prompts');
        this.promptCache = new Map();
    }

    /**
     * Load a prompt from file with optional variable replacement
     * @param {string} promptName - Name of the prompt file (without .txt extension)
     * @param {Object} variables - Optional variables to replace in the prompt
     * @returns {string} The loaded and processed prompt
     */
    loadPrompt(promptName, variables = {}) {
        // Check cache first
        const cacheKey = `${promptName}_${JSON.stringify(variables)}`;
        if (this.promptCache.has(cacheKey)) {
            return this.promptCache.get(cacheKey);
        }

        try {
            const promptPath = path.join(this.promptsDir, `${promptName}.txt`);
            let promptContent = fs.readFileSync(promptPath, 'utf-8');

            // Replace standard configuration variables
            promptContent = this.replaceConfigVariables(promptContent);

            // Replace custom variables if provided
            if (variables && Object.keys(variables).length > 0) {
                promptContent = this.replaceCustomVariables(promptContent, variables);
            }

            // Cache the result
            this.promptCache.set(cacheKey, promptContent);
            
            return promptContent;

        } catch (error) {
            console.error(`Failed to load prompt '${promptName}':`, error);
            throw new Error(`Prompt loading failed for '${promptName}': ${error.message}`);
        }
    }

    /**
     * Replace standard configuration variables in prompts
     * @param {string} promptContent - The prompt content
     * @returns {string} Content with config variables replaced
     */
    replaceConfigVariables(promptContent) {
        return promptContent
            .replace(/{MIN_SLIDES}/g, PRESENTATION_CONFIG.min_slides)
            .replace(/{MAX_SLIDES}/g, PRESENTATION_CONFIG.max_slides)
            .replace(/{DEFAULT_SLIDES}/g, PRESENTATION_CONFIG.default_slides);
    }

    /**
     * Replace custom variables in prompts
     * @param {string} promptContent - The prompt content
     * @param {Object} variables - Variables to replace
     * @returns {string} Content with custom variables replaced
     */
    replaceCustomVariables(promptContent, variables) {
        let result = promptContent;
        
        for (const [key, value] of Object.entries(variables)) {
            const regex = new RegExp(`{${key}}`, 'g');
            result = result.replace(regex, String(value));
        }
        
        return result;
    }

    /**
     * Clear the prompt cache (useful for development/testing)
     */
    clearCache() {
        this.promptCache.clear();
    }

    /**
     * Get list of available prompts
     * @returns {Array<string>} Array of available prompt names
     */
    getAvailablePrompts() {
        try {
            const files = fs.readdirSync(this.promptsDir);
            return files
                .filter(file => file.endsWith('.txt'))
                .map(file => file.replace('.txt', ''));
        } catch (error) {
            console.error('Failed to list available prompts:', error);
            return [];
        }
    }

    /**
     * Validate that a prompt file exists
     * @param {string} promptName - Name of the prompt to validate
     * @returns {boolean} True if prompt exists
     */
    validatePrompt(promptName) {
        const promptPath = path.join(this.promptsDir, `${promptName}.txt`);
        return fs.existsSync(promptPath);
    }
}

// Create singleton instance
const promptLoader = new PromptLoader();

module.exports = { PromptLoader, promptLoader };