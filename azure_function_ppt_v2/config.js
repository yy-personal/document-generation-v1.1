/**
 * Configuration module for PowerPoint Generation Service v2
 */
require('dotenv').config();

// Load environment variables from parent directory like the original
function loadEnvironment() {
    if (process.env.WEBSITE_SITE_NAME) {
        return; // Running in Azure
    }
    
    const path = require('path');
    const fs = require('fs');
    const currentDir = __dirname;
    const parentDir = path.dirname(currentDir);
    const envPath = path.join(parentDir, '.env');
    
    if (fs.existsSync(envPath)) {
        require('dotenv').config({ path: envPath });
    }
}

loadEnvironment();

// ====================================================================
// SUPPORTED FORMATS
// ====================================================================

const SUPPORTED_INPUT_FORMATS = [
    "PDF documents (.pdf)",
    "Word documents (.docx)",
    "Multiple documents (batch processing)"
];

const SUPPORTED_OUTPUT_FORMATS = [
    "PowerPoint presentations (.pptx)"
];

// ====================================================================
// PRESENTATION CONFIGURATION
// ====================================================================

// Slide count settings - CENTRALIZED CONTROL (matching original)
const PRESENTATION_CONFIG = {
    max_slides: 30,        // MAXIMUM allowed slides (hard limit)
    min_slides: 3,         // MINIMUM slides for basic presentation structure
    use_case: "Flexible business presentations - agents determine optimal slide count based on content"
};

// ====================================================================
// SLIDE LAYOUTS (matching original structure)
// ====================================================================

const SLIDE_LAYOUTS = {
    "TITLE_SLIDE": "Company logo, title, subtitle, presenter info",
    "AGENDA_SLIDE": "Overview of presentation topics (3-8 items)",
    "OVERVIEW_SLIDE": "High-level overview and context setting",
    "CONTENT_SLIDE": "Standard content with title and bullet points",
    "ANALYSIS_SLIDE": "Analysis, findings, and observations",
    "OBJECTIVES_SLIDE": "Goals, objectives, and targets",
    "PROCESS_SLIDE": "Steps, workflow, and methodology",
    "RESULTS_SLIDE": "Outcomes, results, and achievements",
    "RECOMMENDATIONS_SLIDE": "Recommendations and action items",
    "NEXT_STEPS_SLIDE": "Next steps and follow-up actions",
    "SUMMARY_SLIDE": "Key takeaways and conclusions (3-6 points)",
    "THANK_YOU_SLIDE": "Contact information and next steps",
    // New layout types for enhanced presentations
    "TABLE_SLIDE": "Data presented in table format with clean formatting",
    "COMPARISON_SLIDE": "Side-by-side comparison layout",
    "TWO_COLUMN_SLIDE": "Two-column layout for organized content"
};

// ====================================================================
// PRESENTATION OUTLINE STRUCTURE (matching original)
// ====================================================================

// Standard presentation outline that should be followed whenever possible
const STANDARD_OUTLINE = [
    {"type": "TITLE_SLIDE", "title": "Title", "required": true},
    {"type": "AGENDA_SLIDE", "title": "Agenda", "required": true},
    {"type": "OVERVIEW_SLIDE", "title": "Overview", "required": true},
    {"type": "ANALYSIS_SLIDE", "title": "Analysis", "required": false, "repeatable": true},
    {"type": "OBJECTIVES_SLIDE", "title": "Objectives", "required": false, "repeatable": true},
    {"type": "RECOMMENDATIONS_SLIDE", "title": "Recommendations", "required": true},
    {"type": "SUMMARY_SLIDE", "title": "Summary", "required": true},
    {"type": "THANK_YOU_SLIDE", "title": "Thank You", "required": true}
];

function getOutlineStructure(availableSlides) {
    /**
     * Generate flexible presentation outline based on available slides.
     * This is used as a fallback structure - agents can create their own optimal structure.
     */
    // Ensure we respect the minimum slide count
    const minSlides = PRESENTATION_CONFIG.min_slides;
    availableSlides = Math.max(availableSlides, minSlides);
    
    if (availableSlides < 6) {
        // Minimal outline for very short presentations
        return [
            {"type": "TITLE_SLIDE", "title": "Title"},
            {"type": "OVERVIEW_SLIDE", "title": "Overview"},
            {"type": "ANALYSIS_SLIDE", "title": "Analysis"},
            {"type": "RECOMMENDATIONS_SLIDE", "title": "Recommendations"},
            {"type": "THANK_YOU_SLIDE", "title": "Thank You"}
        ].slice(0, availableSlides);
    }
    
    // Standard structure with flexible content slots
    const requiredSlides = 5; // Title, Agenda, Overview, Recommendations, Thank You
    const contentSlots = Math.max(1, availableSlides - requiredSlides);
    
    const outline = [
        {"type": "TITLE_SLIDE", "title": "Title"},
        {"type": "AGENDA_SLIDE", "title": "Agenda"},
        {"type": "OVERVIEW_SLIDE", "title": "Overview"}
    ];
    
    // Add flexible content slides (Analysis, Objectives, Process, Results)
    const contentTypes = ["ANALYSIS_SLIDE", "OBJECTIVES_SLIDE", "PROCESS_SLIDE", "RESULTS_SLIDE"];
    for (let i = 0; i < contentSlots; i++) {
        const slideType = contentTypes[i % contentTypes.length];
        const slideTitle = slideType.replace("_SLIDE", "").charAt(0).toUpperCase() + 
                          slideType.replace("_SLIDE", "").slice(1).toLowerCase();
        outline.push({"type": slideType, "title": slideTitle});
    }
    
    outline.push(
        {"type": "RECOMMENDATIONS_SLIDE", "title": "Recommendations"},
        {"type": "THANK_YOU_SLIDE", "title": "Thank You"}
    );
    
    return outline;
}

