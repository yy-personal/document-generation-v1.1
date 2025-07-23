"""
Configuration module for PowerPoint Generation Service
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
# SUPPORTED FORMATS
# ====================================================================

SUPPORTED_INPUT_FORMATS = [
    "PDF documents (.pdf)",
    "Word documents (.docx)",
    "Multiple documents (batch processing)"
]

SUPPORTED_OUTPUT_FORMATS = [
    "PowerPoint presentations (.pptx)"
]

# ====================================================================
# PRESENTATION CONFIGURATION
# ====================================================================

# Standard presentation settings
PRESENTATION_CONFIG = {
    "default_slides": 12,
    "max_slides": 15,
    "min_slides": 8,
    "use_case": "Standard business presentations for all content types"
}

# ====================================================================
# SLIDE LAYOUTS
# ====================================================================

SLIDE_LAYOUTS = {
    "TITLE_SLIDE": "Company logo, title, subtitle, presenter info",
    "AGENDA_SLIDE": "Overview of presentation topics (3-8 items)",
    "CONTENT_SLIDE": "Standard content with title and bullet points",
    "TWO_COLUMN_SLIDE": "Comparative content, before/after, pros/cons",
    "SUMMARY_SLIDE": "Key takeaways and conclusions (3-6 points)",
    "THANK_YOU_SLIDE": "Contact information and next steps"
}

# ====================================================================
# COMPANY BRANDING
# ====================================================================

COMPANY_DESIGN_STANDARDS = {
    "color_scheme": {
        "primary": "#1F4E79",      # Company blue
        "secondary": "#70AD47",    # Company green  
        "accent": "#C55A11",       # Company orange
        "text_dark": "#2F2F2F",
        "text_light": "#FFFFFF"
    },
    "fonts": {
        "title": ("Calibri", 32, True),     # (font, size, bold)
        "subtitle": ("Calibri", 24, False),
        "body": ("Calibri Light", 18, False),
        "footer": ("Calibri", 12, False)
    },
    "branding": {
        "logo_position": "top_right",
        "logo_size": (1.5, 0.5),   # inches
        "footer_template": "Company Name | Confidential"
    }
}

# ====================================================================
# PIPELINE CONFIGURATION
# ====================================================================

MANDATORY_START_AGENTS = ["SmartPresentationProcessor"]
CONTENT_PROCESSORS = [
    "DocumentContentExtractor", 
    "PresentationStructureAgent", 
    "SlideContentGenerator"
]
FILE_GENERATOR = ["PowerPointBuilderAgent"]

def get_complete_pipeline() -> list:
    """Get complete PowerPoint generation pipeline (4 AI calls + 1 rule-based)"""
    return [
        "SmartPresentationProcessor",
        "DocumentContentExtractor", 
        "PresentationStructureAgent",
        "SlideContentGenerator",
        "PowerPointBuilderAgent"
    ]

def get_quick_response_pipeline() -> list:
    """Get pipeline for information requests about presentation capabilities"""
    return ["SmartPresentationProcessor"]

# ====================================================================
# AGENT CONFIGURATIONS
# ====================================================================

DEFAULT_AGENT_CONFIGS = {
    # Intent analysis + slide count optimization
    "SmartPresentationProcessor": {
        "max_tokens": 4000,
        "temperature": 0.3,    # Structured analysis
        "top_p": 0.8
    },
    
    # Content organization and extraction
    "DocumentContentExtractor": {
        "max_tokens": 8000,
        "temperature": 0.4,    # Balanced organization
        "top_p": 0.9
    },
    
    # Slide planning and structure
    "PresentationStructureAgent": {
        "max_tokens": 6000,
        "temperature": 0.5,    # Creative structure
        "top_p": 0.9
    },
    
    # Content creation and formatting
    "SlideContentGenerator": {
        "max_tokens": 10000,
        "temperature": 0.6,    # Creative content
        "top_p": 0.9
    },
    
    # File generation (rule-based, minimal AI)
    "PowerPointBuilderAgent": {
        "max_tokens": 4000,
        "temperature": 0.2,    # Consistent formatting
        "top_p": 0.8
    }
}

# ====================================================================
# SESSION MANAGEMENT
# ====================================================================

SESSION_ID_PREFIX = "PPT"
SESSION_ID_DATE_FORMAT = "%d%m%Y"
SESSION_ID_UNIQUE_LENGTH = 8

# ====================================================================
# UTILITY FUNCTIONS
# ====================================================================

def get_agent_config(agent_class_name: str) -> dict:
    """Get configuration for specific agent class"""
    return DEFAULT_AGENT_CONFIGS.get(agent_class_name, DEFAULT_AGENT_CONFIGS["DocumentContentExtractor"]).copy()

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
