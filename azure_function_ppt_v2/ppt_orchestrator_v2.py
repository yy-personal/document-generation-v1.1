"""
PowerPoint Generation Orchestrator V2 - Pandoc + Markdown Architecture
"""
import json
import uuid
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from agents.markdown_presentation_agent import MarkdownPresentationAgent
from utils.pandoc_converter import PandocConverter
from config import SESSION_ID_PREFIX, SESSION_ID_DATE_FORMAT, SESSION_ID_UNIQUE_LENGTH

class PPTOrchestratorV2:
    """Orchestrator using Pandoc + Markdown approach for consistent presentations"""

    def __init__(self):
        self.markdown_agent = MarkdownPresentationAgent()
        self.pandoc_converter = PandocConverter()
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        date_part = datetime.utcnow().strftime(SESSION_ID_DATE_FORMAT)
        unique_part = str(uuid.uuid4()).replace('-', '')[:SESSION_ID_UNIQUE_LENGTH].upper()
        return f"{SESSION_ID_PREFIX}_V2_{date_part}{unique_part}"

    def _parse_document_extraction(self, user_message: str) -> tuple:
        """Parse user message to extract document content and user input"""
        # Support only the simplified document tag for best quality
        if '[document]' in user_message:
            parts = user_message.split('[document]', 1)
            user_input = parts[0].strip() if parts[0].strip() else None
            document_content = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
            return document_content, user_input, "document"
        
        return None, user_message, None

    def _extract_document_from_conversation_history(self, conversation: List[dict]) -> Tuple[Optional[str], Optional[str]]:
        """Extract the most recent document from conversation history"""
        for message in reversed(conversation):
            if message.get("role") == "user":
                content = message.get("content", "")
                
                # Only support the document tag
                if '[document]' in content:
                    parts = content.split('[document]', 1)
                    if len(parts) > 1 and parts[1].strip():
                        return parts[1].strip(), "document"
        
        return None, None

    def _is_continuation_request(self, user_message: str, conversation: List[dict]) -> bool:
        """Enhanced continuation request detection"""
        continuation_keywords = [
            "create", "generate", "make", "build", "produce", "presentation",
            "slides", "powerpoint", "ppt", "show", "present", "convert",
            "transform", "turn into", "export", "output", "proceed",
            "the document", "this document", "the file", "this file",
            "it", "this", "that", "from this", "based on"
        ]
        
        user_lower = user_message.lower()
        has_continuation_keywords = any(keyword in user_lower for keyword in continuation_keywords)
        has_previous_document = self._extract_document_from_conversation_history(conversation)[0] is not None
        
        is_short_action_request = (
            len(user_message.split()) <= 10 and 
            any(action in user_lower for action in ["create", "make", "generate", "show", "convert", "proceed"])
        )
        
        return (has_continuation_keywords or is_short_action_request) and has_previous_document

    async def _analyze_intent(self, user_input: str, has_previous_document: bool = False) -> Dict[str, Any]:
        """Simple intent analysis for V2"""
        # Simplified intent analysis - focus on CREATE_PRESENTATION vs INFORMATION_REQUEST
        user_lower = user_input.lower()
        
        presentation_keywords = [
            "create", "generate", "make", "build", "produce", "presentation",
            "slides", "powerpoint", "ppt", "show", "present"
        ]
        
        info_keywords = [
            "what", "how", "can you", "help", "info", "explain", "tell me"
        ]
        
        if any(keyword in user_lower for keyword in presentation_keywords) or has_previous_document:
            return {
                "intent": "CREATE_PRESENTATION",
                "confidence": 0.9,
                "reasoning": "User requested presentation creation or has document context"
            }
        elif any(keyword in user_lower for keyword in info_keywords):
            return {
                "intent": "INFORMATION_REQUEST", 
                "confidence": 0.8,
                "reasoning": "User asking for information or capabilities"
            }
        else:
            return {
                "intent": "CREATE_PRESENTATION",
                "confidence": 0.7,
                "reasoning": "Default to presentation creation"
            }

    async def _generate_markdown_presentation(self, document_content: str) -> str:
        """Generate markdown presentation using the agent"""
        try:
            print(f"[V2 STEP 1] Generating markdown presentation - Input length: {len(document_content)} chars")
            
            markdown_content = await self.markdown_agent.process(document_content)
            
            # Validate the markdown
            validation = self.pandoc_converter.validate_markdown(markdown_content)
            print(f"[V2 STEP 1] Markdown validation - Valid: {validation['is_valid']}, Slides: {validation['slide_count']}")
            
            if validation['warnings']:
                print(f"[V2 STEP 1] Warnings: {validation['warnings']}")
            
            return markdown_content
            
        except Exception as e:
            print(f"[V2 STEP 1] Markdown generation error: {str(e)}")
            raise Exception(f"Failed to generate markdown presentation: {str(e)}")

    async def _convert_to_powerpoint(self, markdown_content: str, session_id: str) -> bytes:
        """Convert markdown to PowerPoint using Pandoc"""
        try:
            print(f"[V2 STEP 2] Converting markdown to PowerPoint - Session: {session_id}")
            
            # Use session ID for debug filename
            debug_filename = f"presentation_{session_id}.pptx"
            
            ppt_bytes = self.pandoc_converter.markdown_to_pptx(
                markdown_content, 
                output_filename=debug_filename
            )
            
            print(f"[V2 STEP 2] PowerPoint conversion complete - Size: {len(ppt_bytes)} bytes")
            return ppt_bytes
            
        except Exception as e:
            print(f"[V2 STEP 2] PowerPoint conversion error: {str(e)}")
            raise Exception(f"Failed to convert to PowerPoint: {str(e)}")

    def _provide_capabilities_info(self) -> str:
        """Provide V2 capabilities information"""
        template_info = self.pandoc_converter.get_template_info()
        
        return f"""I can create professional PowerPoint presentations from your documents using an improved V2 system.

**V2 Features:**
• Pandoc-based conversion for better template compatibility
• Markdown-driven content generation for consistency
• Native table support with proper formatting
• Company template integration: {'✓ Active' if template_info['template_exists'] else '✗ Default template'}
• Simplified agent architecture for reliable output

**Supported Input:**
• PDF and Word documents via [document] tag
• Conversational requests for presentation creation

**Output:**
• Professional PowerPoint presentations (.pptx)
• Template-aware formatting and branding
• Structured business presentation flow"""

    def _build_response(self, session_id: str, status: str, conversation: List[dict], **kwargs) -> Dict[str, Any]:
        """Build standardized API response"""
        response_data = {
            "status": status,
            "session_id": session_id,
            "conversation_history": conversation,
            "processing_info": kwargs.get("processing_info", {}),
            "system_version": "V2_Pandoc_Markdown"
        }
        
        if "powerpoint_output" in kwargs:
            response_data["powerpoint_output"] = kwargs["powerpoint_output"]
            
        if status == "error" and "error_message" in kwargs:
            response_data["error_message"] = kwargs["error_message"]
            
        return {"response_data": response_data}

    async def process_conversation_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point - V2 pipeline using Pandoc + Markdown"""
        session_id = request.get('session_id', self._generate_session_id())
        conversation = request.get('conversation_history', [])
        user_message = request.get('user_message', '').strip()
        
        if not user_message:
            return self._build_response(session_id, "error", conversation,
                                      error_message="User message required")
        
        try:
            conversation.append({"role": "user", "content": user_message})
            
            # Parse document extraction from current message
            document_content, clean_user_input, file_type = self._parse_document_extraction(user_message)
            
            # Check for continuation requests if no current document
            if not document_content:
                if self._is_continuation_request(user_message, conversation):
                    print("V2: Detected continuation request")
                    document_content, file_type = self._extract_document_from_conversation_history(conversation)
                    clean_user_input = user_message
                    
                    if document_content:
                        print(f"V2: Found previous {file_type} document")

            if document_content:
                print(f"[V2 PIPELINE] Document detected - Length: {len(document_content)} chars, Type: {file_type}")
                has_previous_document = document_content != self._parse_document_extraction(user_message)[0]
                
                if clean_user_input is None:
                    clean_user_input = "Create a professional presentation from this document"
                    
                print(f"[V2 PIPELINE] User input: '{clean_user_input}'")
                
                # Simple intent analysis
                intent_result = await self._analyze_intent(clean_user_input, has_previous_document)
                print(f"[V2 PIPELINE] Intent determined: {intent_result.get('intent', 'UNKNOWN')}")
                user_intent = intent_result.get("intent", "CREATE_PRESENTATION")
                
                if user_intent == "INFORMATION_REQUEST":
                    info_response = self._provide_capabilities_info()
                    conversation.append({"role": "assistant", "content": info_response})
                    
                    return self._build_response(session_id, "completed", conversation,
                                              processing_info={
                                                  "intent": intent_result,
                                                  "file_type": file_type,
                                                  "response_type": "capabilities_info"
                                              })
                
                elif user_intent == "CREATE_PRESENTATION":
                    print("V2: Starting PowerPoint generation pipeline")
                    
                    # V2 STEP 1: Generate markdown presentation
                    markdown_content = await self._generate_markdown_presentation(document_content)
                    
                    # V2 STEP 2: Convert markdown to PowerPoint
                    ppt_bytes = await self._convert_to_powerpoint(markdown_content, session_id)
                    ppt_base64 = base64.b64encode(ppt_bytes).decode('utf-8')
                    
                    # Count slides from markdown for response
                    slide_count = markdown_content.count('\n## ') + (1 if markdown_content.startswith('# ') else 0)
                    
                    response_text = f"I've created a professional business presentation from your {file_type.upper()} document using the improved V2 system. The presentation contains {slide_count} slides with template-based formatting and enhanced consistency."
                    conversation.append({"role": "assistant", "content": response_text})
                    
                    return self._build_response(
                        session_id, 
                        "completed", 
                        conversation,
                        processing_info={
                            "intent": intent_result,
                            "file_type": file_type,
                            "slide_count": slide_count,
                            "markdown_length": len(markdown_content),
                            "template_used": self.pandoc_converter.template_path is not None,
                            "response_type": "powerpoint_generation",
                            "processing_method": "pandoc_markdown"
                        },
                        powerpoint_output={
                            "ppt_data": ppt_base64,
                            "filename": f"presentation_v2_{session_id}.pptx"
                        }
                    )
            
            else:
                # No document found
                if any(keyword in user_message.lower() for keyword in ["presentation", "powerpoint", "slides", "ppt"]):
                    response_text = "Please upload a PDF or Word document to create a presentation from. I can generate professional PowerPoint presentations using the improved V2 system with better template compatibility."
                else:
                    response_text = self._provide_capabilities_info()
                
                conversation.append({"role": "assistant", "content": response_text})
                return self._build_response(session_id, "waiting_for_file", conversation)
        
        except Exception as e:
            error_message = f"V2 PowerPoint generation error: {str(e)}"
            print(f"V2 PowerPoint Orchestrator Error: {error_message}")
            
            conversation.append({"role": "assistant", "content": "I encountered an error generating your presentation with the V2 system. Please try again or upload a different document."})
            
            return self._build_response(session_id, "error", conversation, error_message=error_message)