// ====================================================================
// SESSION MANAGEMENT (matching original)
// ====================================================================

const SESSION_CONFIG = {
    idPrefix: 'PPT',
    dateFormat: '%d%m%Y',
    uniqueLength: 8
};

// Corporate Branding Colors
const BRAND_COLORS = {
    primary: '584DC1',      // NCS Purple
    secondary: 'D1B95B',    // NCS Gold
    accent: '2E8B57',       // Sea Green
    text: '333333',         // Dark Gray
    background: 'FFFFFF',   // White
    lightGray: 'F5F5F5'     // Light Gray
};

// ====================================================================
// AGENT CONFIGURATIONS (matching original structure)
// ====================================================================

const DEFAULT_AGENT_CONFIGS = {
    // Intent analysis only
    "SmartPresentationProcessor": {
        "max_tokens": 3000,     // Reduced - no slide count logic
        "temperature": 0.3,
        "top_p": 0.8
    },
    
    // Content organization only
    "DocumentContentExtractor": {
        "max_tokens": 8000,
        "temperature": 0.4,
        "top_p": 0.9
    },
    
    // Content analysis + slide planning + structure
    "PresentationStructureAgent": {
        "max_tokens": 8000,     // Increased - handles slide count logic
        "temperature": 0.5,
        "top_p": 0.9
    },
    
    // Content creation and formatting
    "SlideContentGenerator": {
        "max_tokens": 16000,    // Increased for handling 15+ slides
        "temperature": 0.6,
        "top_p": 0.9
    },
    
    // File generation (rule-based)
    "PowerPointBuilderAgent": {
        "max_tokens": 10000,
        "temperature": 0.2,
        "top_p": 0.8
    }
};

// ====================================================================
// UTILITY FUNCTIONS (matching original structure and behavior)
// ====================================================================

function getAgentConfig(agentClassName) {
    /**Get configuration for specific agent class*/
    return DEFAULT_AGENT_CONFIGS[agentClassName] || DEFAULT_AGENT_CONFIGS["DocumentContentExtractor"];
}

function applyConfigOverrides(agentClassName, overrides = {}) {
    /**Get agent config with optional parameter overrides*/
    const config = { ...getAgentConfig(agentClassName) };
    Object.assign(config, overrides);
    return config;
}

function getMaxSlides() {
    /**Get maximum allowed slides*/
    return PRESENTATION_CONFIG.max_slides;
}

function generateSessionId() {
    /**Generate unique session ID matching original format*/
    const date = new Date();
    const dateStr = String(date.getDate()).padStart(2, '0') + 
                   String(date.getMonth() + 1).padStart(2, '0') + 
                   date.getFullYear();
    const unique = Math.random().toString(36).substr(2, SESSION_CONFIG.uniqueLength).toUpperCase();
    return `${SESSION_CONFIG.idPrefix}${dateStr}${unique}`;
}

function getOptimalSlideCount(contentLength) {
    if (contentLength < 1000) return 8;
    if (contentLength < 3000) return 12;
    if (contentLength < 5000) return 16;
    return Math.min(20, PRESENTATION_CONFIG.max_slides);
}

function getAiService(maxTokens = 800, temperature = 1.0, topP = 1.0, frequencyPenalty = 0.0, presencePenalty = 0.0) {
    /**Get Azure OpenAI service and execution settings - Node.js equivalent*/
    const envEndpoint = process.env.ENDPOINT_URL;
    const envDeployment = process.env.DEPLOYMENT_NAME;
    const envApiKey = process.env.AZURE_OPENAI_API_KEY;
    const envApiVersion = process.env.API_VERSION;
    
    if (!envApiKey) {
        throw new Error("Please set your AZURE_OPENAI_API_KEY in the .env file");
    }
    
    return {
        endpoint: envEndpoint,
        deploymentName: envDeployment,
        apiKey: envApiKey,
        apiVersion: envApiVersion,
        executionSettings: {
            max_tokens: maxTokens,
            temperature: temperature,
            top_p: topP,
            frequency_penalty: frequencyPenalty,
            presence_penalty: presencePenalty,
            stream: false
        }
    };
}

module.exports = {
    // Constants (matching original exports)
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    PRESENTATION_CONFIG,
    SLIDE_LAYOUTS,
    STANDARD_OUTLINE,
    DEFAULT_AGENT_CONFIGS,
    SESSION_CONFIG,
    BRAND_COLORS,
    
    // Utility functions (matching original)
    getOutlineStructure,
    getAgentConfig,
    applyConfigOverrides,
    getMaxSlides,
    generateSessionId,
    getOptimalSlideCount,
    getAiService
};