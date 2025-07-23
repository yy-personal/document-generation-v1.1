"""
Document Content Extractor - Organizes content for presentation structure
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent

class DocumentContentExtractor(BaseAgent):
    """Extracts and organizes document content for presentations"""

    agent_description = "Document content organization and key point extraction"
    agent_use_cases = [
        "Content hierarchy identification",
        "Key point extraction for slides", 
        "Document structure analysis",
        "Information prioritization"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a Content Organization Expert that analyzes documents to extract key information for business presentations.

        ANALYZE AND ORGANIZE:
        - Document structure and main topics
        - Key points suitable for slide content
        - Hierarchical information flow
        - Supporting details and examples

        EXTRACTION PRIORITIES:
        1. **Main Topics**: Central themes that deserve individual slides
        2. **Key Points**: Important information within each topic (3-6 points per slide)
        3. **Supporting Details**: Evidence, examples, statistics
        4. **Visual Elements**: Charts, tables, diagrams mentioned in text

        CONTENT ORGANIZATION:
        - Group related information logically
        - Identify natural presentation flow
        - Prioritize information by importance
        - Suggest slide-worthy topics

        OUTPUT FORMAT:
        Provide organized content as structured text with clear headings and bullet points:

        # Main Topic 1
        - Key point 1
        - Key point 2
        - Key point 3

        # Main Topic 2
        - Key point 1
        - Key point 2

        Keep content concise and presentation-ready. Focus on the most important information for business presentations.
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, content: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Extract and organize document content"""
        try:
            analysis_prompt = f"""
            DOCUMENT CONTENT EXTRACTION:
            
            DOCUMENT TEXT: "{content[:3000]}..."
            
            Extract and organize the key information from this document for a business presentation.
            Focus on identifying the main topics and supporting points that would work well as slides.
            
            Organize content into clear topics with bullet points suitable for slides.
            """
            
            self.add_user_message(analysis_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            response_content = str(response.content) if hasattr(response, 'content') else str(response)
            self.add_assistant_message(response_content)
            
            return response_content

        except Exception as e:
            print(f"Content extraction error: {str(e)}")
            return self._fallback_extraction(content)

    def _fallback_extraction(self, content: str) -> str:
        """Simple fallback content extraction"""
        lines = content.split('\n')
        organized_content = []
        current_section = None
        
        for line in lines[:50]:  # Process first 50 lines
            line = line.strip()
            if not line:
                continue
            
            # Check if line looks like a heading
            if (len(line.split()) <= 6 and 
                (line.isupper() or line.startswith('#') or 
                 any(word in line.lower() for word in ['overview', 'summary', 'introduction', 'conclusion']))):
                if current_section:
                    organized_content.append(current_section)
                current_section = f"# {line.lstrip('# ')}\n"
            elif current_section and len(line.split()) > 3:
                current_section += f"- {line[:100]}\n"
        
        if current_section:
            organized_content.append(current_section)
        
        if not organized_content:
            organized_content = [f"# Document Overview\n- {content[:200]}..."]
        
        return '\n'.join(organized_content)