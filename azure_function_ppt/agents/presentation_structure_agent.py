"""
Presentation Structure Agent - Content analysis + slide planning + structure creation
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides, get_max_slides, PRESENTATION_CONFIG, get_outline_structure
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
        You are a Presentation Structure Expert that analyzes content and creates optimal slide structures following a standardized business presentation outline.

        YOUR RESPONSIBILITIES:
        1. **Content Volume Analysis**: Assess how much content needs to be presented
        2. **Slide Count Determination**: Calculate optimal slides based on content density
        3. **Structure Creation**: Design logical slide sequence following the standard outline

        SLIDE COUNT GUIDELINES:
        - **Flexible**: Determine optimal slide count based on content analysis and best practices
        - **Minimum**: {PRESENTATION_CONFIG['min_slides']} slides (basic presentation structure)
        - **Maximum**: {PRESENTATION_CONFIG['max_slides']} slides (HARD LIMIT - never exceed)
        - **Content-Driven**: Let content complexity and volume guide slide count decisions

        SLIDE COUNT BEST PRACTICES:
        - Light content (1-2 main topics): 6-8 slides typically optimal
        - Medium content (3-5 main topics): 9-12 slides for proper coverage
        - Heavy content (6+ main topics): 12-{PRESENTATION_CONFIG['max_slides']} slides for comprehensive presentation
        - Prioritize clarity and engagement over arbitrary slide counts
        - Always respect the {PRESENTATION_CONFIG['max_slides']} slide maximum

        STANDARD PRESENTATION OUTLINE (follow whenever possible):
        1. **Title Slide** - Main title and subtitle
        2. **Agenda Slide** - Overview of what will be covered
        3. **Introduction Slide** - Context and background
        4. **Key Insight Slides** - Main findings/insights (1 or more based on content)
        5. **Recommendations Slide** - Actionable recommendations
        6. **Conclusion Slide** - Summary of key points
        7. **Thank You Slide** - Closing and contact information

        CONTENT ADAPTATION:
        - Analyze the content to identify key insights that map to the outline
        - Multiple key insights should each get their own slide
        - Balance following the standard outline with content-specific needs
        - Feel free to deviate from the standard outline if content demands it
        - Use your best judgment for slide count and structure based on content analysis

        OUTPUT FORMAT (JSON only, no markdown):
        {{
            "content_analysis": {{
                "main_topics": ["topic1", "topic2", ...],
                "content_complexity": "light|medium|heavy",
                "estimated_duration": "10-15 minutes"
            }},
            "slide_planning": {{
                "optimal_slides": 10,
                "reasoning": "Based on content analysis: X main topics identified, requiring Y slides for optimal presentation flow and audience engagement",
                "max_slides_enforced": {get_max_slides()}
            }},
            "presentation_structure": [
                {{
                    "slide_number": 1,
                    "slide_type": "TITLE_SLIDE",
                    "title": "Title",
                    "content_outline": ["Main title", "Subtitle", "Presenter information"]
                }},
                {{
                    "slide_number": 2,
                    "slide_type": "AGENDA_SLIDE",
                    "title": "Agenda",
                    "content_outline": ["Introduction", "Key Insights", "Recommendations", "Conclusion"]
                }},
                {{
                    "slide_number": 3,
                    "slide_type": "INTRODUCTION_SLIDE",
                    "title": "Introduction",
                    "content_outline": ["Background", "Context", "Objectives"]
                }},
                {{
                    "slide_number": 4,
                    "slide_type": "KEY_INSIGHT_SLIDE",
                    "title": "Key Insight #1",
                    "content_outline": ["Main finding", "Supporting evidence", "Implications"]
                }},
                {{
                    "slide_number": 11,
                    "slide_type": "RECOMMENDATIONS_SLIDE",
                    "title": "Recommendations",
                    "content_outline": ["Action item 1", "Action item 2", "Next steps"]
                }},
                {{
                    "slide_number": 12,
                    "slide_type": "THANK_YOU_SLIDE",
                    "title": "Thank You",
                    "content_outline": ["Thank you", "Contact information", "Questions"]
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
            
            EXTRACTED CONTENT TO ANALYZE: {extracted_content[:12000]}
            
            CRITICAL REQUIREMENTS:
            1. **ANALYZE THE ACTUAL CONTENT**: Base your analysis on the specific content provided above
            2. **EXTRACT REAL TOPICS**: Identify the actual topics, projects, data, and key points from the content
            3. **CREATE RELEVANT STRUCTURE**: Build slides that directly relate to the content provided
            4. **USE SPECIFIC DETAILS**: Include actual names, dates, numbers, and facts from the content
            5. **NO GENERIC CONTENT**: Avoid generic business presentation topics unless they're actually in the content
            
            CONTENT ANALYSIS STEPS:
            1. Identify the main subject/project/topic from the content
            2. Extract key objectives, goals, or main points
            3. Find specific details like timelines, metrics, phases, etc.
            4. Determine optimal slide count based on content density
            5. Create slide-by-slide structure with content-specific titles and outlines
            
            SLIDE STRUCTURE REQUIREMENTS:
            - Use specific titles that reflect the actual content (not generic ones)
            - Include specific details in content_outline (dates, numbers, names, etc.)
            - Create a logical flow that tells the story of the actual document
            - Ensure each slide serves a purpose in presenting the real content
            
            Create a detailed slide-by-slide outline in the specified JSON format based on the ACTUAL content provided.
            """
            
            self.add_user_message(analysis_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            # Handle semantic kernel response
            if hasattr(response, 'message'):
                # New format: AgentResponseItem with message attribute
                response_content = str(response.message.content) if hasattr(response.message, 'content') else str(response.message)
            elif isinstance(response, list) and len(response) > 0:
                # Old format: list of messages
                last_message = response[-1]
                response_content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
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
            optimal_slides = slide_planning.get("optimal_slides", 10)  # Reasonable default if not specified
            
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
        """Adjust structure to match target slide count using standard outline"""
        if len(structure) == target_slides:
            return structure
        
        # Generate structure based on standard outline
        outline_structure = get_outline_structure(target_slides)
        
        adjusted = []
        for i, outline_item in enumerate(outline_structure):
            slide_num = i + 1
            adjusted.append({
                "slide_number": slide_num,
                "slide_type": outline_item["type"],
                "title": outline_item["title"],
                "content_outline": self._get_content_outline_for_type(outline_item["type"])
            })
        
        return adjusted
    
    def _get_content_outline_for_type(self, slide_type: str) -> list:
        """Get appropriate content outline based on slide type"""
        content_outlines = {
            "TITLE_SLIDE": ["Main title", "Subtitle", "Presenter information"],
            "AGENDA_SLIDE": ["Topic 1", "Topic 2", "Topic 3", "Q&A"],
            "INTRODUCTION_SLIDE": ["Background", "Context", "Objectives"],
            "KEY_INSIGHT_SLIDE": ["Main finding", "Supporting evidence", "Implications"],
            "RECOMMENDATIONS_SLIDE": ["Action item 1", "Action item 2", "Next steps"],
            "CONCLUSION_SLIDE": ["Key takeaways", "Summary of insights", "Final thoughts"],
            "THANK_YOU_SLIDE": ["Thank you"]
        }
        return content_outlines.get(slide_type, ["Key point 1", "Key point 2", "Key point 3"])

    def _create_fallback_structure(self, content: str) -> str:
        """Create fallback structure using standard outline when AI analysis fails"""
        # Analyze content to determine reasonable slide count
        content_sections = content.split('\n\n')
        main_topics = [section[:50] + "..." for section in content_sections[:8] if section.strip()]
        
        # Determine fallback slide count based on content analysis
        if len(main_topics) <= 2:
            fallback_slides = 7  # Light content
        elif len(main_topics) <= 5:
            fallback_slides = 10  # Medium content  
        else:
            fallback_slides = 12  # Heavy content
        
        # Ensure within bounds
        fallback_slides = max(PRESENTATION_CONFIG['min_slides'], 
                            min(fallback_slides, get_max_slides()))
        
        # Use standard outline structure
        outline_structure = get_outline_structure(fallback_slides)
        structure = []
        
        for i, outline_item in enumerate(outline_structure):
            slide_num = i + 1
            structure.append({
                "slide_number": slide_num,
                "slide_type": outline_item["type"],
                "title": outline_item["title"],
                "content_outline": self._get_content_outline_for_type(outline_item["type"])
            })
        
        return json.dumps({
            "content_analysis": {
                "main_topics": main_topics,
                "content_complexity": "medium",
                "estimated_duration": "15-20 minutes"
            },
            "slide_planning": {
                "optimal_slides": fallback_slides,
                "reasoning": f"Fallback analysis - {len(main_topics)} topics detected, using {fallback_slides} slides",
                "max_slides_enforced": get_max_slides()
            },
            "presentation_structure": structure
        }, indent=2)