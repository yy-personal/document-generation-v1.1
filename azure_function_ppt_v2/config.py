"""
Configuration module for PowerPoint Generation Service V2
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
# V2 SYSTEM CONFIGURATION
# ====================================================================

SYSTEM_VERSION = "V2_Pandoc_Markdown"
SYSTEM_DESCRIPTION = "PowerPoint generation using Pandoc + Markdown approach for better consistency"

# ====================================================================
# SUPPORTED FORMATS
# ====================================================================

SUPPORTED_INPUT_FORMATS = [
    "PDF documents (.pdf)",
    "Word documents (.docx)",
    "Conversational document processing"
]

SUPPORTED_OUTPUT_FORMATS = [
    "PowerPoint presentations (.pptx) via Pandoc conversion"
]

# ====================================================================
# PRESENTATION CONFIGURATION
# ====================================================================

# V2 presentation configuration - agent-driven slide count determination
PRESENTATION_CONFIG = {
    "max_slides": 15,           # Maximum slides to prevent overwhelming presentations (hard limit)
    "use_case": "Business presentations via Pandoc markdown conversion - agents determine optimal slide count"
}

# ====================================================================
# MARKDOWN GENERATION SETTINGS
# ====================================================================

MARKDOWN_CONFIG = {
    "slide_level": 2,           # Level 2 headers (##) create new slides
    "enable_tables": True,      # Support for markdown tables
    "enable_columns": True,     # Support for two-column layouts
    "yaml_metadata": True,      # Include YAML front matter
    "preserve_formatting": True # Preserve line breaks and formatting
}

# ====================================================================
# PANDOC CONFIGURATION
# ====================================================================

PANDOC_CONFIG = {
    "timeout_seconds": 60,      # Conversion timeout
    "slide_level": 2,           # Maps to --slide-level=2
    "wrap": "preserve",         # Maps to --wrap=preserve
    "enable_debug": True,       # Save debug copies of generated files
    "template_path": "templates/company_template.pptx"
}

# ====================================================================
# AGENT CONFIGURATIONS
# ====================================================================

# Simplified agent configuration for V2
V2_AGENT_CONFIGS = {
    # Markdown generation agent
    "MarkdownPresentationAgent": {
        "max_tokens": 12000,    # Increased for longer markdown generation
        "temperature": 0.4,     # Lower temperature for more consistent output
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }
}

# ====================================================================
# SESSION MANAGEMENT
# ====================================================================

SESSION_ID_PREFIX = "PPT_V2"
SESSION_ID_DATE_FORMAT = "%d%m%Y"
SESSION_ID_UNIQUE_LENGTH = 8

# ====================================================================
# TEMPLATE CONFIGURATION
# ====================================================================

TEMPLATE_CONFIG = {
    "use_custom_template": True,        # Enable custom template usage
    "template_path": "templates/company_template.pptx",
    "fallback_to_default": True,        # Use Pandoc default if template fails
    "validate_template": True           # Validate template exists before use
}

# ====================================================================
# UTILITY FUNCTIONS
# ====================================================================

def get_agent_config(agent_class_name: str) -> dict:
    """Get configuration for specific agent class"""
    return V2_AGENT_CONFIGS.get(agent_class_name, V2_AGENT_CONFIGS["MarkdownPresentationAgent"]).copy()

def apply_config_overrides(agent_class_name: str, **overrides) -> dict:
    """Get agent config with optional parameter overrides"""
    config = get_agent_config(agent_class_name)
    config.update(overrides)
    return config

def get_max_slides() -> int:
    """Get maximum allowed slides"""
    return PRESENTATION_CONFIG["max_slides"]

def get_template_path() -> str:
    """Get template file path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, TEMPLATE_CONFIG["template_path"])
    
    if TEMPLATE_CONFIG["use_custom_template"] and os.path.exists(template_path):
        return template_path
    
    # Return None to use Pandoc default
    return None

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

def get_system_info() -> dict:
    """Get V2 system information"""
    return {
        "version": SYSTEM_VERSION,
        "description": SYSTEM_DESCRIPTION,
        "supported_inputs": SUPPORTED_INPUT_FORMATS,
        "supported_outputs": SUPPORTED_OUTPUT_FORMATS,
        "max_slides": get_max_slides(),
        "agent_driven_slides": True,
        "template_enabled": TEMPLATE_CONFIG["use_custom_template"],
        "pandoc_timeout": PANDOC_CONFIG["timeout_seconds"]
    }