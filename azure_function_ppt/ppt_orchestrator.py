"""
PowerPoint Generation Orchestrator - Refactored architecture
"""
import json
import uuid
import base64
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from config import *

class PowerPointOrchestrator:
    """Orchestrator with refactored agent architecture"""

    def __init__(self):
        self.agent_instances = {}

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        date_part = datetime.utcnow().strftime(SESSION_ID_DATE_FORMAT)
        unique_part = str(uuid.uuid4()).replace('-', '')[:SESSION_ID_UNIQUE_LENGTH].upper()
        return f"{SESSION_ID_PREFIX}{date_part}{unique_part}"

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

    async def _analyze_intent(self, user_input: str, has_previous_document: bool = False) -> Dict[str, Any]:
        """Step 1: Intent analysis only"""
        try:
            smart_processor = self._get_agent("SmartPresentationProcessor")
            if not smart_processor:
                raise Exception("SmartPresentationProcessor not available")
            
            context_metadata = {"has_previous_document": has_previous_document}
            analysis_result = await smart_processor.process(user_input, context_metadata)
            
            if analysis_result.startswith('```json'):
                analysis_result = analysis_result.replace('```json', '').replace('```', '').strip()
            
            return json.loads(analysis_result)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Intent analysis error: {str(e)}")
            return {"intent": "CREATE_PRESENTATION", "confidence": 0.6, "reasoning": "Fallback"}

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

    async def _create_presentation_structure(self, extracted_content: str) -> Dict[str, Any]:
        """Step 3: Content analysis + slide planning + structure creation"""
        try:
            structure_agent = self._get_agent("PresentationStructureAgent")
            if not structure_agent:
                raise Exception("PresentationStructureAgent not available")
                
            structure_result = await structure_agent.process(extracted_content)
            
            if structure_result.startswith('```json'):
                structure_result = structure_result.replace('```json', '').replace('```', '').strip()
            
            return json.loads(structure_result)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Structure creation error: {str(e)}")
            return {
                "slide_planning": {"optimal_slides": PRESENTATION_CONFIG['default_slides']},
                "presentation_structure": []
            }

    async def _generate_slide_content(self, structure_data: Dict[str, Any]) -> str:
        """Step 4: Generate detailed slide content"""
        try:
            content_generator = self._get_agent("SlideContentGenerator")
            if not content_generator:
                return json.dumps(structure_data.get("presentation_structure", []))
                
            structure_json = json.dumps(structure_data.get("presentation_structure", []))
            return await content_generator.process(structure_json)
            
        except Exception as e:
            print(f"Content generation error: {str(e)}")
            return json.dumps(structure_data.get("presentation_structure", []))

    async def _build_powerpoint_file(self, slide_content: str, session_id: str) -> bytes:
        """Step 5: Build actual PowerPoint file"""
        try:
            builder_agent = self._get_agent("PowerPointBuilderAgent")
            if not builder_agent:
                raise Exception("PowerPointBuilderAgent not available")
                
            context_metadata = {"session_id": session_id}
            ppt_data = await builder_agent.process(slide_content, context_metadata)
            
            if isinstance(ppt_data, str):
                return base64.b64decode(ppt_data)
            return ppt_data
            
        except Exception as e:
            print(f"PowerPoint building error: {str(e)}")
            raise Exception(f"Failed to generate PowerPoint file: {str(e)}")

    def _provide_capabilities_info(self) -> str:
        """Provide capabilities information"""
        return """I can create professional PowerPoint presentations from your documents.

**Features:**
• Business presentations with company branding
• Intelligent content organization and summarization
• Clean slide layouts with proper formatting
• Support for PDF and Word document input
• Maximum {max_slides} slides with optimal content distribution""".format(max_slides=get_max_slides())

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
        """Main entry point - refactored pipeline"""
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
                    print("Detected continuation request")
                    document_content, file_type = self._extract_document_from_conversation_history(conversation)
                    clean_user_input = user_message
                    
                    if document_content:
                        print(f"Found previous {file_type} document")

            if document_content:
                has_previous_document = document_content != self._parse_document_extraction(user_message)[0]
                
                if clean_user_input is None:
                    clean_user_input = "Create a professional presentation from this document"
                
                # STEP 1: Intent analysis only (no slide count)
                intent_result = await self._analyze_intent(clean_user_input, has_previous_document)
                user_intent = intent_result.get("intent", "CREATE_PRESENTATION")
                
                if user_intent == "INFORMATION_REQUEST":
                    info_response = self._provide_capabilities_info()
                    conversation.append({"role": "assistant", "content": info_response})
                    
                    return self._build_response(session_id, "completed", conversation,
                                              processing_info={
                                                  "intent": intent_result,
                                                  "file_type": file_type,
                                                  "response_type": "capabilities_info"
                                              },
                                              pipeline_info=get_quick_response_pipeline())
                
                elif user_intent == "CREATE_PRESENTATION":
                    print("Starting PowerPoint generation pipeline")
                    
                    # STEP 2: Extract and organize content
                    extracted_content = await self._extract_document_content(document_content)
                    
                    # STEP 3: Content analysis + slide planning + structure (NEW COMBINED STEP)
                    structure_data = await self._create_presentation_structure(extracted_content)
                    
                    optimal_slides = structure_data.get("slide_planning", {}).get("optimal_slides", PRESENTATION_CONFIG['default_slides'])
                    print(f"Optimal slides determined: {optimal_slides} (max: {get_max_slides()})")
                    
                    # STEP 4: Generate detailed slide content
                    slide_content = await self._generate_slide_content(structure_data)
                    
                    # STEP 5: Build PowerPoint file
                    ppt_bytes = await self._build_powerpoint_file(slide_content, session_id)
                    ppt_base64 = base64.b64encode(ppt_bytes).decode('utf-8')
                    
                    response_text = f"I've created a professional business presentation from your {file_type.upper()} document. The presentation contains {optimal_slides} slides with company branding and clean formatting."
                    conversation.append({"role": "assistant", "content": response_text})
                    
                    # --- FIX START ---
                    # For easier debugging, add the final JSON content to the response.
                    # First, try to parse the JSON string from the generator into a Python object.
                    try:
                        powerpoint_json_content = json.loads(slide_content)
                    except (json.JSONDecodeError, TypeError):
                        # If it fails (e.g., it's not valid JSON), just keep the raw string.
                        powerpoint_json_content = slide_content
                    
                    # Now, build the processing_info dictionary with the new debug key.
                    processing_info = {
                        "intent": intent_result,
                        "structure_analysis": structure_data.get("content_analysis", {}),
                        "slide_planning": structure_data.get("slide_planning", {}),
                        "powerpoint_json_content": powerpoint_json_content, # The new debugging key
                        "file_type": file_type,
                        "response_type": "powerpoint_generation"
                    }
                    
                    # Finally, build the final response using this complete info dictionary.
                    return self._build_response(
                        session_id, 
                        "completed", 
                        conversation,
                        processing_info=processing_info,
                        pipeline_info=get_complete_pipeline(),
                        powerpoint_output={
                            "ppt_data": ppt_base64,
                            "filename": f"presentation_{session_id}.pptx"
                        }
                    )
                    # --- FIX END ---
            
            else:
                # No document found
                if any(keyword in user_message.lower() for keyword in ["presentation", "powerpoint", "slides", "ppt"]):
                    response_text = f"Please upload a PDF or Word document to create a presentation from. I can generate professional PowerPoint presentations up to {get_max_slides()} slides with company branding."
                else:
                    response_text = self._provide_capabilities_info()
                
                conversation.append({"role": "assistant", "content": response_text})
                return self._build_response(session_id, "waiting_for_file", conversation)
        
        except Exception as e:
            error_message = f"PowerPoint generation error: {str(e)}"
            print(f"PowerPoint Orchestrator Error: {error_message}")
            
            conversation.append({"role": "assistant", "content": "I encountered an error generating your presentation. Please try again or upload a different document."})
            
            return self._build_response(session_id, "error", conversation, error_message=error_message)