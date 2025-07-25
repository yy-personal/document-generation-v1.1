"""
Slide Content Generator - Creates detailed slide content
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
import json

class SlideContentGenerator(BaseAgent):
    """Generates detailed content for individual slides"""

    agent_description = "Detailed slide content creation and formatting"
    agent_use_cases = [
        "Slide-specific content generation",
        "Bullet point optimization", 
        "Content formatting for slides",
        "Presentation-ready text creation"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a Slide Content Specialist that creates engaging, professional slide content based STRICTLY on the provided document structure and content.

        CRITICAL REQUIREMENTS:
        - **STAY TRUE TO SOURCE**: All content must be directly derived from the provided structure
        - **NO GENERIC CONTENT**: Never create generic business content or placeholder text
        - **MATCH STRUCTURE**: Follow the exact slide structure and topics provided
        - **USE ACTUAL DATA**: Include specific details, numbers, dates from the source material

        CONTENT GUIDELINES:
        - **Quality Over Quantity**: Only create slides with meaningful, substantive content
        - **Natural Content**: 2-6 bullets per slide based on available information
        - **Clear Language**: Professional but accessible terminology
        - **Action-Oriented**: Use active voice and strong verbs
        - **Source-Driven**: Every bullet point must relate to the actual document content
        - **Consistent Style**: Parallel structure in bullet points
        - **No Padding**: Skip slides or reduce slide count if content is insufficient

        SLIDE CONTENT CREATION PROCESS:
        1. **Analyze Structure**: Understand each slide's purpose and topic
        2. **Extract Key Info**: Pull relevant details from the source content
        3. **Format Professionally**: Create clear, engaging bullet points
        4. **Maintain Accuracy**: Ensure all information is factually correct from source

        OUTPUT FORMAT (JSON only, no markdown):
        Generate slide content in JSON format exactly matching the provided structure:

        [
          {
            "title": "Exact Title from Structure",
            "content": [
              "Content item 1 (no manual bullets - PowerPoint handles this)",
              "Content item 2 (for multiple points)", 
              "Content item 3 (when appropriate)"
            ],
            "layout": "SLIDE_TYPE_FROM_STRUCTURE"
          },
          {
            "title": "Overview Example",
            "content": [
              "This project represents a comprehensive modernization effort designed to enhance our core technology platform and improve user experience across all digital touchpoints."
            ],
            "layout": "OVERVIEW_SLIDE"
          }
        ]

        CRITICAL: Your content must be 100% derived from the provided structure and source material. 
        Never generate generic business content. Your entire output must be a single, valid JSON array.
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, structure: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate detailed slide content from structure, staying true to source material"""
        try:
            # Parse the structure to understand what we're working with
            try:
                structure_data = json.loads(structure)
                if "presentation_structure" in structure_data:
                    # Full structure data received
                    slide_list = structure_data.get("presentation_structure", [])
                    content_analysis = structure_data.get("content_analysis", {})
                    main_topics = content_analysis.get("main_topics", [])
                else:
                    # Just the slide array received
                    slide_list = structure_data if isinstance(structure_data, list) else []
                    main_topics = []
            except json.JSONDecodeError as e:
                print(f"SlideContentGenerator: Failed to parse structure JSON: {e}")
                return self._fallback_content_generation(structure)
            
            if not slide_list:
                print("SlideContentGenerator: No slides found in structure")
                return self._fallback_content_generation(structure)
            
            print(f"SlideContentGenerator: Processing {len(slide_list)} slides based on topics: {main_topics}")
            
            content_prompt = f"""
            SLIDE CONTENT GENERATION FROM SOURCE MATERIAL:
            
            You must create slide content based EXCLUSIVELY on the following presentation structure.
            This structure was created from specific document content - you must honor that content.
            
            MAIN TOPICS IDENTIFIED: {main_topics}
            
            PRESENTATION STRUCTURE: {json.dumps(slide_list, indent=2)}
            
            CRITICAL INSTRUCTIONS:
            1. **ANALYZE THE STRUCTURE**: Parse the JSON structure to understand each slide's purpose
            2. **USE STRUCTURE CONTENT**: Base your content on titles and content_outline provided in the structure
            3. **EXPAND APPROPRIATELY**: Take the outline points and expand them into professional bullet points
            4. **MAINTAIN ACCURACY**: Keep all facts, numbers, dates, and details from the original structure
            5. **NO INVENTION**: Do not add generic business content or create new information
            6. **USE MAIN TOPICS**: Reference the main topics to ensure relevance to the source document
            
            CONTENT REQUIREMENTS:
            - Create slides for all structured content, expanding brief outlines into detailed explanations
            - Use appropriate content format based on slide type and content nature:
              * BULLET FORMAT: For lists, key points, multiple items (2-6 items)
              * PARAGRAPH FORMAT: For explanations, descriptions, single concepts
            - Use the exact slide titles from the structure where content exists  
            - Use the exact slide types (slide_type field) from the structure
            - EXPAND SPARSE CONTENT: When content_outline is brief, create detailed explanatory content that maintains relevance to the source
            - For sparse content, focus on:
              * Contextual explanations of what the content means
              * Implications and significance of the information
              * How it relates to the overall document theme
              * Professional elaboration while staying factually accurate
            - Ensure minimum 12-slide presentation even with limited source material
            - Better to have comprehensive explanatory slides than empty presentations
            
            FORMATTING GUIDELINES:
            - Title slides: Use paragraph format for subtitle/description
            - Overview slides: Use paragraph format for narrative explanation
            - Analysis/Process slides: Use bullet format for multiple points
            - Conclusion/Summary: Use bullet format for key takeaways
            - Thank You slides: Keep concise - maximum 3 brief items
            - DON'T add manual bullet symbols (•) - PowerPoint will handle bullets automatically
            
            OUTPUT: Valid JSON array with slides exactly matching the structure provided.
            Each slide must have: title, content (array of strings), layout (use slide_type value)
            """
            
            self.add_user_message(content_prompt)
            
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

            # Clean up markdown formatting if present
            if response_content.startswith('```json'):
                response_content = response_content.replace('```json', '').replace('```', '').strip()

            # Validate that we got valid JSON
            try:
                parsed_response = json.loads(response_content)
                if isinstance(parsed_response, list) and len(parsed_response) > 0:
                    print(f"SlideContentGenerator: Successfully generated {len(parsed_response)} slides with AI")
                    self.add_assistant_message(response_content)
                    return response_content
                else:
                    print(f"SlideContentGenerator: Invalid AI response format, using fallback")
                    return self._fallback_content_generation(structure)
            except json.JSONDecodeError as e:
                print(f"SlideContentGenerator: AI response not valid JSON ({e}), using fallback")
                return self._fallback_content_generation(structure)

        except Exception as e:
            print(f"Content generation error: {str(e)}")
            return self._fallback_content_generation(structure)

    def _fallback_content_generation(self, structure: str) -> str:
        """Fallback content generation that preserves source structure"""
        slides = []
        try:
            # Try to parse as JSON structure first
            structure_data = json.loads(structure)
            slide_list = structure_data.get("presentation_structure", [])

            for slide_plan in slide_list:
                # Use the structure content directly but ensure it's properly formatted
                content_outline = slide_plan.get("content_outline", [])
                
                # Only include slides with substantive content
                if content_outline and len(content_outline) > 0 and any(len(str(item).strip()) > 10 for item in content_outline):
                    # Filter out generic or too-short content
                    quality_content = [str(item) for item in content_outline if len(str(item).strip()) > 10][:6]
                    if len(quality_content) >= 2:  # Need at least 2 good bullet points
                        content = quality_content
                    else:
                        # Skip this slide - not enough quality content
                        continue
                else:
                    # Skip slides with insufficient content rather than creating filler
                    continue

                slides.append({
                    "title": slide_plan.get("title", "Slide Title"),
                    "content": content,
                    "layout": slide_plan.get("slide_type", "CONTENT_SLIDE")
                })
                
            print(f"SlideContentGenerator: Using fallback generation for {len(slides)} slides")
            
            if not slides:
                raise ValueError("Could not parse structure")

        except (json.JSONDecodeError, ValueError):
            # Last resort fallback - create basic slides
            print("Warning: Using basic fallback for slide content generation")
            slides = [
                {
                    "title": "Presentation Overview",
                    "content": ["Content could not be generated", "Please check source document", "Manual review needed"],
                    "layout": "TITLE_SLIDE"
                }
            ]

        return json.dumps(slides, indent=2)