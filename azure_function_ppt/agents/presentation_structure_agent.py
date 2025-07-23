"""
Presentation Structure Agent - Creates slide-by-slide outline
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent

class PresentationStructureAgent(BaseAgent):
    """Creates presentation structure and slide outline"""

    agent_description = "Presentation structure planning and slide outline creation"
    agent_use_cases = [
        "Slide sequence optimization",
        "Presentation flow design", 
        "Content distribution across slides",
        "Narrative structure creation"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a Presentation Structure Expert that creates compelling slide sequences from organized content.

        CREATE PRESENTATION STRUCTURE:
        - Logical slide progression that tells a story
        - Appropriate slide types for different content
        - Balanced information distribution
        - Engaging flow with clear transitions

        SLIDE SEQUENCE PRINCIPLES:
        1. **Opening**: Title slide with clear topic
        2. **Agenda**: Overview of presentation structure (if needed)
        3. **Content Flow**: Main topics in logical order
        4. **Supporting**: Details that build the narrative
        5. **Conclusion**: Summary and key takeaways

        SLIDE TYPES:
        - TITLE_SLIDE: Opening slide with presentation title
        - AGENDA_SLIDE: Presentation outline
        - CONTENT_SLIDE: Standard content with bullet points
        - SUMMARY_SLIDE: Key takeaways and conclusions

        OUTPUT FORMAT:
        Provide slide-by-slide structure with clear slide numbers, titles, and content outline:

        ## Slide 1: [Title]
        **Type:** TITLE_SLIDE
        **Content:**
        - Main title
        - Subtitle

        ## Slide 2: [Title]  
        **Type:** CONTENT_SLIDE
        **Content:**
        - Key point 1
        - Key point 2
        - Key point 3

        Ensure smooth narrative flow and appropriate content distribution for business presentations.
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, extracted_content: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create presentation structure from extracted content"""
        try:
            target_slides = context_metadata.get("target_slides", 12) if context_metadata else 12
            
            structure_prompt = f"""
            PRESENTATION STRUCTURE CREATION:
            
            EXTRACTED CONTENT: "{extracted_content}"
            TARGET SLIDES: {target_slides}
            
            Create a well-structured business presentation outline with {target_slides} slides from the extracted content.
            
            Create logical slide progression that tells a compelling story.
            Distribute content evenly across slides while maintaining narrative flow.
            Focus on business presentation best practices with clear structure.
            """
            
            self.add_user_message(structure_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            response_content = str(response.content) if hasattr(response, 'content') else str(response)
            self.add_assistant_message(response_content)
            
            return response_content

        except Exception as e:
            print(f"Structure creation error: {str(e)}")
            return self._fallback_structure(extracted_content, target_slides)

    def _fallback_structure(self, content: str, target_slides: int) -> str:
        """Simple fallback structure creation"""
        structure = []
        content_sections = content.split('#')
        content_sections = [s.strip() for s in content_sections if s.strip()]
        
        # Title slide
        structure.append("""## Slide 1: Presentation Title
**Type:** TITLE_SLIDE
**Content:**
- Document Analysis Presentation
- Key Insights and Information""")
        
        # Content slides
        slides_per_section = max(1, (target_slides - 1) // max(1, len(content_sections)))
        slide_num = 2
        
        for section in content_sections[:target_slides-1]:
            lines = section.split('\n')
            title = lines[0] if lines else "Content Section"
            content_points = [line.lstrip('- ') for line in lines[1:] if line.strip().startswith('-')][:6]
            
            structure.append(f"""## Slide {slide_num}: {title}
**Type:** CONTENT_SLIDE
**Content:**
{chr(10).join(f'- {point}' for point in content_points[:6])}""")
            slide_num += 1
            
            if slide_num > target_slides:
                break
        
        return '\n\n'.join(structure)
