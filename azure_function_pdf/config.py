"""
Configuration module for PDF Processing Service - Simplified for extraction only
"""
import os
from dotenv import load_dotenv
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings

def load_environment():
    """Load environment variables from parent directory"""
    if os.environ.get("WEBSITE_SITE_NAME"):
        return  # Running in Azure
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    env_path = os.path.join(parent_dir, ".env")
    
    if os.path.exists(env_path):
        load_dotenv(env_path)

load_environment()

# ====================================================================
# SUPPORTED FORMATS - Simplified
# ====================================================================

SUPPORTED_INPUT_FORMATS = [
    "PDF documents (.pdf)",
    "Word documents (.docx)"
]

SUPPORTED_OUTPUT_FORMATS = [
    "PDF documents (.pdf)"  # Only PDF output now
]

# ====================================================================
# CONTENT CLASSIFICATION
# ====================================================================

CONTENT_TYPES = {
    "CV": "curriculum_vitae",
    "GENERAL": "general_document"
}

# ====================================================================
# CONSOLIDATED PIPELINE CONFIGURATION
# ====================================================================

MANDATORY_START_AGENTS = ["SmartIntentProcessor"]  # Consolidated routing agent
DOCUMENT_PROCESSORS = ["CVAnalysisSkill", "DocumentExtractionSkill", "MarkdownFormatterAgent"]
QUICK_RESPONSE_AGENTS = ["DocumentQuickSummarySkill"]

def get_complete_pipeline(selected_processor: str) -> list:
    """Get complete pipeline with consolidated routing - single AI call"""
    return ["SmartIntentProcessor", selected_processor, "MarkdownFormatterAgent"]

def get_quick_response_pipeline() -> list:
    """Get pipeline for quick information requests"""
    return ["SmartIntentProcessor", "DocumentQuickSummarySkill"]

# ====================================================================
# SIMPLIFIED AGENT CONFIGURATIONS
# ====================================================================

DEFAULT_AGENT_CONFIGS = {
    # CONSOLIDATED: Smart intent processor (replaces DocumentInputValidator + DocumentClassifierAgent)
    "SmartIntentProcessor": {
        "max_tokens": 5000,  # Increased for comprehensive analysis
        "temperature": 0.3,  # Balanced for analysis + creativity
        "top_p": 0.8
    },
    
    # Quick summary - Medium temperature for natural responses
    "DocumentQuickSummarySkill": {
        "max_tokens": 6000,
        "temperature": 0.4,
        "top_p": 0.9
    },
    
    # CV analysis - Medium temperature for natural language (includes focused future skills)
    "CVAnalysisSkill": {
        "max_tokens": 10000,  # Reduced from 8000
        "temperature": 0.5, 
        "top_p": 0.9
    },
    
    # Simple document extraction - Medium temperature for organization
    "DocumentExtractionSkill": {
        "max_tokens": 10000,  # Much reduced from 10000
        "temperature": 0.4, 
        "top_p": 0.9
    },
    
    # Simple markdown formatting - Low temperature for consistency
    "MarkdownFormatterAgent": {
        "max_tokens": 10000,  # Reduced from 8000
        "temperature": 0.3, 
        "top_p": 0.8
    }
}

# ====================================================================
# SESSION MANAGEMENT
# ====================================================================

SESSION_ID_PREFIX = "PDF"
SESSION_ID_DATE_FORMAT = "%d%m%Y"
SESSION_ID_UNIQUE_LENGTH = 8

# ====================================================================
# UTILITY FUNCTIONS
# ====================================================================

def get_agent_config(agent_class_name: str) -> dict:
    """Get configuration for specific agent class"""
    return DEFAULT_AGENT_CONFIGS.get(agent_class_name, DEFAULT_AGENT_CONFIGS["DocumentExtractionSkill"]).copy()

def apply_config_overrides(agent_class_name: str, **overrides) -> dict:
    """Get agent config with optional parameter overrides"""
    config = get_agent_config(agent_class_name)
    config.update(overrides)
    return config

def get_ai_service(max_tokens=800, temperature=1.0, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
    """Get Azure OpenAI service and execution settings"""
    env_endpoint = os.getenv("ENDPOINT_URL")
    env_deployment = os.getenv("DEPLOYMENT_NAME")
    env_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    env_api_version = os.getenv("API_VERSION")
    
    if not env_api_key:
        raise ValueError("Please set your AZURE_OPENAI_API_KEY in the .env file")
    
    service = AzureChatCompletion(
        deployment_name=env_deployment,
        endpoint=env_endpoint,
        api_key=env_api_key,
        api_version=env_api_version
    )
    
    execution_settings = OpenAIChatPromptExecutionSettings(
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stream=False
    )
    
    return service, execution_settings
