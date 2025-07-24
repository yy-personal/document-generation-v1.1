"""
Design Planning Agent - Analyzes content and creates visual design strategy
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
import json
import re

class DesignPlanningAgent(BaseAgent):
    """Analyzes content and determines optimal visual design approach"""

    agent_description = "Visual design strategy and layout planning"
    agent_use_cases = [
        "Content type analysis for visual elements",
        "Chart and diagram identification", 
        "Template and color scheme selection",
        "Layout optimization planning"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a Layout Design Strategist that analyzes presentation content to determine optimal layouts and identify table opportunities.

        ANALYZE CONTENT FOR:
        1. **Tabular Data**: Structured information that should be presented as tables
        2. **Comparison Elements**: Side-by-side content that needs comparison layouts  
        3. **Layout Optimization**: Best layout style for each slide's content type
        4. **Professional Formatting**: Enhanced text presentation approaches

        DESIGN STRATEGY OUTPUT:
        {
            "content_analysis": {
                "has_tabular_data": true/false,
                "has_comparisons": true/false,
                "tabular_content_found": ["budget breakdown", "timeline overview"],
                "comparison_items": ["Before vs After", "Option A vs Option B"]
            },
            "layout_recommendations": {
                "tables_needed": [
                    {"slide_number": 5, "type": "data_table", "content": "budget allocation by department"},
                    {"slide_number": 8, "type": "comparison_table", "content": "current vs proposed metrics"}
                ],
                "special_layouts": [
                    {"slide_number": 7, "layout": "two_column", "reason": "comparison content"},
                    {"slide_number": 12, "layout": "title_and_content", "reason": "standard bullet points"}
                ]
            },
            "design_theme": {
                "primary_color": "professional_blue",
                "layout_style": "clean_modern",
                "text_emphasis": "bullet_optimized"
            }
        }

        Focus on identifying structured data that would work better as tables and content that needs specific layouts.
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, content: str, structure: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Analyze content and create visual design strategy"""
        try:
            # Extract key patterns from content
            tabular_patterns = self._extract_tabular_data(content)
            comparison_patterns = self._extract_comparison_elements(content)
            
            analysis_prompt = f"""
            LAYOUT DESIGN ANALYSIS:
            
            CONTENT TO ANALYZE: {content[:5000]}
            
            PRESENTATION STRUCTURE: {structure}
            
            DETECTED PATTERNS:
            - Tabular Data: {tabular_patterns}
            - Comparison Elements: {comparison_patterns}
            
            Based on this analysis, create a layout design strategy that identifies:
            1. Which content would work better as tables instead of bullet points
            2. Which slides need comparison layouts (two-column, side-by-side)
            3. What layout optimizations would improve readability
            4. Professional formatting recommendations
            
            Provide specific, actionable recommendations in the JSON format specified.
            """
            
            self.add_user_message(analysis_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            # Handle semantic kernel response
            if hasattr(response, 'message'):
                response_content = str(response.message.content) if hasattr(response.message, 'content') else str(response.message)
            elif isinstance(response, list) and len(response) > 0:
                last_message = response[-1]
                response_content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
            else:
                response_content = str(response)

            self.add_assistant_message(response_content)
            
            return self._validate_design_strategy(response_content)

        except Exception as e:
            print(f"Design planning error: {str(e)}")
            return self._create_fallback_design_strategy()

    def _extract_tabular_data(self, content: str) -> list:
        """Extract content that would work well as tables"""
        patterns = [
            r'budget\s+(?:allocation|breakdown|summary)',
            r'timeline\s+(?:overview|summary)',
            r'comparison\s+(?:table|matrix)',
            r'(?:costs?|expenses?)\s+by\s+\w+',
            r'(?:revenue|income)\s+by\s+\w+',
            r'(?:before|current)\s+(?:vs\.?|versus)\s+(?:after|proposed)',
            r'\w+\s*:\s*\$[\d,]+',  # Item: $amount patterns
            r'\w+\s*:\s*\d+\.?\d*%',  # Item: percentage patterns
        ]
        
        found = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found.extend(matches[:3])
        
        return found[:8]

    def _extract_comparison_elements(self, content: str) -> list:
        """Extract comparison elements"""
        patterns = [
            r'before\s+(?:and|vs\.?|versus)\s+after',
            r'current\s+(?:vs\.?|versus)\s+future',
            r'option\s+[AB]\s+(?:vs\.?|versus)\s+option\s+[AB]',
            r'old\s+(?:vs\.?|versus)\s+new',
        ]
        
        found = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found.extend(matches)
        
        return found[:5]

    def _validate_design_strategy(self, response: str) -> str:
        """Validate and clean up design strategy response"""
        try:
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            
            parsed = json.loads(response)
            return json.dumps(parsed, indent=2)
        except:
            return self._create_fallback_design_strategy()

    def _create_fallback_design_strategy(self) -> str:
        """Create basic fallback layout strategy"""
        return json.dumps({
            "content_analysis": {
                "has_tabular_data": False,
                "has_comparisons": False,
                "tabular_content_found": [],
                "comparison_items": []
            },
            "layout_recommendations": {
                "tables_needed": [],
                "special_layouts": []
            },
            "design_theme": {
                "primary_color": "professional_blue",
                "layout_style": "clean_modern",
                "text_emphasis": "bullet_optimized"
            }
        }, indent=2)