"""
Smart Presentation Processor - Intent analysis only
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
import json

class SmartPresentationProcessor(BaseAgent):
    """Analyzes user intent for PowerPoint generation - Intent only"""

    agent_description = "Intent analysis for PowerPoint generation requests"
    agent_use_cases = [
        "User intent detection",
        "CREATE_PRESENTATION vs INFORMATION_REQUEST classification"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are an Intent Analysis Expert for PowerPoint generation requests.

        ANALYZE USER REQUESTS FOR INTENT ONLY:
        - **CREATE_PRESENTATION**: User wants PowerPoint generated
        - **INFORMATION_REQUEST**: User wants to know capabilities

        INTENT CLASSIFICATION:
        1. **CREATE_PRESENTATION** - User wants PowerPoint:
           - "create presentation", "make slides", "generate ppt"
           - "convert to powerpoint", "turn into slides"
           - Document upload without specific questions
           - Action words: "create", "make", "generate", "proceed"
           
        2. **INFORMATION_REQUEST** - User wants capabilities info:
           - "what can you do", "how does this work", "explain features"
           - "what's in this document" (asking about content, not requesting action)

        RESPONSE FORMAT (JSON only, no markdown):
        {
            "intent": "CREATE_PRESENTATION" | "INFORMATION_REQUEST",
            "confidence": 0.85,
            "reasoning": "Clear explanation of intent classification"
        }

        DO NOT analyze slide count, content structure, or document details.
        Focus ONLY on understanding what the user wants to accomplish.
        Your entire output must be a single, valid JSON object.
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, user_input: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Analyze user intent for PowerPoint generation"""
        try:
            has_previous_document = context_metadata.get("has_previous_document", False) if context_metadata else False
            
            analysis_prompt = f"""
            INTENT ANALYSIS:
            
            USER REQUEST: "{user_input}"
            CONTEXT: {"User has previous document" if has_previous_document else "New request"}
            
            Analyze this request to determine user intent.
            Focus ONLY on intent classification. Do not analyze document content or slide requirements.
            Output your response in the specified JSON format.
            """
            
            self.add_user_message(analysis_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            # --- THE FIX ---
            if response and isinstance(response, list) and len(response) > 0:
                last_message = response[-1]
                response_content = str(last_message.content)
            else:
                response_content = str(response)
            # --- END FIX ---

            self.add_assistant_message(response_content)
            
            return self._validate_response(response_content, user_input)

        except Exception as e:
            print(f"Intent analysis error: {str(e)}")
            return self._create_fallback(user_input)

    def _validate_response(self, ai_response: str, user_input: str) -> str:
        """Validate and clean AI response"""
        try:
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(ai_response)
            
            # Ensure required fields
            if "intent" not in result:
                result["intent"] = "CREATE_PRESENTATION"
            if "confidence" not in result:
                result["confidence"] = 0.7
            if "reasoning" not in result:
                result["reasoning"] = "Intent classification based on user request patterns"
            
            return json.dumps(result, indent=2)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Response validation error: {str(e)}")
            return self._create_fallback(user_input)

    def _create_fallback(self, user_input: str) -> str:
        """Create fallback intent analysis"""
        user_lower = user_input.lower()
        
        # Simple keyword-based classification
        if any(word in user_lower for word in ["what", "how", "explain", "capabilities", "features"]):
            intent = "INFORMATION_REQUEST"
        else:
            intent = "CREATE_PRESENTATION"
        
        return json.dumps({
            "intent": intent,
            "confidence": 0.6,
            "reasoning": "Fallback analysis using keyword patterns"
        }, indent=2)