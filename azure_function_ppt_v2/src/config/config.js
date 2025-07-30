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
    "PDF documents (.pdf)",
    "Word documents (.docx)",
    "Text with document content"
];

const SUPPORTED_OUTPUT_FORMATS = [
    "PowerPoint presentations (.pptx)"
];

// ====================================================================
// PRESENTATION CONFIGURATION
// ====================================================================

const PRESENTATION_CONFIG = {
    max_slides: 60,        // Maximum allowed slides (hard limit)
    min_slides: 3,         // Minimum slides for proper presentation structure
    default_slides: 12,    // Default target when content complexity is medium
    use_case: "Conversational business presentations with PptxGenJS"
};

// ====================================================================
// SLIDE LAYOUTS AND CONTENT TYPES
// ====================================================================

const SLIDE_LAYOUTS = {
    TITLE_SLIDE: "Title slide with company branding",
    AGENDA_SLIDE: "Agenda overview with bullet points",
    OVERVIEW_SLIDE: "High-level overview and context",
    CONTENT_SLIDE: "Standard content with title and bullets",
    TWO_COLUMN_SLIDE: "Two-column layout for side-by-side content",
    TABLE_SLIDE: "Data presented in table format",
    ANALYSIS_SLIDE: "Analysis findings and insights",
    RECOMMENDATIONS_SLIDE: "Recommendations and action items",
    SUMMARY_SLIDE: "Key takeaways and conclusions",
    THANK_YOU_SLIDE: "Contact information and next steps"
};

const CONTENT_TYPES = {
    BULLET_POINTS: "bullet_points",
    TABLE_DATA: "table_data",
    TWO_COLUMN: "two_column",
    IMAGE_PLACEHOLDER: "image_placeholder",
    CHART_PLACEHOLDER: "chart_placeholder"
};

// ====================================================================
// AGENT PIPELINE CONFIGURATION
// ====================================================================

const AGENT_PIPELINE = [
    "ConversationManager",                 // Handle conversation flow and context
    "DocumentProcessor",                   // Extract and organize document content
    "ClarificationQuestionGenerator",      // Estimate slide count and generate questions
    "ContentStructurer",                   // Structure content for slides
    "PptxGenerator"                        // Generate PowerPoint using PptxGenJS
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
    
    DocumentProcessor: {
        max_tokens: 8000,
        temperature: 0.4,
        purpose: "Extract and organize content from documents for presentation structure"
    },
    
    ClarificationQuestionGenerator: {
        max_tokens: 8000,
        temperature: 0.4,
        purpose: "Analyze content complexity, estimate optimal slide count, and generate contextual clarification questions"
    },
    
    ContentStructurer: {
        max_tokens: 12000,
        temperature: 0.5,
        purpose: "Structure content into slides with appropriate layouts and formatting"
    },
    
    PptxGenerator: {
        max_tokens: 10000,
        temperature: 0.2,
        purpose: "Generate PptxGenJS code for creating PowerPoint files"
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
// PPTXGENJS CONFIGURATION
// ====================================================================

const PPTX_CONFIG = {
    layout: "LAYOUT_16x9",     // Use 16:9 aspect ratio
    theme: {
        primary_color: "584dc1",    // Purple
        accent_color: "d1b95b",     // Gold
        text_color: "333333",       // Dark gray
        background_color: "ffffff"   // White
    },
    fonts: {
        title: { face: "Calibri", size: 32, bold: true },
        subtitle: { face: "Calibri", size: 18, bold: false },
        content: { face: "Calibri", size: 16, bold: false },
        small: { face: "Calibri", size: 12, bold: false }
    },
    margins: {
        top: 0.5,
        bottom: 0.5,
        left: 0.5,
        right: 0.5
    }
};

// ====================================================================
// UTILITY FUNCTIONS
// ====================================================================

const getAgentConfig = (agentName) => {
    return AGENT_CONFIGS[agentName] || AGENT_CONFIGS.DocumentProcessor;
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
    SLIDE_LAYOUTS,
    CONTENT_TYPES,
    AGENT_PIPELINE,
    QUICK_RESPONSE_PIPELINE,
    AGENT_CONFIGS,
    SESSION_CONFIG,
    LOCAL_DEV_CONFIG,
    PPTX_CONFIG,
    getAgentConfig,
    generateSessionId,
    getOpenAIConfig,
    getLocalUrl,
    getApiUrl
};