// Load environment variables from parent directory .env file (same as Python services)
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../../.env') });

/**
 * Configuration module for PowerPoint Generation Service v2
 * Using PptxGenJS for enhanced PowerPoint capabilities
 */

// ====================================================================
// ENVIRONMENT CONFIGURATION
// ====================================================================

const loadEnvironment = () => {
    // Check if running in Azure
    if (process.env.WEBSITE_SITE_NAME) {
        console.log('Running in Azure - using Function App environment variables');
        return; // Running in Azure, use environment variables directly
    }
    
    // For local development, load from parent directory .env file (same as Python services)
    console.log('Running locally - loading from root .env file');
    
    const requiredEnvVars = ['ENDPOINT_URL', 'DEPLOYMENT_NAME', 'AZURE_OPENAI_API_KEY', 'API_VERSION'];
    
    for (const envVar of requiredEnvVars) {
        if (!process.env[envVar]) {
            console.error(`Missing required environment variable: ${envVar}`);
            console.error('Make sure the root .env file (document-generation-v1.1/.env) has all required values');
            throw new Error(`Missing required environment variable: ${envVar}`);
        }
    }
    
    console.log('Environment variables loaded successfully from root .env file');
};

// ====================================================================
// SUPPORTED FORMATS
// ====================================================================

const SUPPORTED_INPUT_FORMATS = [
    "Conversation history (JSON)",
    "Chat session data"
];

const SUPPORTED_OUTPUT_FORMATS = [
    "Consolidated presentation requirements (JSON)"
];

// ====================================================================
// PRESENTATION CONFIGURATION
// ====================================================================

const PRESENTATION_CONFIG = {
    max_slides: 60,        // Maximum allowed slides (hard limit)
    min_slides: 3,         // Minimum slides for proper presentation structure
    default_slides: 12,    // Default target when content complexity is medium
    use_case: "Conversational presentation planning and requirements gathering"
};


// ====================================================================
// AGENT PIPELINE CONFIGURATION
// ====================================================================

const AGENT_PIPELINE = [
    "ConversationManager",                 // Handle conversation flow and context
    "ClarificationQuestionGenerator"       // Estimate slide count and generate questions
];

const QUICK_RESPONSE_PIPELINE = [
    "ConversationManager",                 // Handle conversation only
    "ClarificationQuestionGenerator"       // Provide slide count estimate and questions
];

// ====================================================================
// AGENT CONFIGURATIONS
// ====================================================================

const AGENT_CONFIGS = {
    ConversationManager: {
        max_tokens: 20000,
        temperature: 0.3,
        purpose: "Manage conversation flow, understand user intent, and maintain context"
    },
    
    ClarificationQuestionGenerator: {
        max_tokens: 8000,
        temperature: 0.4,
        purpose: "Analyze content complexity, estimate optimal slide count, and generate contextual clarification questions"
    }
};

// ====================================================================
// SESSION MANAGEMENT
// ====================================================================

const SESSION_CONFIG = {
    id_prefix: "PPTV2",
    date_format: "DDMMYYYY",
    unique_length: 8,
    max_conversation_history: 20,
    session_timeout_minutes: 60
};

// ====================================================================
// LOCAL DEVELOPMENT CONFIGURATION
// ====================================================================

const LOCAL_DEV_CONFIG = {
    port: 7076,
    host: 'localhost',
    api_path: '/api/powerpointGeneration'
};

const getLocalUrl = () => `http://${LOCAL_DEV_CONFIG.host}:${LOCAL_DEV_CONFIG.port}`;
const getApiUrl = () => `${getLocalUrl()}${LOCAL_DEV_CONFIG.api_path}`;

// ====================================================================
// PRESENTATION FORMATTING CONFIGURATION (for third-party services)
// ====================================================================

const PRESENTATION_FORMAT_CONFIG = {
    supported_formats: ["bullet_points", "tables"],
    default_layout: "16:9",
    recommended_styling: {
        fonts: {
            title: "Calibri, 32pt, Bold",
            content: "Calibri, 16pt, Regular",
            table_headers: "Calibri, 14pt, Bold",
            table_content: "Calibri, 12pt, Regular"
        },
        colors: {
            primary: "#584dc1",    // Purple
            accent: "#d1b95b",     // Gold
            text: "#333333",       // Dark gray
            background: "#ffffff"   // White
        }
    }
};

// ====================================================================
// UTILITY FUNCTIONS
// ====================================================================

const getAgentConfig = (agentName) => {
    return AGENT_CONFIGS[agentName] || AGENT_CONFIGS.ConversationManager;
};

const generateSessionId = () => {
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '');
    const randomStr = Math.random().toString(36).substring(2, 2 + SESSION_CONFIG.unique_length).toUpperCase();
    return `${SESSION_CONFIG.id_prefix}${dateStr}${randomStr}`;
};

const getOpenAIConfig = () => {
    return {
        endpoint: process.env.ENDPOINT_URL,
        deployment: process.env.DEPLOYMENT_NAME,
        apiKey: process.env.AZURE_OPENAI_API_KEY,
        apiVersion: process.env.API_VERSION
    };
};

// Initialize environment on module load
loadEnvironment();

module.exports = {
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    PRESENTATION_CONFIG,
    PRESENTATION_FORMAT_CONFIG,
    AGENT_PIPELINE,
    QUICK_RESPONSE_PIPELINE,
    AGENT_CONFIGS,
    SESSION_CONFIG,
    LOCAL_DEV_CONFIG,
    getAgentConfig,
    generateSessionId,
    getOpenAIConfig,
    getLocalUrl,
    getApiUrl
};