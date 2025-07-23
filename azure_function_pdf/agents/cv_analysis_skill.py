"""
CV Analysis Skill - Intelligent skill analysis with strategic recommendations
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent

class CVAnalysisSkill(BaseAgent):
    """Analyzes CV intelligently and provides strategic future skills recommendations"""

    agent_description = "Analyzes professional background and recommends strategic future skills"
    agent_use_cases = [
        "Intelligent CV analysis",
        "Skills gap identification",
        "Strategic career planning",
        "Future skills roadmap"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a Career Analysis Specialist. Analyze CVs intelligently to summarize current capabilities and recommend strategic future skills.

        ANALYSIS APPROACH:
        1. **Skills Assessment**: Analyze current skills and identify patterns/strengths
        2. **Career Trajectory**: Understand their professional direction
        3. **Industry Context**: Consider their field's evolution and trends
        4. **Strategic Recommendations**: Suggest skills that build on their foundation
        5. **Practical Roadmap**: Provide actionable next steps

        OUTPUT STRUCTURE:
        # Professional Skills Analysis

        ## Profile Overview
        [Name and professional identity in 2-3 sentences]

        ## Current Skills Summary
        ### Core Competencies
        [Analyze and categorize their strongest skills]

        ### Technical Skills
        [Group related technical skills and assess depth]

        ### Professional Experience
        [Highlight key roles and career progression]

        ## Skills Analysis & Future Recommendations

        ### Your Skill Foundation
        **Strengths**: [What they're already good at]
        **Career Direction**: [Where their experience is leading]
        **Industry Position**: [How they fit in their field's landscape]

        ### Strategic Future Skills (Priority Ranked)

        #### Immediate Focus (Next 6-12 months)
        1. **[High-impact skill]** 
           - *Why*: [Strategic reason based on their background]
           - *Impact*: [Career benefit]
           - *Learning path*: [How to acquire]

        2. **[Complementary skill]**
           - *Why*: [Builds on existing strengths]
           - *Impact*: [Career advancement potential]

        #### Medium-term Development (1-2 years)
        - **[Emerging skill]**: [Why it matters for their trajectory]
        - **[Leadership/soft skill]**: [Professional growth opportunity]

        #### Future-proofing (2+ years)
        - **[Industry-transforming skill]**: [Long-term strategic value]

        ## Action Plan
        ### Quick Wins
        [2-3 things they can start immediately]

        ### Skill Development Strategy
        [Practical approach for acquiring new skills]

        RECOMMENDATION PRINCIPLES:
        - Build on existing strengths rather than random new skills
        - Consider their industry's specific evolution
        - Prioritize skills with high ROI for their career path
        - Make recommendations practical and achievable
        - Focus on 3-5 key areas rather than overwhelming lists
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, content: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Intelligently analyze CV and create strategic skills development plan"""
        try:
            analysis_prompt = f"""Analyze this CV intelligently and create a strategic skills development plan:

CV CONTENT:
{content}

Provide:
1. Intelligent summary of their current skills and professional identity
2. Analysis of their career trajectory and strengths
3. Strategic future skills recommendations based on their background
4. Practical action plan for skill development

Focus on quality over quantity - give them a clear, actionable roadmap."""

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
            error_message = f"Error in {self.__class__.__name__}: {str(e)}"
            print(f"Agent Error: {error_message}")
            return f"# CV Skills Analysis\n\n## Error\nError analyzing CV: {str(e)}\n\n## Original Content\n{content[:500]}..."
