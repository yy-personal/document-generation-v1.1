"""
Presentation Structure Agent - Content analysis + slide planning + structure creation
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides, get_max_slides, PRESENTATION_CONFIG
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
import json

class PresentationStructureAgent(BaseAgent):
    """Analyzes content volume, determines optimal slides, and creates presentation structure"""

    agent_description = "Content analysis, slide count determination, and presentation structure creation"
    agent_use_cases = [
        "Content volume analysis",
        "Optimal slide count determination", 
        "Slide sequence planning",
        "Presentation structure creation"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = f"""
        You are a Presentation Structure Expert that analyzes content and creates optimal slide structures.

        YOUR RESPONSIBILITIES:
        1. **Content Volume Analysis**: Assess how much content needs to be presented
        2. **Slide Count Determination**: Calculate optimal slides based on content density
        3. **Structure Creation**: Design logical slide sequence and flow

        SLIDE COUNT GUIDELINES:
        - **Default**: {PRESENTATION_CONFIG['default_slides']} slides for standard content
        - **Minimum**: {PRESENTATION_CONFIG['min_slides']} slides (even for simple content)
        - **Maximum**: {PRESENTATION_CONFIG['max_slides']} slides (HARD LIMIT - never exceed)
        - **Content Density**: More complex content = more slides (up to max)

        SLIDE COUNT CALCULATION:
        - Light content (1-2 main topics): 8-10 slides
        - Medium content (3-5 main topics): 10-12 slides  
        - Heavy content (6+ main topics): 12-15 slides
        - Always respect the {PRESENTATION_CONFIG['max_slides']} slide maximum

        PRESENTATION STRUCTURE:
        - Slide 1: Title slide
        - Slides 2-N: Content slides (main topics)
        - Final slide: Summary/conclusion

        OUTPUT FORMAT (JSON only, no markdown):
        {{
            "content_analysis": {{
                "main_topics": ["topic1", "topic2", ...],
                "content_complexity": "light|medium|heavy",
                "estimated_duration": "10-15 minutes"
            }},
            "slide_planning": {{
                "optimal_slides": 12,
                "reasoning": "Content has X main topics requiring Y slides",
                "max_slides_enforced": {get_max_slides()}
            }},
            "presentation_structure": [
                {{
                    "slide_number": 1,
                    "slide_type": "TITLE_SLIDE",
                    "title": "Presentation Title",
                    "content_outline": ["Main title", "Subtitle"]
                }},
                {{
                    "slide_number": 2,
                    "slide_type": "CONTENT_SLIDE", 
                    "title": "Topic Title",
                    "content_outline": ["Key point 1", "Key point 2", "Key point 3"]
                }}
            ]
        }}

        CRITICAL: Never exceed {get_max_slides()} slides regardless of content volume. Your entire output must be a single, valid JSON object.
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, extracted_content: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Analyze content and create presentation structure"""
        try:
            analysis_prompt = f"""
            CONTENT ANALYSIS & STRUCTURE CREATION:
            
            EXTRACTED CONTENT: "{extracted_content[:2500]}..."
            
            Analyze this content and create an optimal presentation structure.
            1. Analyze content to identify main topics and complexity.
            2. Determine the optimal number of slides (between {PRESENTATION_CONFIG['min_slides']} and {get_max_slides()}).
            3. Create a detailed slide-by-slide outline in the specified JSON format.
            
            Focus on creating a compelling narrative flow.
            """
            
            self.add_user_message(analysis_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            if response and isinstance(response, list) and len(response) > 0:
                last_message = response[-1]
                response_content = str(last_message.content)
            else:
                response_content = str(response)

            self.add_assistant_message(response_content)
            
            return self._validate_and_enforce_limits(response_content, extracted_content)

        except Exception as e:
            print(f"Structure creation error: {str(e)}")
            return self._create_fallback_structure(extracted_content)

    def _validate_and_enforce_limits(self, ai_response: str, content: str) -> str:
        """Validate response and enforce slide limits"""
        try:
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(ai_response)
            
            # Enforce slide count limits
            slide_planning = result.get("slide_planning", {})
            optimal_slides = slide_planning.get("optimal_slides", PRESENTATION_CONFIG['default_slides'])
            
            # Apply hard limits
            max_slides = get_max_slides()
            min_slides = PRESENTATION_CONFIG['min_slides']
            
            if optimal_slides > max_slides:
                optimal_slides = max_slides
                slide_planning["reasoning"] += f" | Limited to maximum {max_slides} slides"
                slide_planning["max_slides_enforced"] = max_slides
            elif optimal_slides < min_slides:
                optimal_slides = min_slides
                slide_planning["reasoning"] += f" | Minimum {min_slides} slides enforced"
            
            slide_planning["optimal_slides"] = optimal_slides
            result["slide_planning"] = slide_planning
            
            # Ensure structure matches slide count
            structure = result.get("presentation_structure", [])
            if len(structure) != optimal_slides:
                result["presentation_structure"] = self._adjust_structure_length(structure, optimal_slides)
            
            return json.dumps(result, indent=2)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Structure validation error: {str(e)}")
            return self._create_fallback_structure(content)

    def _adjust_structure_length(self, structure: list, target_slides: int) -> list:
        """Adjust structure to match target slide count"""
        if len(structure) == target_slides:
            return structure
        
        if len(structure) > target_slides:
            # Too many slides - keep title + summary + middle content
            return structure[:target_slides]
        
        # Too few slides - add content slides
        adjusted = structure.copy()
        while len(adjusted) < target_slides:
            slide_num = len(adjusted) + 1
            adjusted.append({
                "slide_number": slide_num,
                "slide_type": "CONTENT_SLIDE",
                "title": f"Additional Content {slide_num - 1}",
                "content_outline": ["Key information", "Supporting details", "Examples"]
            })
        
        return adjusted

    def _create_fallback_structure(self, content: str) -> str:
        """Create fallback structure when AI analysis fails"""
        default_slides = PRESENTATION_CONFIG['default_slides']
        
        # Simple content analysis
        content_sections = content.split('\n\n')
        main_topics = [section[:50] + "..." for section in content_sections[:5] if section.strip()]
        
        structure = [
            {
                "slide_number": 1,
                "slide_type": "TITLE_SLIDE",
                "title": "Document Presentation",
                "content_outline": ["Main title", "Document overview"]
            }
        ]
        
        # Add content slides
        for i, topic in enumerate(main_topics[:default_slides-2], 2):
            structure.append({
                "slide_number": i,
                "slide_type": "CONTENT_SLIDE",
                "title": f"Topic {i-1}",
                "content_outline": [topic, "Supporting information", "Key details"]
            })
        
        # Add summary slide
        structure.append({
            "slide_number": default_slides,
            "slide_type": "SUMMARY_SLIDE",
            "title": "Summary",
            "content_outline": ["Key takeaways", "Main conclusions", "Next steps"]
        })
        
        return json.dumps({
            "content_analysis": {
                "main_topics": main_topics,
                "content_complexity": "medium",
                "estimated_duration": "15-20 minutes"
            },
            "slide_planning": {
                "optimal_slides": default_slides,
                "reasoning": "Fallback analysis - using default slide count",
                "max_slides_enforced": get_max_slides()
            },
            "presentation_structure": structure
        }, indent=2)