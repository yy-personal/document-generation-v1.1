"""
PDF Processing Orchestrator - Consolidated for single AI routing call
"""
import json
import uuid
import base64
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from config import *

class PDFOrchestrator:
    """Consolidated orchestrator with single AI call for routing decisions"""

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
            user_input = parts[0].strip() if parts[0].strip() else None  # No default question
            document_content = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
            return document_content, user_input, "pdf"
        
        elif '[word_document_extraction]' in user_message:
            parts = user_message.split('[word_document_extraction]', 1)
            user_input = parts[0].strip() if parts[0].strip() else None  # No default question
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
        """Check if user message is a continuation request referring to a previous document"""
        continuation_keywords = [
            "create", "generate", "make", "build", "produce",
            "summarize", "summary", "analyze", "process", "extract",
            "show me", "give me", "provide", 
            "the document", "this document", "the file", "this file",
            "it", "this", "that"
        ]
        
        user_lower = user_message.lower()
        has_continuation_keywords = any(keyword in user_lower for keyword in continuation_keywords)
        has_previous_document = self._extract_document_from_conversation_history(conversation)[0] is not None
        
        return has_continuation_keywords and has_previous_document

    def _get_agent(self, agent_name: str):
        """Get or create agent instance using lazy loading"""
        if agent_name not in self.agent_instances:
            try:
                if agent_name == "SmartIntentProcessor":
                    from agents.smart_intent_processor import SmartIntentProcessor
                    self.agent_instances[agent_name] = SmartIntentProcessor()
                elif agent_name == "DocumentQuickSummarySkill":
                    from agents.document_quick_summary_skill import DocumentQuickSummarySkill
                    self.agent_instances[agent_name] = DocumentQuickSummarySkill()
                elif agent_name == "CVAnalysisSkill":
                    from agents.cv_analysis_skill import CVAnalysisSkill
                    self.agent_instances[agent_name] = CVAnalysisSkill()
                elif agent_name == "DocumentExtractionSkill":
                    from agents.document_extraction_skill import DocumentExtractionSkill
                    self.agent_instances[agent_name] = DocumentExtractionSkill()
                elif agent_name == "MarkdownFormatterAgent":
                    from agents.markdown_formatter_agent import MarkdownFormatterAgent
                    self.agent_instances[agent_name] = MarkdownFormatterAgent()
            except ImportError as e:
                print(f"Warning: Could not load {agent_name}: {e}")
                return None
        
        return self.agent_instances.get(agent_name)

    async def _analyze_intent_and_classify(self, user_input: str, document_content: str, has_previous_document: bool = False) -> Dict[str, Any]:
        """CONSOLIDATED: Single AI call for intent analysis and document classification"""
        try:
            smart_processor = self._get_agent("SmartIntentProcessor")
            if not smart_processor:
                raise Exception("SmartIntentProcessor not available")
            
            context_metadata = {
                "document_content": document_content,
                "has_previous_document": has_previous_document
            }
            
            analysis_result = await smart_processor.process(user_input, context_metadata)
            
            if analysis_result.startswith('```json'):
                analysis_result = analysis_result.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(analysis_result)
            
            # Ensure all required fields are present
            required_fields = ["intent", "document_type", "confidence", "action"]
            for field in required_fields:
                if field not in result:
                    if field == "intent":
                        result[field] = "PROCESSING_REQUEST"
                    elif field == "document_type":
                        result[field] = "GENERAL"
                    elif field == "confidence":
                        result[field] = 0.6
                    elif field == "action":
                        result[field] = "process_general"
            
            return result
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Consolidated analysis error: {str(e)}")
            # Smart fallback that mimics old behavior
            return self._create_consolidated_fallback(user_input, document_content)

    def _create_consolidated_fallback(self, user_input: str, document_content: str) -> Dict[str, Any]:
        """Create intelligent fallback that preserves existing functionality"""
        user_lower = user_input.lower()
        
        # Intent detection (preserves old DocumentInputValidator logic)
        if any(word in user_lower for word in ["what", "tell", "explain", "show", "describe"]):
            intent = "INFORMATION_REQUEST"
            action = "quick_summary"
        else:
            intent = "PROCESSING_REQUEST"
            
            # Document type detection (preserves old DocumentClassifierAgent logic)
            if any(indicator in document_content.lower() for indicator in 
                  ["resume", "cv", "experience", "education", "skills", "work history"]):
                document_type = "CV"
                action = "process_cv"
            else:
                document_type = "GENERAL"
                action = "process_general"
        
        return {
            "intent": intent,
            "document_type": document_type if intent == "PROCESSING_REQUEST" else "GENERAL",
            "confidence": 0.6,
            "reasoning": "Fallback analysis using keyword patterns",
            "action": action,
            "fallback_used": True
        }

    async def _provide_quick_summary(self, content: str, user_question: str) -> str:
        """Provide quick document summary without full processing"""
        try:
            summary_skill = self._get_agent("DocumentQuickSummarySkill")
            if summary_skill:
                return await summary_skill.process(content, {"user_question": user_question})
            return f"I can see this document contains information about: {content[:200]}..."
            
        except Exception as e:
            print(f"Quick summary error: {str(e)}")
            return f"I can see this document, but encountered an error providing a summary: {str(e)}"

    async def _extract_document_content(self, content: str, document_type: str) -> str:
        """Extract document content based on type - no enhancement"""        
        if document_type == "CV":
            # Use CV analysis for resumes (includes future skills)
            cv_skill = self._get_agent("CVAnalysisSkill")
            if cv_skill:
                return await cv_skill.process(content, {"document_type": document_type})
        
        # Use simple extraction for general documents
        extraction_skill = self._get_agent("DocumentExtractionSkill")
        if extraction_skill:
            return await extraction_skill.process(content, {"document_type": document_type})
        
        return content  # Fallback if agents not available

    async def _format_to_markdown(self, processed_content: str, document_type: str) -> str:
        """Format processed content to clean markdown for PDF"""
        formatter = self._get_agent("MarkdownFormatterAgent")
        if formatter:
            return await formatter.process(processed_content, {"document_type": document_type})
        return processed_content

    async def _generate_pdf_from_markdown(self, markdown_content: str) -> bytes:
        """Generate PDF from markdown content using reportlab"""
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles for clean PDF
        custom_title = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            textColor=colors.black,
            alignment=1  # Center
        )
        
        custom_heading = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.black
        )
        
        # Process markdown simply
        lines = markdown_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
                
            if line.startswith('# '):
                text = line[2:].strip()
                story.append(Paragraph(text, custom_title))
                story.append(Spacer(1, 12))
                
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, custom_heading))
                
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(text, styles['Heading3']))
                
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip()
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                story.append(Paragraph(f"• {text}", styles['Normal']))
                
            elif re.match(r'^\d+\. ', line):
                text = re.sub(r'^\d+\. ', '', line)
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                story.append(Paragraph(text, styles['Normal']))
                
            else:
                if line:
                    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                    story.append(Paragraph(text, styles['Normal']))
                    story.append(Spacer(1, 4))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    def _build_response(self, session_id: str, status: str, conversation: List[dict], 
                       **kwargs) -> Dict[str, Any]:
        """Build standardized API response"""
        response_data = {
            "status": status,
            "session_id": session_id,
            "conversation_history": conversation,
            "processing_info": kwargs.get("processing_info", {}),
            "pipeline_info": kwargs.get("pipeline_info", [])
        }
        
        # Add PDF output if available
        if "pdf_output" in kwargs:
            response_data["pdf_output"] = kwargs["pdf_output"]
            
        if status == "error" and "error_message" in kwargs:
            response_data["error_message"] = kwargs["error_message"]
            
        return {"response_data": response_data}

    async def process_conversation_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point - consolidated routing with single AI call"""
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

            if document_content:
                # DOCUMENT PROCESSING PATH WITH CONSOLIDATED AI ANALYSIS
                print(f"Processing {file_type} document...")
                
                has_previous_document = document_content != self._parse_document_extraction(user_message)[0]
                
                # CONSOLIDATED STEP: Single AI call for intent + classification
                # Handle case where user uploads document without any text input
                if clean_user_input is None:
                    # No user text = direct document upload = processing request
                    analysis_result = {
                        "intent": "PROCESSING_REQUEST",
                        "document_type": "CV" if any(indicator in document_content.lower() for indicator in 
                                                    ["resume", "cv", "experience", "education", "skills", "work history"]) else "GENERAL",
                        "confidence": 0.9,
                        "reasoning": "Direct document upload without user text indicates processing request",
                        "action": "process_cv" if any(indicator in document_content.lower() for indicator in 
                                                    ["resume", "cv", "experience", "education", "skills", "work history"]) else "process_general",
                        "ambiguity_level": "low",
                        "fallback_used": False,
                        "user_question_extracted": "Process this document"
                    }
                else:
                    analysis_result = await self._analyze_intent_and_classify(
                        clean_user_input, 
                        document_content, 
                        has_previous_document
                    )
                
                user_intent = analysis_result.get("intent", "PROCESSING_REQUEST")
                document_type = analysis_result.get("document_type", "GENERAL")
                
                if user_intent == "INFORMATION_REQUEST":
                    # Quick summary only
                    print("User wants information about document - providing quick summary")
                    summary_response = await self._provide_quick_summary(document_content, clean_user_input)
                    
                    conversation.append({"role": "assistant", "content": summary_response})
                    
                    pipeline_info = get_quick_response_pipeline()
                    
                    return self._build_response(session_id, "completed", conversation,
                                              processing_info={
                                                  "intent": analysis_result,
                                                  "file_type": file_type,
                                                  "response_type": "quick_summary",
                                                  "context_source": "previous_conversation" if has_previous_document else "current_message"
                                              },
                                              pipeline_info=pipeline_info)
                
                elif user_intent == "PROCESSING_REQUEST":
                    # Full extraction and PDF generation
                    print(f"User wants document processing - running extraction pipeline for {document_type}")
                    
                    # Extract content based on consolidated classification
                    extracted_content = await self._extract_document_content(document_content, document_type)
                    
                    # Format to markdown
                    markdown_content = await self._format_to_markdown(extracted_content, document_type)
                    
                    # Generate PDF
                    pdf_bytes = await self._generate_pdf_from_markdown(markdown_content)
                    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
                    
                    # Build response message
                    doc_type = document_type.lower()
                    
                    if has_previous_document:
                        if "summary" in clean_user_input.lower() or "create" in clean_user_input.lower():
                            response_text = f"I've processed the {file_type.upper()} document as requested. "
                        else:
                            response_text = f"Based on your request '{clean_user_input}', I've processed the {file_type.upper()} document. "
                    else:
                        response_text = f"I've processed your {doc_type} document ({file_type.upper()}). "
                    
                    if doc_type == "cv":
                        response_text += "I've extracted your professional information and included focused future skills recommendations."
                    else:
                        response_text += "I've extracted and organized the content into a clean, professional format."
                    
                    conversation.append({"role": "assistant", "content": response_text})
                    
                    # Generate pipeline info with consolidated analysis
                    selected_processor = "CVAnalysisSkill" if document_type == "CV" else "DocumentExtractionSkill"
                    pipeline_info = ["SmartIntentProcessor", selected_processor, "MarkdownFormatterAgent"]
                    
                    return self._build_response(session_id, "completed", conversation,
                                              processing_info={
                                                  "intent": analysis_result,
                                                  "classification": {"classification": document_type, "confidence": analysis_result.get("confidence", 0.6)},
                                                  "file_type": file_type,
                                                  "content_type": doc_type,
                                                  "response_type": "extraction_and_pdf",
                                                  "context_source": "previous_conversation" if has_previous_document else "current_message"
                                              },
                                              pipeline_info=pipeline_info,
                                              pdf_output={
                                                  "pdf_data": pdf_base64,
                                                  "filename": f"{doc_type}_extract_{session_id}.pdf"
                                              })
                
                else:
                    # This should rarely happen with the new smart processor, but keeping as safety net
                    clarification_response = f"I can see you've uploaded a {file_type.upper()} document. Would you like me to:\n\n• **Summarize it** - Tell you what's in the document\n• **Process it** - Extract content and generate a PDF\n\nWhat would you prefer?"
                    
                    conversation.append({"role": "assistant", "content": clarification_response})
                    
                    return self._build_response(session_id, "needs_clarification", conversation,
                                              processing_info={
                                                  "intent": analysis_result,
                                                  "file_type": file_type,
                                                  "response_type": "clarification_request",
                                                  "context_source": "previous_conversation" if has_previous_document else "current_message"
                                              })
            
            else:
                # No document found
                if any(keyword in user_message.lower() for keyword in ["upload", "document", "file", "pdf", "word"]):
                    response_text = "Please upload a PDF or Word document for processing. I can extract CV information or organize general documents into clean PDFs."
                else:
                    response_text = "I'm ready to help you process documents! Upload a PDF or Word file, and I can:\n\n• **CV/Resume**: Extract your profile with future skills recommendations\n• **General Documents**: Extract and organize content into clean PDFs\n\nWhat would you like to do?"
                
                conversation.append({"role": "assistant", "content": response_text})
                
                return self._build_response(session_id, "waiting_for_file", conversation)
        
        except Exception as e:
            error_message = f"Processing error: {str(e)}"
            print(f"PDF Orchestrator Error: {error_message}")
            
            conversation.append({"role": "assistant", "content": "I encountered an error processing your request. Please try again or upload a different document."})
            
            return self._build_response(session_id, "error", conversation,
                                      error_message=error_message)
