"""
Configuration module for Python Content Analysis Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_environment_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(load_environment_path):
    load_dotenv(load_environment_path)

# Azure OpenAI Configuration
AI_CONFIG = {
    "endpoint": os.getenv("ENDPOINT_URL"),
    "deployment_name": os.getenv("DEPLOYMENT_NAME"), 
    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
    "api_version": os.getenv("API_VERSION"),
    "max_tokens": 8000,
    "temperature": 0.5,
    "top_p": 0.9
}

# Content Analysis Configuration
ANALYSIS_CONFIG = {
    "min_slides": 5,
    "max_slides": 25,
    "default_slides": 12,
    "max_content_length": 10000,
    "min_section_length": 100,
    "key_points_limit": 20
}

# Slide Type Mapping
SLIDE_TYPES = {
    "title": "TITLE_SLIDE",
    "agenda": "AGENDA_SLIDE", 
    "content": "CONTENT_SLIDE",
    "table": "TABLE_SLIDE",
    "chart": "CHART_SLIDE",
    "two_column": "TWO_COLUMN",
    "summary": "SUMMARY_SLIDE",
    "thank_you": "THANK_YOU_SLIDE"
}

# Content Analysis Prompts
ANALYSIS_PROMPTS = {
    "content_analysis": """
You are a professional business analyst specializing in document analysis for presentation creation.

Analyze the following document content and provide a structured analysis for PowerPoint generation:

DOCUMENT CONTENT:
{document_content}

USER REQUEST: {user_input}

Provide your analysis in the following JSON format:

{{
    "slideCount": <optimal_number_between_5_and_25>,
    "presentationTitle": "<professional_title>",
    "contentSummary": "<3_sentence_summary>",
    "keyTopics": ["<topic1>", "<topic2>", "<topic3>", "<topic4>"],
    "slides": [
        {{
            "type": "TITLE_SLIDE",
            "title": "<presentation_title>",
            "subtitle": "<subtitle_or_context>",
            "content": []
        }},
        {{
            "type": "AGENDA_SLIDE", 
            "title": "Agenda",
            "content": ["<agenda_item_1>", "<agenda_item_2>", "<agenda_item_3>"]
        }},
        {{
            "type": "CONTENT_SLIDE",
            "title": "<slide_title>",
            "content": ["<bullet_point_1>", "<bullet_point_2>", "<bullet_point_3>"]
        }},
        // ... more slides based on content analysis
        {{
            "type": "SUMMARY_SLIDE",
            "title": "Key Takeaways", 
            "content": ["<takeaway_1>", "<takeaway_2>", "<takeaway_3>"]
        }},
        {{
            "type": "THANK_YOU_SLIDE",
            "title": "Thank You",
            "content": []
        }}
    ],
    "analysisMetadata": {{
        "contentLength": <character_count>,
        "processingMethod": "ai_analysis",
        "confidence": <confidence_score_0_to_1>,
        "suggestedDuration": "<presentation_duration_minutes>"
    }}
}}

Guidelines:
1. Create {max_slides} slides maximum
2. Focus on business value and actionable insights
3. Use professional language appropriate for corporate presentations
4. Ensure each slide has 3-6 bullet points maximum
5. Create logical flow from overview to conclusions
6. Identify opportunities for tables/charts when data is present
7. Make titles descriptive and engaging
8. Ensure content is concise and presentation-ready

Return only the JSON response, no additional text.
""",

    "quick_analysis": """
Quickly analyze this document content for presentation structure:

CONTENT: {document_content}

Provide a brief JSON analysis focusing on:
1. Main topics (3-5)
2. Optimal slide count (8-15)  
3. Key insights (5-8 bullet points)
4. Suggested presentation title

Format as minimal JSON with slideCount, title, keyTopics, and keyInsights fields.
"""
}

def get_analysis_prompt(analysis_type="content_analysis", **kwargs):
    """Get analysis prompt with parameters"""
    prompt_template = ANALYSIS_PROMPTS.get(analysis_type, ANALYSIS_PROMPTS["content_analysis"])
    
    # Set default values
    kwargs.setdefault("max_slides", ANALYSIS_CONFIG["max_slides"])
    kwargs.setdefault("min_slides", ANALYSIS_CONFIG["min_slides"])
    
    return prompt_template.format(**kwargs)

def validate_ai_config():
    """Validate AI configuration"""
    required_fields = ["endpoint", "deployment_name", "api_key", "api_version"]
    missing_fields = [field for field in required_fields if not AI_CONFIG.get(field)]
    
    if missing_fields:
        raise ValueError(f"Missing required AI configuration: {', '.join(missing_fields)}")
    
    return True