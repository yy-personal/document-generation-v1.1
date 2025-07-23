"""
PowerPoint Generation Orchestrator - Fixed conversation context handling
"""
import json
import uuid
import base64
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from config import *

class PowerPointOrchestrator:
    """Orchestrator for PowerPoint generation with fixed context handling"""

    def __init__(self):
        self.agent_instances = {}

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        date_part = datetime.utcnow().strftime(SESSION_ID_DATE_FORMAT)
        unique_part = str(uuid.uuid4()).replace('-', '')[:SESSION_ID_UNIQUE_LENGTH].upper()
        return f"{SESSION_ID_PREFIX}{date_part}{unique_part}"

    def _parse_document_extraction(self, user_message: str) -> tuple:
        """Parse user message to extract document content and user input"""
        if '[pdf_extraction]' in user_message:
            parts = user_message.split('[pdf_extraction]', 1)
            user_input = parts[0].strip() if parts[0].strip() else None
            document_content = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
            return document_content, user_input, "pdf"
        
        elif '[word_document_extraction]' in user_message:
            parts = user_message.split('[word_document_extraction]', 1)
            user_input = parts[0].strip() if parts[0].strip() else None
            document_content = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
            return document_content, user_input, "word"
        
        return None, user_message, None

    def _extract_document_from_conversation_history(self, conversation: List[dict]) -> Tuple[Optional[str], Optional[str]]:
        """Extract the most recent document from conversation history"""
        for message in reversed(conversation):
            if message.get("role") == "user":
                content = message.get("content", "")
                
                if '[pdf_extraction]' in content:
                    parts = content.split('[pdf_extraction]', 1)
                    if len(parts) > 1 and parts[1].strip():
                        return parts[1].strip(), "pdf"
                
                elif '[word_document_extraction]' in content:
                    parts = content.split('[word_document_extraction]', 1)
                    if len(parts) > 1 and parts[1].strip():
                        return parts[1].strip(), "word"
        
        return None, None

    def _is_continuation_request(self, user_message: str, conversation: List[dict]) -> bool:
        """Enhanced continuation request detection"""
        continuation_keywords = [
            "create", "generate", "make", "build", "produce", "presentation",
            "slides", "powerpoint", "ppt", "show", "present", "convert",
            "transform", "turn into", "export", "output",
            "the document", "this document", "the file", "this file",
            "it", "this", "that", "from this", "based on", "proceed"
        ]
        
        user_lower = user_message.lower()
        has_continuation_keywords = any(keyword in user_lower for keyword in continuation_keywords)
        has_previous_document = self._extract_document_from_conversation_history(conversation)[0] is not None
        
        # Additional check: if user message is short and has action words, likely continuation
        is_short_action_request = (
            len(user_message.split()) <= 10 and 
            any(action in user_lower for action in ["create", "make", "generate", "show", "convert"])
        )
        
        return (has_continuation_keywords or is_short_action_request) and has_previous_document

    def _get_agent(self, agent_name: str):
        """Get or create agent instance using lazy loading"""
        if agent_name not in self.agent_instances:
            try:
                if agent_name == "SmartPresentationProcessor":
                    from agents.smart_presentation_processor_skill import SmartPresentationProcessor
                    self.agent_instances[agent_name] = SmartPresentationProcessor()
                elif agent_name == "DocumentContentExtractor":
                    from agents.document_content_extractor_skill import DocumentContentExtractor
                    self.agent_instances[agent_name] = DocumentContentExtractor()
                elif agent_name == "PresentationStructureAgent":
                    from agents.presentation_structure_agent import PresentationStructureAgent
                    self.agent_instances[agent_name] = PresentationStructureAgent()
                elif agent_name == "SlideContentGenerator":
                    from agents.slide_content_generator import SlideContentGenerator
                    self.agent_instances[agent_name] = SlideContentGenerator()
                elif agent_name == "PowerPointBuilderAgent":
                    from agents.powerpoint_builder_agent import PowerPointBuilderAgent
                    self.agent_instances[agent_name] = PowerPointBuilderAgent()
            except ImportError as e:
                print(f"Warning: Could not load {agent_name}: {e}")
                return None
        
        return self.agent_instances.get(agent_name)

    async def _analyze_presentation_intent(self, user_input: str, document_content: str, has_previous_document: bool = False) -> Dict[str, Any]:
        """Step 1: Analyze intent and determine slide count"""
        try:
            smart_processor = self._get_agent("SmartPresentationProcessor")
            if not smart_processor:
                raise Exception("SmartPresentationProcessor not available")
            
            context_metadata = {
                "document_content": document_content,
                "has_previous_document": has_previous_document
            }
            
            analysis_result = await smart_processor.process(user_input, context_metadata)
            
            if analysis_result.startswith('```json'):
                analysis_result = analysis_result.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(analysis_result)
            
            # Ensure required fields
            required_fields = ["intent", "confidence", "estimated_slides"]
            for field in required_fields:
                if field not in result:
                    if field == "intent":
                        result[field] = "CREATE_PRESENTATION"
                    elif field == "confidence":
                        result[field] = 0.7
                    elif field == "estimated_slides":
                        result[field] = 12
            
            return result
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Presentation analysis error: {str(e)}")
            return self._create_presentation_fallback(user_input, document_content)

    def _create_presentation_fallback(self, user_input: str, document_content: str) -> Dict[str, Any]:
        """Create intelligent fallback for presentation analysis"""
        return {
            "intent": "CREATE_PRESENTATION",
            "confidence": 0.6,
            "reasoning": "Fallback analysis - generating standard business presentation",
            "estimated_slides": 12,
            "fallback_used": True
        }

    async def _extract_document_content(self, content: str) -> str:
        """Step 2: Extract and organize document content"""
        try:
            extractor = self._get_agent("DocumentContentExtractor")
            if not extractor:
                return content
                
            return await extractor.process(content)
            
        except Exception as e:
            print(f"Content extraction error: {str(e)}")
            return content

    async def _create_presentation_structure(self, extracted_content: str, target_slides: int) -> str:
        """Step 3: Create slide structure and outline"""
        try:
            structure_agent = self._get_agent("PresentationStructureAgent")
            if not structure_agent:
                return extracted_content
                
            context_metadata = {"target_slides": target_slides}
            return await structure_agent.process(extracted_content, context_metadata)
            
        except Exception as e:
            print(f"Structure creation error: {str(e)}")
            return extracted_content

    async def _generate_slide_content(self, structure: str) -> str:
        """Step 4: Generate detailed slide content"""
        try:
            content_generator = self._get_agent("SlideContentGenerator")
            if not content_generator:
                return structure
                
            return await content_generator.process(structure)
            
        except Exception as e:
            print(f"Content generation error: {str(e)}")
            return structure

    async def _build_powerpoint_file(self, slide_content: str, session_id: str) -> bytes:
        """Step 5: Build actual PowerPoint file (rule-based)"""
        try:
            builder_agent = self._get_agent("PowerPointBuilderAgent")
            if not builder_agent:
                raise Exception("PowerPointBuilderAgent not available")
                
            context_metadata = {"session_id": session_id}
            ppt_data = await builder_agent.process(slide_content, context_metadata)
            
            # Convert to bytes if needed
            if isinstance(ppt_data, str):
                return base64.b64decode(ppt_data)
            return ppt_data
            
        except Exception as e:
            print(f"PowerPoint building error: {str(e)}")
            raise Exception(f"Failed to generate PowerPoint file: {str(e)}")

    def _provide_capabilities_info(self) -> str:
        """Provide information about PowerPoint generation capabilities"""
        return """I can create professional PowerPoint presentations from your documents.

**Features:**
• 12-slide business presentations with company branding
• Intelligent content organization and summarization
• Clean slide layouts with proper formatting
• Support for PDF and Word document input

Upload a document and I'll create a professional presentation automatically."""

    def _build_response(self, session_id: str, status: str, conversation: List[dict], **kwargs) -> Dict[str, Any]:
        """Build standardized API response"""
        response_data = {
            "status": status,
            "session_id": session_id,
            "conversation_history": conversation,
            "processing_info": kwargs.get("processing_info", {}),
            "pipeline_info": kwargs.get("pipeline_info", [])
        }
        
        if "powerpoint_output" in kwargs:
            response_data["powerpoint_output"] = kwargs["powerpoint_output"]
            
        if status == "error" and "error_message" in kwargs:
            response_data["error_message"] = kwargs["error_message"]
            
        return {"response_data": response_data}

    async def process_conversation_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for PowerPoint generation requests"""
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
                    print("Detected continuation request - looking for previous document...")
                    document_content, file_type = self._extract_document_from_conversation_history(conversation)
                    clean_user_input = user_message
                    
                    if document_content:
                        print(f"Found previous {file_type} document in conversation history")
                    else:
                        print("No previous document found in conversation history")

            if document_content:
                # POWERPOINT GENERATION PIPELINE
                print(f"Processing {file_type} document for PowerPoint generation...")
                
                has_previous_document = document_content != self._parse_document_extraction(user_message)[0]
                
                # Handle direct document upload without user text
                if clean_user_input is None:
                    clean_user_input = "Create a professional presentation from this document"
                
                # STEP 1: Intent analysis and slide count optimization
                analysis_result = await self._analyze_presentation_intent(
                    clean_user_input, 
                    document_content, 
                    has_previous_document
                )
                
                user_intent = analysis_result.get("intent", "CREATE_PRESENTATION")
                estimated_slides = analysis_result.get("estimated_slides", 12)
                # Apply max slide limit
                max_slides = min(estimated_slides, 15)
                
                if user_intent == "INFORMATION_REQUEST":
                    # Provide capabilities information
                    info_response = self._provide_capabilities_info()
                    conversation.append({"role": "assistant", "content": info_response})
                    
                    pipeline_info = get_quick_response_pipeline()
                    
                    return self._build_response(session_id, "completed", conversation,
                                              processing_info={
                                                  "intent": analysis_result,
                                                  "file_type": file_type,
                                                  "response_type": "capabilities_info",
                                                  "context_source": "previous_conversation" if has_previous_document else "current_message"
                                              },
                                              pipeline_info=pipeline_info)
                
                elif user_intent == "CREATE_PRESENTATION":
                    # Full PowerPoint generation pipeline
                    print(f"Generating presentation with {max_slides} slides (limited from {estimated_slides})")
                    
                    # STEP 2: Extract and organize content
                    extracted_content = await self._extract_document_content(document_content)
                    
                    # STEP 3: Create presentation structure
                    presentation_structure = await self._create_presentation_structure(
                        extracted_content, max_slides)
                    
                    # STEP 4: Generate detailed slide content
                    slide_content = await self._generate_slide_content(presentation_structure)
                    
                    # STEP 5: Build PowerPoint file
                    ppt_bytes = await self._build_powerpoint_file(slide_content, session_id)
                    ppt_base64 = base64.b64encode(ppt_bytes).decode('utf-8')
                    
                    # Build response message
                    if has_previous_document:
                        response_text = f"I've created a presentation from the {file_type.upper()} document as requested. "
                    else:
                        response_text = f"I've created a professional business presentation from your {file_type.upper()} document. "
                    
                    response_text += f"The presentation contains {max_slides} slides with company branding and clean formatting."
                    
                    conversation.append({"role": "assistant", "content": response_text})
                    
                    # Generate pipeline info
                    pipeline_info = get_complete_pipeline()
                    
                    return self._build_response(session_id, "completed", conversation,
                                              processing_info={
                                                  "intent": analysis_result,
                                                  "max_slides": max_slides,
                                                  "estimated_slides": estimated_slides,
                                                  "file_type": file_type,
                                                  "response_type": "powerpoint_generation",
                                                  "context_source": "previous_conversation" if has_previous_document else "current_message"
                                              },
                                              pipeline_info=pipeline_info,
                                              powerpoint_output={
                                                  "ppt_data": ppt_base64,
                                                  "filename": f"presentation_{session_id}.pptx"
                                              })
                
                else:
                    # Clarification needed (rare with smart processor)
                    clarification_response = f"I can see you've uploaded a {file_type.upper()} document. Would you like me to create a presentation from it?"
                    
                    conversation.append({"role": "assistant", "content": clarification_response})
                    
                    return self._build_response(session_id, "needs_clarification", conversation,
                                              processing_info={
                                                  "intent": analysis_result,
                                                  "file_type": file_type,
                                                  "response_type": "clarification_request",
                                                  "context_source": "previous_conversation" if has_previous_document else "current_message"
                                              })
            
            else:
                # No document found - provide guidance
                if any(keyword in user_message.lower() for keyword in ["presentation", "powerpoint", "slides", "ppt"]):
                    response_text = "Please upload a PDF or Word document to create a presentation from. I can generate professional PowerPoint presentations with company branding."
                else:
                    response_text = self._provide_capabilities_info()
                
                conversation.append({"role": "assistant", "content": response_text})
                
                return self._build_response(session_id, "waiting_for_file", conversation)
        
        except Exception as e:
            error_message = f"PowerPoint generation error: {str(e)}"
            print(f"PowerPoint Orchestrator Error: {error_message}")
            
            conversation.append({"role": "assistant", "content": "I encountered an error generating your presentation. Please try again or upload a different document."})
            
            return self._build_response(session_id, "error", conversation,
                                      error_message=error_message)