"""
Markdown Formatter Agent - Simple, clean formatting for PDF generation
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent

class MarkdownFormatterAgent(BaseAgent):
    """Simple markdown formatting optimized for clean PDF output"""

    agent_description = "Formats content into clean markdown for PDF generation"
    agent_use_cases = [
        "Clean markdown formatting",
        "PDF-ready document structure",
        "Professional presentation"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a Simple Markdown Formatter. Create clean, readable markdown optimized for PDF generation.

        FORMATTING PRINCIPLES:
        1. **Clean Structure**: Clear headings and logical organization
        2. **PDF-Friendly**: Simple formatting that converts well to PDF
        3. **Professional**: Business-appropriate presentation
        4. **Consistent**: Uniform formatting throughout

        MARKDOWN ELEMENTS:
        - **Headers**: # for title, ## for sections, ### for subsections
        - **Lists**: Use - for bullets, 1. 2. 3. for numbered lists
        - **Emphasis**: **bold** for important terms only
        - **Spacing**: Proper line breaks between sections
        - **Tables**: Only when absolutely necessary

        FORMATTING RULES:
        - Start with H1 (#) for document title
        - Use H2 (##) for main sections
        - Use H3 (###) for subsections if needed
        - Keep lists clean and concise
        - Add line breaks between major sections
        - Avoid excessive formatting

        PDF OPTIMIZATION:
        - Structure for good page flow
        - Use headings that create natural breaks
        - Keep formatting simple and clean
        - Ensure readability when printed

        OUTPUT:
        - Return ONLY the clean markdown content
        - No meta-commentary or explanations
        - Ready for immediate PDF conversion
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, content: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format content into clean markdown for PDF generation"""
        try:
            formatting_prompt = f"Format this content into clean, simple markdown for PDF generation:\n\n{content}"
            
            self.add_user_message(formatting_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            response_content = str(response.content) if hasattr(response, 'content') else str(response)
            self.add_assistant_message(response_content)
            
            return response_content

        except Exception as e:
            print(f"Formatting error: {str(e)}")
            # Fallback to basic formatting
            lines = content.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    if line.isupper() or (len(line) < 100 and not line.endswith('.')):
                        # Likely a heading
                        formatted_lines.append(f"## {line}")
                    else:
                        formatted_lines.append(line)
                formatted_lines.append("")
            
            return '\n'.join(formatted_lines)
