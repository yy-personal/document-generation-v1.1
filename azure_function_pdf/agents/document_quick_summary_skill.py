"""
Document Quick Summary Skill - Provides fast document summaries without full processing
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent

class DocumentQuickSummarySkill(BaseAgent):
    """Provides quick document summaries for information requests"""

    agent_description = "Provides fast, concise summaries of document content without full processing"
    agent_use_cases = [
        "Quick document overview",
        "Content summarization",
        "Fast information extraction"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a Document Summary Specialist. Provide quick, helpful summaries of document content.

        SUMMARY APPROACH:
        - Read the document content quickly
        - Identify the main type/purpose of the document
        - Extract key information and highlights
        - Provide a concise, informative summary
        - Answer the user's specific question if they asked one

        SUMMARY STRUCTURE:
        1. **Document Type**: What kind of document this is
        2. **Main Purpose**: What the document is about
        3. **Key Points**: 3-5 most important points or sections
        4. **Summary**: Brief overview of the content

        RESPONSE STYLE:
        - Conversational and helpful
        - Focus on what the user wants to know
        - Highlight the most relevant information
        - Keep it concise but informative

        EXAMPLES:
        - For CV: "This is a professional resume for [Name]. It shows their experience in [field], including roles at [companies] and skills in [areas]."
        - For Technical Doc: "This is a functional specification for [system]. It describes [purpose] and outlines [key features]."
        - For Report: "This is a [type] report covering [topic]. The main findings include [key points]."

        Always be helpful and directly address what the user wants to know about the document.
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, content: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate quick summary of document content"""
        try:
            user_question = context_metadata.get("user_question", "What's in this document?") if context_metadata else "What's in this document?"
            
            summary_prompt = f"The user asked: '{user_question}'\n\nProvide a quick, helpful summary of this document:\n\n{content[:2000]}"  # Limit content for speed
            
            self.add_user_message(summary_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            response_content = str(response.content) if hasattr(response, 'content') else str(response)
            self.add_assistant_message(response_content)
            
            return response_content

        except Exception as e:
            print(f"Quick summary error: {str(e)}")
            return f"I can see this document contains information, but I encountered an error providing a summary: {str(e)}"
