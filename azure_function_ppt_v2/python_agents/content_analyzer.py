"""
Simplified Content Analysis Agent for PowerPoint Generation v2
Single-purpose agent focused on document analysis and slide planning
"""
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

# Semantic Kernel imports
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelFunction
from semantic_kernel.prompt_template import PromptTemplateConfig, InputVariable

from config import AI_CONFIG, ANALYSIS_CONFIG, get_analysis_prompt, validate_ai_config

class ContentAnalysisAgent:
    """Simplified content analysis agent for PowerPoint generation"""
    
    def __init__(self):
        """Initialize the content analysis agent"""
        self.kernel = None
        self.chat_service = None
        self.analysis_function = None
        self._setup_kernel()
    
    def _setup_kernel(self):
        """Setup Semantic Kernel with Azure OpenAI"""
        try:
            # Validate configuration
            validate_ai_config()
            
            # Create kernel
            self.kernel = Kernel()
            
            # Setup Azure OpenAI service
            self.chat_service = AzureChatCompletion(
                deployment_name=AI_CONFIG["deployment_name"],
                endpoint=AI_CONFIG["endpoint"],
                api_key=AI_CONFIG["api_key"],
                api_version=AI_CONFIG["api_version"]
            )
            
            # Add service to kernel
            self.kernel.add_service(self.chat_service)
            
            # Create analysis function
            self._create_analysis_function()
            
            logging.info("ContentAnalysisAgent initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to setup ContentAnalysisAgent: {str(e)}")
            raise
    
    def _create_analysis_function(self):
        """Create the content analysis function"""
        try:
            # Create prompt template
            prompt_template = get_analysis_prompt("content_analysis", 
                                                document_content="{{$document_content}}", 
                                                user_input="{{$user_input}}")
            
            # Create prompt template config
            prompt_config = PromptTemplateConfig(
                template=prompt_template,
                name="content_analysis",
                description="Analyze document content for PowerPoint generation",
                input_variables=[
                    InputVariable(name="document_content", description="The document content to analyze"),
                    InputVariable(name="user_input", description="User's request or instructions")
                ]
            )
            
            # Create execution settings
            execution_settings = OpenAIChatPromptExecutionSettings(
                max_tokens=AI_CONFIG["max_tokens"],
                temperature=AI_CONFIG["temperature"],
                top_p=AI_CONFIG["top_p"]
            )
            
            # Create kernel function
            self.analysis_function = KernelFunction.from_prompt(
                prompt_template_config=prompt_config,
                execution_settings=execution_settings
            )
            
            logging.info("Analysis function created successfully")
            
        except Exception as e:
            logging.error(f"Failed to create analysis function: {str(e)}")
            raise
    
    async def analyze_content(self, document_content: str, user_input: str = "") -> Dict[str, Any]:
        """
        Analyze document content for PowerPoint generation
        
        Args:
            document_content: The document content to analyze
            user_input: User's specific request or instructions
            
        Returns:
            Dict containing analysis results with slide structure
        """
        try:
            logging.info(f"Starting content analysis - Content length: {len(document_content)} chars")
            
            # Validate inputs
            if not document_content or len(document_content.strip()) < 100:
                return self._create_fallback_analysis(document_content, user_input)
            
            # Truncate content if too long
            if len(document_content) > ANALYSIS_CONFIG["max_content_length"]:
                document_content = document_content[:ANALYSIS_CONFIG["max_content_length"]] + "... [truncated]"
                logging.warning(f"Content truncated to {ANALYSIS_CONFIG['max_content_length']} characters")
            
            # Prepare arguments
            user_input = user_input or "Create a professional presentation from this document"
            
            # Execute analysis
            result = await self.kernel.invoke(
                self.analysis_function,
                document_content=document_content,
                user_input=user_input
            )
            
            # Parse result
            analysis_text = str(result).strip()
            logging.info(f"Raw analysis result length: {len(analysis_text)} chars")
            
            # Clean and parse JSON
            analysis_data = self._parse_analysis_result(analysis_text)
            
            # Validate and enhance analysis
            validated_analysis = self._validate_and_enhance_analysis(analysis_data, document_content)
            
            logging.info(f"Content analysis completed - {validated_analysis.get('slideCount', 0)} slides planned")
            return validated_analysis
            
        except Exception as e:
            logging.error(f"Content analysis failed: {str(e)}")
            return self._create_fallback_analysis(document_content, user_input, str(e))
    
    def _parse_analysis_result(self, analysis_text: str) -> Dict[str, Any]:
        """Parse and clean analysis result JSON"""
        try:
            # Remove common markdown formatting
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                # Try to extract content between any code blocks
                parts = analysis_text.split('```')
                if len(parts) >= 3:
                    analysis_text = parts[1]
            
            # Clean up the text
            analysis_text = analysis_text.strip()
            
            # Parse JSON
            analysis_data = json.loads(analysis_text)
            
            logging.info("Successfully parsed analysis JSON")
            return analysis_data
            
        except json.JSONDecodeError as e:
            logging.warning(f"JSON parsing failed: {str(e)}")
            logging.warning(f"Raw text (first 500 chars): {analysis_text[:500]}")
            
            # Try to extract JSON-like content with regex
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            raise Exception("Failed to parse analysis result as JSON")
    
    def _validate_and_enhance_analysis(self, analysis_data: Dict[str, Any], document_content: str) -> Dict[str, Any]:
        """Validate and enhance the analysis results"""
        try:
            # Ensure required fields exist
            analysis_data.setdefault("slideCount", ANALYSIS_CONFIG["default_slides"])
            analysis_data.setdefault("presentationTitle", "Business Presentation")
            analysis_data.setdefault("contentSummary", "Analysis of business document")
            analysis_data.setdefault("keyTopics", ["Overview", "Analysis", "Recommendations"])
            analysis_data.setdefault("slides", [])
            
            # Validate slide count
            slide_count = analysis_data["slideCount"]
            if slide_count < ANALYSIS_CONFIG["min_slides"]:
                analysis_data["slideCount"] = ANALYSIS_CONFIG["min_slides"]
            elif slide_count > ANALYSIS_CONFIG["max_slides"]:
                analysis_data["slideCount"] = ANALYSIS_CONFIG["max_slides"]
            
            # Ensure we have slides array
            if not analysis_data["slides"] or len(analysis_data["slides"]) == 0:
                analysis_data["slides"] = self._create_default_slides(analysis_data)
            
            # Validate slide structure
            validated_slides = []
            for slide in analysis_data["slides"]:
                validated_slide = self._validate_slide(slide)
                validated_slides.append(validated_slide)
            
            analysis_data["slides"] = validated_slides[:analysis_data["slideCount"]]
            
            # Add metadata
            analysis_data.setdefault("analysisMetadata", {})
            analysis_data["analysisMetadata"].update({
                "contentLength": len(document_content),
                "processingMethod": "ai_analysis",
                "confidence": 0.8,  # Default confidence
                "processedAt": datetime.utcnow().isoformat(),
                "agentVersion": "v2.0.0"
            })
            
            logging.info("Analysis validation and enhancement completed")
            return analysis_data
            
        except Exception as e:
            logging.error(f"Analysis validation failed: {str(e)}")
            raise
    
    def _validate_slide(self, slide: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual slide structure"""
        validated_slide = {
            "type": slide.get("type", "CONTENT_SLIDE"),
            "title": slide.get("title", "Slide Title"),
            "content": slide.get("content", [])
        }
        
        # Ensure content is a list
        if not isinstance(validated_slide["content"], list):
            if isinstance(validated_slide["content"], str):
                validated_slide["content"] = [validated_slide["content"]]
            else:
                validated_slide["content"] = []
        
        # Limit content to reasonable number of points
        validated_slide["content"] = validated_slide["content"][:6]
        
        # Add subtitle for title slide
        if validated_slide["type"] == "TITLE_SLIDE" and "subtitle" in slide:
            validated_slide["subtitle"] = slide["subtitle"]
        
        return validated_slide
    
    def _create_default_slides(self, analysis_data: Dict[str, Any]) -> list:
        """Create default slide structure when AI analysis fails"""
        slides = []
        slide_count = analysis_data.get("slideCount", ANALYSIS_CONFIG["default_slides"])
        key_topics = analysis_data.get("keyTopics", ["Overview", "Analysis", "Findings", "Recommendations"])
        
        # Title slide
        slides.append({
            "type": "TITLE_SLIDE",
            "title": analysis_data.get("presentationTitle", "Business Presentation"),
            "subtitle": "Document Analysis and Insights",
            "content": []
        })
        
        # Agenda slide
        slides.append({
            "type": "AGENDA_SLIDE",
            "title": "Agenda",
            "content": key_topics[:5]
        })
        
        # Content slides
        content_slide_count = slide_count - 4  # Exclude title, agenda, summary, thank you
        for i in range(max(1, content_slide_count)):
            topic_index = i % len(key_topics)
            slides.append({
                "type": "CONTENT_SLIDE",
                "title": key_topics[topic_index] if topic_index < len(key_topics) else f"Analysis Point {i + 1}",
                "content": [
                    "Key insights from document analysis",
                    "Important findings and observations", 
                    "Strategic implications",
                    "Actionable recommendations"
                ]
            })
        
        # Summary slide
        slides.append({
            "type": "SUMMARY_SLIDE",
            "title": "Key Takeaways",
            "content": [
                "Primary insights from analysis",
                "Critical findings and recommendations",
                "Strategic next steps",
                "Value-driven outcomes"
            ]
        })
        
        # Thank you slide
        slides.append({
            "type": "THANK_YOU_SLIDE",
            "title": "Thank You",
            "content": []
        })
        
        return slides[:slide_count]
    
    def _create_fallback_analysis(self, document_content: str, user_input: str, error_message: str = "") -> Dict[str, Any]:
        """Create fallback analysis when AI processing fails"""
        logging.warning("Creating fallback analysis due to processing failure")
        
        # Basic content analysis
        content_length = len(document_content) if document_content else 0
        word_count = len(document_content.split()) if document_content else 0
        
        # Determine slide count based on content length
        if content_length < 1000:
            slide_count = 8
        elif content_length < 3000:
            slide_count = 12
        else:
            slide_count = 16
        
        slide_count = min(slide_count, ANALYSIS_CONFIG["max_slides"])
        
        fallback_analysis = {
            "slideCount": slide_count,
            "presentationTitle": "Business Document Analysis",
            "contentSummary": f"Analysis of document content ({word_count} words)",
            "keyTopics": ["Overview", "Key Points", "Analysis", "Findings", "Recommendations"],
            "slides": self._create_default_slides({"slideCount": slide_count}),
            "analysisMetadata": {
                "contentLength": content_length,
                "processingMethod": "fallback",
                "confidence": 0.6,
                "processedAt": datetime.utcnow().isoformat(),
                "agentVersion": "v2.0.0",
                "fallbackReason": error_message or "AI analysis unavailable"
            }
        }
        
        return fallback_analysis

# Standalone function for API usage
async def analyze_document_content(document_content: str, user_input: str = "") -> Dict[str, Any]:
    """
    Standalone function to analyze document content
    """
    try:
        agent = ContentAnalysisAgent()
        return await agent.analyze_content(document_content, user_input)
    except Exception as e:
        logging.error(f"Document analysis failed: {str(e)}")
        # Return fallback analysis
        agent = ContentAnalysisAgent()
        return agent._create_fallback_analysis(document_content, user_input, str(e))

# For testing purposes
if __name__ == "__main__":
    async def test_analysis():
        test_content = """
        This is a sample business document for testing the content analysis system.
        
        The document contains multiple sections including an overview of the business situation,
        detailed analysis of market conditions, financial projections, and strategic recommendations.
        
        Key findings include:
        - Market opportunity worth $10M annually
        - Competitive advantage in technology sector
        - Required investment of $2M over 18 months
        - Projected ROI of 150% within 3 years
        
        The recommendations focus on immediate market entry, strategic partnerships,
        and aggressive marketing campaigns to capture market share.
        """
        
        result = await analyze_document_content(test_content, "Create a professional presentation")
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_analysis())