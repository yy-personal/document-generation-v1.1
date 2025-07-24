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

# Slide count settings - CENTRALIZED CONTROL
PRESENTATION_CONFIG = {
    "max_slides": 30,        # MAXIMUM allowed slides (hard limit)
    "min_slides": 3,         # MINIMUM slides for basic presentation structure
    "use_case": "Flexible business presentations - agents determine optimal slide count based on content"
}

# ====================================================================
# SLIDE LAYOUTS  
# ====================================================================

SLIDE_LAYOUTS = {
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
    "THANK_YOU_SLIDE": "Contact information and next steps"
}

# ====================================================================
# PRESENTATION OUTLINE STRUCTURE
# ====================================================================

# Standard presentation outline that should be followed whenever possible
STANDARD_OUTLINE = [
    {"type": "TITLE_SLIDE", "title": "Title", "required": True},
    {"type": "AGENDA_SLIDE", "title": "Agenda", "required": True},
    {"type": "OVERVIEW_SLIDE", "title": "Overview", "required": True},
    {"type": "ANALYSIS_SLIDE", "title": "Analysis", "required": False, "repeatable": True},
    {"type": "OBJECTIVES_SLIDE", "title": "Objectives", "required": False, "repeatable": True},
    {"type": "RECOMMENDATIONS_SLIDE", "title": "Recommendations", "required": True},
    {"type": "SUMMARY_SLIDE", "title": "Summary", "required": True},
    {"type": "THANK_YOU_SLIDE", "title": "Thank You", "required": True}
]

def get_outline_structure(available_slides: int) -> list:
    """
    Generate flexible presentation outline based on available slides.
    This is used as a fallback structure - agents can create their own optimal structure.
    """
    # Ensure we respect the minimum slide count
    min_slides = PRESENTATION_CONFIG["min_slides"]
    available_slides = max(available_slides, min_slides)
    
    if available_slides < 6:
        # Minimal outline for very short presentations
        return [
            {"type": "TITLE_SLIDE", "title": "Title"},
            {"type": "OVERVIEW_SLIDE", "title": "Overview"},
            {"type": "ANALYSIS_SLIDE", "title": "Analysis"},
            {"type": "RECOMMENDATIONS_SLIDE", "title": "Recommendations"},
            {"type": "THANK_YOU_SLIDE", "title": "Thank You"}
        ][:available_slides]
    
    # Standard structure with flexible content slots
    required_slides = 5  # Title, Agenda, Overview, Recommendations, Thank You
    content_slots = max(1, available_slides - required_slides)
    
    outline = [
        {"type": "TITLE_SLIDE", "title": "Title"},
        {"type": "AGENDA_SLIDE", "title": "Agenda"},
        {"type": "OVERVIEW_SLIDE", "title": "Overview"}
    ]
    
    # Add flexible content slides (Analysis, Objectives, Process, Results)
    content_types = ["ANALYSIS_SLIDE", "OBJECTIVES_SLIDE", "PROCESS_SLIDE", "RESULTS_SLIDE"]
    for i in range(content_slots):
        slide_type = content_types[i % len(content_types)]
        slide_title = slide_type.replace("_SLIDE", "").title()
        outline.append({"type": slide_type, "title": slide_title})
    
    outline.extend([
        {"type": "RECOMMENDATIONS_SLIDE", "title": "Recommendations"},
        {"type": "THANK_YOU_SLIDE", "title": "Thank You"}
    ])
    
    return outline

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
    """Get complete PowerPoint generation pipeline"""
    return [
        "SmartPresentationProcessor",
        "DocumentContentExtractor", 
        "PresentationStructureAgent",
        "SlideContentGenerator",
        "PowerPointBuilderAgent"
    ]

def get_quick_response_pipeline() -> list:
    """Get pipeline for information requests"""
    return ["SmartPresentationProcessor"]

# ====================================================================
# AGENT CONFIGURATIONS
# ====================================================================

DEFAULT_AGENT_CONFIGS = {
    # Intent analysis only
    "SmartPresentationProcessor": {
        "max_tokens": 3000,     # Reduced - no slide count logic
        "temperature": 0.3,
        "top_p": 0.8
    },
    
    # Content organization only
    "DocumentContentExtractor": {
        "max_tokens": 8000,
        "temperature": 0.4,
        "top_p": 0.9
    },
    
    # Content analysis + slide planning + structure
    "PresentationStructureAgent": {
        "max_tokens": 8000,     # Increased - handles slide count logic
        "temperature": 0.5,
        "top_p": 0.9
    },
    
    # Content creation and formatting
    "SlideContentGenerator": {
        "max_tokens": 16000,    # Increased for handling 15+ slides
        "temperature": 0.6,
        "top_p": 0.9
    },
    
    # File generation (rule-based)
    "PowerPointBuilderAgent": {
        "max_tokens": 10000,
        "temperature": 0.2,
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
# TEMPLATE CONFIGURATION
# ====================================================================

TEMPLATE_CONFIG = {
    "use_templates": False,  # Set to False to disable all custom templates
    "default_template": "templates/default_template.pptx",
    "company_template": "templates/company_template.pptx", 
    "executive_template": "templates/executive_template.pptx",
    "technical_template": "templates/technical_template.pptx",
    "fallback_template": None  # Use python-pptx default if templates fail
}

# Template selection based on presentation type or content
TEMPLATE_MAPPING = {
    "executive": "company_template",
    "technical": "technical_template", 
    "general": "default_template",
    "default": "default_template"
}

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

def get_max_slides() -> int:
    """Get maximum allowed slides"""
    return PRESENTATION_CONFIG["max_slides"]

def get_template_path(template_type: str = "default") -> str:
    """Get template file path based on presentation type"""
    import os
    
    # Check if templates are enabled
    if not TEMPLATE_CONFIG.get("use_templates", True):
        print("Templates disabled in config - using python-pptx default")
        return None
    
    # Get template name from mapping
    template_name = TEMPLATE_MAPPING.get(template_type, "default_template")
    template_path = TEMPLATE_CONFIG.get(template_name)
    
    if template_path and os.path.exists(template_path):
        return template_path
    
    # Try fallback template
    fallback = TEMPLATE_CONFIG.get("fallback_template")
    if fallback and os.path.exists(fallback):
        return fallback
    
    # Return None to use python-pptx default
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