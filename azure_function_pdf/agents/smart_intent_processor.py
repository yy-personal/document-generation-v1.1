"""
Smart Intent Processor - Single AI call for comprehensive intent analysis
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from config import get_ai_service, apply_config_overrides
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
import json

class SmartIntentProcessor(BaseAgent):
    """Unified processor that handles intent detection, classification, and confidence in one AI call"""

    agent_description = "Comprehensive intent analysis with ambiguity handling and smart defaults"
    agent_use_cases = [
        "Vague request interpretation",
        "Intent + document type classification", 
        "Confidence-based smart defaults",
        "Elimination of clarification requests"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = """
        You are a Document Processing Intent Expert that excels at understanding vague user requests.

        ANALYZE USER REQUESTS COMPREHENSIVELY:
        - Parse subtle intent from vague language ("help with this thing")
        - Consider document content and structure for type classification
        - Use context clues and common user behavior patterns
        - Provide confidence scoring for transparency

        INTENT CLASSIFICATION:
        1. **INFORMATION_REQUEST** - User wants to know document content:
           - "what is this", "tell me about", "explain this", "show me what's in"
           - Clear questions about document content
           
        2. **PROCESSING_REQUEST** - User wants document enhancement/processing:
           - "help me with", "fix this", "improve", "create from this", "process"
           - Vague requests with action implications
           - Default assumption for ambiguous cases

        DOCUMENT TYPE DETECTION:
        - **CV/RESUME**: Personal info, work history, skills, education sections
        - **GENERAL**: Reports, specifications, articles, technical documents

        VAGUE REQUEST PATTERNS:
        - "help me with this resume" → Process CV (0.85 confidence)
        - "do something with this document" → Process General (0.6 confidence)
        - "this thing needs work" → Process General (0.7 confidence)  
        - "what's in here?" → Information request (0.9 confidence)
        - "make this better" → Process (0.8 confidence)

        CONFIDENCE SCORING:
        - 0.9+: Very clear intent and document type
        - 0.7-0.9: Clear with minor ambiguity
        - 0.5-0.7: Some ambiguity but reasonable inference
        - 0.3-0.5: High ambiguity, using smart defaults
        - <0.3: Extreme ambiguity, default to processing

        SMART DEFAULTS STRATEGY:
        - When in doubt, assume PROCESSING_REQUEST (users typically want action)
        - Use document content to determine CV vs GENERAL type
        - Never return "unclear" - always provide best analysis
        - Explain reasoning transparently

        RESPONSE FORMAT (JSON only):
        {
            "intent": "INFORMATION_REQUEST" | "PROCESSING_REQUEST",
            "document_type": "CV" | "GENERAL",
            "confidence": 0.85,
            "reasoning": "Detailed explanation of decision factors and ambiguity handling",
            "action": "quick_summary" | "process_cv" | "process_general",
            "ambiguity_level": "low" | "medium" | "high",
            "fallback_used": false,
            "user_question_extracted": "What the user actually wants"
        }

        EXAMPLES:
        User: "help me with this resume thing"
        Analysis: Vague but "help" suggests action, "resume" indicates CV type
        Response: {intent: "PROCESSING_REQUEST", document_type: "CV", confidence: 0.8}

        User: "what's this document about?"
        Analysis: Clear information request, document type from content
        Response: {intent: "INFORMATION_REQUEST", document_type: "GENERAL", confidence: 0.9}

        User: "this needs work"
        Analysis: Vague but implies improvement needed
        Response: {intent: "PROCESSING_REQUEST", document_type: "GENERAL", confidence: 0.6}
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, user_input: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Comprehensive intent analysis with document content consideration"""
        try:
            document_content = context_metadata.get("document_content", "") if context_metadata else ""
            conversation_context = context_metadata.get("has_previous_document", False) if context_metadata else False
            
            # Build comprehensive analysis prompt
            analysis_prompt = f"""
            COMPREHENSIVE INTENT ANALYSIS:
            
            USER REQUEST: "{user_input}"
            DOCUMENT PREVIEW: "{document_content[:800]}..."
            CONVERSATION CONTEXT: {"User has previous document" if conversation_context else "New document upload"}
            
            Analyze this request considering:
            1. User's language patterns and implied intent (even if vague)
            2. Document content structure and type indicators
            3. Context from conversation flow
            4. Common user behavior patterns for similar requests
            5. Confidence in your assessment
            
            Handle ambiguity intelligently:
            - If user language is vague, use document content clues
            - If document type is unclear, analyze content structure
            - If intent is ambiguous, default to processing with reasoning
            - Always provide your best analysis with confidence scoring
            
            CRITICAL: Never respond with "unclear" or "unknown". Always provide
            your best intelligent guess with transparent reasoning.
            """
            
            self.add_user_message(analysis_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            response_content = str(response.content) if hasattr(response, 'content') else str(response)
            self.add_assistant_message(response_content)
            
            # Enhance response with smart defaults if needed
            return self._apply_smart_enhancements(response_content, user_input, document_content)

        except Exception as e:
            print(f"Smart intent analysis error: {str(e)}")
            # Enhanced fallback with better defaults
            return self._create_smart_fallback(user_input, document_content)

    def _apply_smart_enhancements(self, ai_response: str, user_input: str, document_content: str) -> str:
        """Apply smart defaults and enhancements to AI response"""
        try:
            # Clean and parse JSON response
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(ai_response)
            
            # Apply confidence-based enhancements
            confidence = result.get("confidence", 0.5)
            
            if confidence < 0.5:
                # Low confidence - apply smart defaults
                result["fallback_used"] = True
                result["ambiguity_level"] = "high"
                
                # Smart document type detection from content
                if any(indicator in document_content.lower() for indicator in 
                      ["resume", "cv", "experience", "education", "skills", "work history"]):
                    result["document_type"] = "CV"
                    result["action"] = "process_cv"
                else:
                    result["document_type"] = "GENERAL"
                    result["action"] = "process_general"
                
                # Default to processing for vague requests
                result["intent"] = "PROCESSING_REQUEST"
                result["reasoning"] += " | Applied smart defaults for ambiguous request"
            
            elif confidence < 0.7:
                # Medium confidence - minor enhancements
                result["ambiguity_level"] = "medium"
                result["fallback_used"] = False
            
            else:
                # High confidence - use as-is
                result["ambiguity_level"] = "low"
                result["fallback_used"] = False
            
            return json.dumps(result, indent=2)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Enhancement error: {str(e)}")
            return self._create_smart_fallback(user_input, document_content)

    def _create_smart_fallback(self, user_input: str, document_content: str) -> str:
        """Create intelligent fallback when AI analysis fails"""
        user_lower = user_input.lower()
        
        # Determine intent from patterns
        if any(word in user_lower for word in ["what", "tell", "explain", "show", "describe"]):
            intent = "INFORMATION_REQUEST"
            action = "quick_summary"
            confidence = 0.7
            reasoning = "Fallback: Question words indicate information request"
        else:
            intent = "PROCESSING_REQUEST"
            confidence = 0.6
            reasoning = "Fallback: Default to processing for ambiguous requests"
            
            # Determine document type and action
            if any(indicator in document_content.lower() for indicator in 
                  ["resume", "cv", "experience", "education", "skills"]):
                document_type = "CV"
                action = "process_cv"
            else:
                document_type = "GENERAL"
                action = "process_general"
        
        return json.dumps({
            "intent": intent,
            "document_type": document_type if intent == "PROCESSING_REQUEST" else "GENERAL",
            "confidence": confidence,
            "reasoning": reasoning,
            "action": action,
            "ambiguity_level": "high",
            "fallback_used": True,
            "user_question_extracted": user_input
        }, indent=2)
