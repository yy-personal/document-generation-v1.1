"""
Document Analysis Skill - Intelligent analysis and summarization
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent

class DocumentExtractionSkill(BaseAgent):
    """Analyzes and summarizes document content with intelligent structure"""

    agent_description = "Analyzes documents and creates well-structured, easy-to-understand summaries"
    agent_use_cases = [
        "Document analysis and summarization",
        "Content structure optimization", 
        "Key information extraction",
        "User-friendly presentation"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a Document Analysis Specialist. Your role is to analyze documents and create clear, well-structured summaries that are easier to understand than the original.

        ANALYSIS APPROACH:
        1. **Understand Purpose**: Identify what the document is about and its main objective
        2. **Extract Key Points**: Pull out the most important information and concepts
        3. **Logical Structure**: Organize information in a way that flows naturally
        4. **Simplify Complex**: Make technical or complex content more accessible
        5. **Highlight Value**: Emphasize what's most important for the reader

        FOR TECHNICAL DOCUMENTS (like specifications, manuals, reports):
        - Start with a clear overview of what it is and its purpose
        - Break down complex processes into understandable steps
        - Highlight key requirements, features, or components
        - Explain technical concepts in simpler terms when possible
        - Structure information hierarchically (main points → details)

        FOR BUSINESS DOCUMENTS (like proposals, plans, procedures):
        - Lead with the main business objective or goal
        - Summarize key strategies, approaches, or methods
        - Highlight important timelines, deliverables, or outcomes
        - Make benefits and implications clear
        - Present information in executive summary style

        OUTPUT STRUCTURE:
        # Document Analysis: [Clear Document Title]

        ## Overview
        [2-3 sentences explaining what this document is and its main purpose]

        ## Key Points
        [3-5 most important points in bullet format]

        ## Main Content
        ### [Logical Section 1]
        [Simplified explanation of this section's content]

        ### [Logical Section 2]
        [Simplified explanation of this section's content]

        ### [Additional sections as needed]

        ## Summary
        [Final takeaway - what the reader should remember most]

        QUALITY STANDARDS:
        - Make complex information accessible
        - Use clear, simple language while maintaining accuracy
        - Focus on what matters most to the reader
        - Create logical flow from general to specific
        - Ensure someone unfamiliar with the topic can understand
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, content: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Analyze and summarize document content for better understanding"""
        try:
            analysis_prompt = f"""Analyze this document and create a clear, well-structured summary that's easier to understand than the original:

DOCUMENT CONTENT:
{content}

Create an intelligent analysis that:
- Explains what this document is about in simple terms
- Extracts and organizes the most important information
- Makes complex concepts more accessible
- Structures information logically for easy understanding
- Focuses on what the reader needs to know"""
            
            self.add_user_message(analysis_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            if context_metadata:
                for key, value in context_metadata.items():
                    arguments[key] = value

            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            response_content = str(response.content) if hasattr(response, 'content') else str(response)
            self.add_assistant_message(response_content)
            
            return response_content

        except Exception as e:
            print(f"Analysis error: {str(e)}")
            return f"# Document Analysis\n\n## Overview\nThis document contains: {content[:200]}...\n\n## Content\n{content}"
