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
        You are a Slide Content Specialist that creates engaging, professional slide content.

        GENERATE SLIDE CONTENT:
        - Clear, concise bullet points
        - Professional business presentation language
        - Actionable and meaningful content
        - Proper formatting for visual presentation

        CONTENT GUIDELINES:
        - **6x6 Rule**: Maximum 6 bullets per slide, 6 words per bullet when possible
        - **Clear Language**: Professional but accessible terminology
        - **Action-Oriented**: Use active voice and strong verbs
        - **Consistent Style**: Parallel structure in bullet points

        SLIDE CONTENT FORMAT:
        For each slide, provide:
        - Clear, compelling title
        - Well-formatted bullet points
        - Appropriate content length for readability

        OUTPUT FORMAT (JSON only, no markdown):
        Generate slide content in JSON format:

        [
          {
            "title": "Slide Title",
            "content": [
              "Clear bullet point 1",
              "Actionable bullet point 2", 
              "Meaningful bullet point 3"
            ],
            "layout": "CONTENT_SLIDE"
          }
        ]

        Focus on creating content that will engage the audience and communicate key messages effectively.
        Your entire output must be a single, valid JSON array.
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, structure: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate detailed slide content from structure"""
        try:
            content_prompt = f"""
            SLIDE CONTENT GENERATION:
            
            PRESENTATION STRUCTURE: "{structure}"
            
            Generate detailed, engaging content for each slide based on the structure provided.
            
            Requirements for business presentations:
            - Professional, business-appropriate language
            - Clear, actionable bullet points (max 6 per slide)
            - Content optimized for visual presentation
            
            Create compelling slide content that effectively communicates the key messages.
            Output in JSON format with a list of slide objects. Each object must contain 'title', 'content' (an array of strings), and 'layout'.
            """
            
            self.add_user_message(content_prompt)
            
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
            
            return response_content

        except Exception as e:
            print(f"Content generation error: {str(e)}")
            return self._fallback_content_generation(structure)

    def _fallback_content_generation(self, structure: str) -> str:
        """Simple fallback content generation"""
        slides = []
        try:
            structure_data = json.loads(structure)
            slide_list = structure_data.get("presentation_structure", [])

            for slide_plan in slide_list:
                slides.append({
                    "title": slide_plan.get("title", "Fallback Title"),
                    "content": slide_plan.get("content_outline", ["Fallback content."]),
                    "layout": slide_plan.get("slide_type", "CONTENT_SLIDE")
                })
            
            if not slides: # If parsing fails, use old method
                raise ValueError("Could not parse structure")

        except (json.JSONDecodeError, ValueError):
             # This is a less reliable fallback, kept for safety
            slide_sections = structure.split('## Slide')
            for i, section in enumerate(slide_sections[1:], 1):
                lines = section.strip().split('\n')
                title_line = lines[0] if lines else f"Slide {i}"
                title = title_line.split(':', 1)[1].strip() if ':' in title_line else title_line.strip()
                content_points = [line.strip()[2:] for line in lines if line.strip().startswith('- ')]
                if not content_points: content_points = [f"Content for slide {i}"]
                layout = "TITLE_SLIDE" if i == 1 else "CONTENT_SLIDE"
                slides.append({"title": title, "content": content_points[:6], "layout": layout})

        return json.dumps(slides, indent=2)