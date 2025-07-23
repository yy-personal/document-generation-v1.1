"""
Smart Presentation Processor - Intent analysis and slide optimization
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
import json

class SmartPresentationProcessor(BaseAgent):
    """Analyzes user intent and optimizes slide count for presentation generation"""

    agent_description = "Intent analysis and slide count optimization for PowerPoint generation"
    agent_use_cases = [
        "User intent detection for PowerPoint requests", 
        "Target slide count optimization",
        "Content volume analysis"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a PowerPoint Generation Expert that analyzes user requests and document content for presentation generation.

        ANALYZE USER REQUESTS FOR:
        - Intent: CREATE_PRESENTATION vs INFORMATION_REQUEST
        - Target slide count for optimal information density (default: 12 slides)
        - Content highlights for presentation focus

        INTENT DETECTION:
        - **CREATE_PRESENTATION**: User wants PowerPoint generated
          - "create presentation", "make slides", "generate ppt"
          - Document upload without specific questions
        - **INFORMATION_REQUEST**: User wants to know capabilities
          - "what can you do", "how does this work", "explain features"

        SLIDE COUNT OPTIMIZATION:
        - Default: 12 slides for business presentations
        - Consider content volume and complexity
        - Maintain 6x6 rule (max 6 bullets, 6 words each)
        - Maximum: 15 slides (enforce strict limit)

        RESPONSE FORMAT (JSON only):
        {
            "intent": "CREATE_PRESENTATION" | "INFORMATION_REQUEST",
            "confidence": 0.85,
            "reasoning": "Detailed explanation of analysis",
            "estimated_slides": 12,
            "content_highlights": ["Key points identified for slides"],
            "fallback_used": false
        }

        EXAMPLES:
        User: "create presentation from this report"
        Response: {intent: "CREATE_PRESENTATION", target_slides: 12}

        User: "what can you do with presentations?"
        Response: {intent: "INFORMATION_REQUEST", target_slides: 0}
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, user_input: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Analyze presentation intent and determine optimal approach"""
        try:
            document_content = context_metadata.get("document_content", "") if context_metadata else ""
            conversation_context = context_metadata.get("has_previous_document", False) if context_metadata else False
            
            # Build comprehensive analysis prompt
            analysis_prompt = f"""
            PRESENTATION INTENT ANALYSIS:
            
            USER REQUEST: "{user_input}"
            DOCUMENT PREVIEW: "{document_content[:1200]}..."
            CONVERSATION CONTEXT: {"User has previous document" if conversation_context else "New document upload"}
            
            Analyze this request for optimal PowerPoint generation:
            1. User intent (create presentation vs information request)
            2. Optimal slide count considering content volume and complexity
            3. Key content highlights that should be emphasized
            
            Consider document characteristics:
            - Length and complexity
            - Structure (headings, sections, bullet points)
            - Content type (technical, business, strategic)
            - Key topics and themes
            
            CRITICAL: Always provide specific, actionable analysis with clear reasoning
            for slide count optimization.
            """
            
            self.add_user_message(analysis_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            response_content = str(response.content) if hasattr(response, 'content') else str(response)
            self.add_assistant_message(response_content)
            
            return self._validate_and_enhance_response(response_content, user_input, document_content)

        except Exception as e:
            print(f"Presentation analysis error: {str(e)}")
            return self._create_presentation_fallback(user_input, document_content)

    def _validate_and_enhance_response(self, ai_response: str, user_input: str, document_content: str) -> str:
        """Validate AI response and apply enhancements"""
        try:
            # Clean and parse JSON response
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(ai_response)
            
            # Apply slide count constraints (8-15 slides max)
            estimated_slides = result.get("estimated_slides", 12)
            
            if estimated_slides > 15:
                result["estimated_slides"] = 15
                result["reasoning"] += " | Limited to max 15 slides"
            elif estimated_slides < 8:
                result["estimated_slides"] = 12
                result["reasoning"] += " | Minimum 8 slides for effective presentation"
            
            # Ensure required fields
            if "content_highlights" not in result:
                result["content_highlights"] = self._extract_content_highlights(document_content)
            
            result["fallback_used"] = False
            
            return json.dumps(result, indent=2)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Response validation error: {str(e)}")
            return self._create_presentation_fallback(user_input, document_content)

    def _extract_content_highlights(self, document_content: str) -> list:
        """Extract key content highlights for presentation focus"""
        highlights = []
        
        # Look for headings and structure
        lines = document_content.split('\n')
        for line in lines[:20]:  # First 20 lines
            line = line.strip()
            if line and (line.isupper() or line.startswith('#') or len(line.split()) <= 8):
                if line not in highlights and len(line) > 3:
                    highlights.append(line[:50])
                    if len(highlights) >= 5:
                        break
        
        if not highlights:
            # Fallback to first few sentences
            sentences = document_content.split('.')[:3]
            highlights = [s.strip()[:50] for s in sentences if s.strip()]
        
        return highlights[:5]

    def _create_presentation_fallback(self, user_input: str, document_content: str) -> str:
        """Create intelligent fallback for presentation analysis"""
        user_lower = user_input.lower()
        
        # Determine intent
        if any(word in user_lower for word in ["what", "how", "explain", "capabilities", "features"]):
            intent = "INFORMATION_REQUEST"
            estimated_slides = 0
        else:
            intent = "CREATE_PRESENTATION"
            estimated_slides = 12
        
        return json.dumps({
            "intent": intent,
            "confidence": 0.6,
            "reasoning": "Fallback analysis using keyword patterns and document structure",
            "estimated_slides": estimated_slides,
            "content_highlights": self._extract_content_highlights(document_content),
            "fallback_used": True
        }, indent=2)
