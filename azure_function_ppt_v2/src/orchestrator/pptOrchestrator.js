const { 
    AGENT_PIPELINE, 
    QUICK_RESPONSE_PIPELINE,
    generateSessionId 
} = require('../config/config');

// Import agents with updated naming convention
const { ConversationManager } = require('../agents/conversationManager_agent');
const { DocumentProcessor } = require('../agents/documentProcessor_skill');
const { SlideEstimator } = require('../agents/slideEstimator_skill');
const { ContentStructurer } = require('../agents/contentStructurer_skill');
const { PptxGenerator } = require('../agents/pptxGenerator_skill');

class PowerPointOrchestrator {
    constructor() {
        this.agents = {
            ConversationManager: new ConversationManager(),
            DocumentProcessor: new DocumentProcessor(),
            SlideEstimator: new SlideEstimator(),
            ContentStructurer: new ContentStructurer(),
            PptxGenerator: new PptxGenerator()
        };
        
        this.conversationHistory = new Map(); // Store conversation history by session
    }

    async processConversationRequest(requestData) {
        try {
            console.log('Processing conversation request:', {
                hasMessage: !!requestData.user_message,
                sessionId: requestData.session_id,
                hasHistory: !!requestData.conversation_history
            });

            // Extract request data
            const {
                user_message,
                entra_id,
                session_id,
                conversation_history = []
            } = requestData;

            // Generate or use existing session ID
            const sessionId = session_id || generateSessionId();

            // Initialize response structure
            const response = {
                response_data: {
                    status: 'processing',
                    session_id: sessionId,
                    conversation_history: conversation_history,
                    pipeline_info: [],
                    processing_info: {},
                    response_text: '',
                    powerpoint_output: null
                }
            };

            // Step 1: Conversation Management
            console.log('Step 1: Processing conversation with ConversationManager');
            const conversationResult = await this.agents.ConversationManager.process({
                user_message,
                session_id: sessionId,
                conversation_history,
                entra_id
            });

            response.response_data.pipeline_info.push('ConversationManager');
            response.response_data.processing_info.conversation = conversationResult;

            // Update conversation history
            const updatedHistory = [...conversation_history, {
                role: 'user',
                content: user_message,
                timestamp: new Date().toISOString()
            }];

            // Determine workflow stage
            const shouldGeneratePresentation = conversationResult.should_generate_presentation;
            const showSlideRecommendation = conversationResult.show_slide_recommendation;
            const showClarificationQuestions = conversationResult.show_clarification_questions;
            const clarificationAnswers = conversationResult.clarification_answers;
            const hasDocumentContent = conversationResult.has_document_content;
            const hasConversationContent = conversationResult.conversation_content && conversationResult.conversation_content.trim();
            const contentSource = conversationResult.content_source || 'unknown';
            const requestedSlideCount = conversationResult.requested_slide_count;

            if (showClarificationQuestions) {
                // Stage 1: Show clarification questions (frontend will show popup)
                console.log('Stage 1: Providing clarification questions for popup');
                
                response.response_data.show_clarification_popup = true;
                response.response_data.clarification_questions = conversationResult.clarification_questions;
                response.response_data.response_text = conversationResult.response_text;
                
                // Add assistant response to history
                updatedHistory.push({
                    role: 'assistant',
                    content: conversationResult.response_text,
                    timestamp: new Date().toISOString()
                });

                response.response_data.conversation_history = updatedHistory;
                response.response_data.status = 'completed';
                return response;
                
            } else if (showSlideRecommendation) {
                // Legacy: Show slide recommendation (frontend will show popup)
                console.log('Stage 1: Providing slide recommendation for popup');
                
                if (hasDocumentContent || hasConversationContent) {
                    const slideEstimateInput = {};
                    
                    if (hasDocumentContent) {
                        slideEstimateInput.document_content = conversationResult.document_content;
                    }
                    
                    if (hasConversationContent) {
                        slideEstimateInput.conversation_content = conversationResult.conversation_content;
                    }
                    
                    slideEstimateInput.user_context = conversationResult.user_context;

                    const slideEstimate = await this.agents.SlideEstimator.process(slideEstimateInput);
                    
                    response.response_data.pipeline_info.push('SlideEstimator');
                    response.response_data.processing_info.slide_estimate = slideEstimate;
                    response.response_data.show_slide_popup = true;
                    response.response_data.recommended_slides = slideEstimate.estimated_slides;
                    response.response_data.response_text = `Ready to create presentation! I recommend ${slideEstimate.estimated_slides} slides based on your conversation content.`;
                } else {
                    throw new Error('Cannot recommend slides without content');
                }
            } else if (!shouldGeneratePresentation) {
                // Regular conversation - no presentation workflow
                console.log('Regular conversation mode');
                response.response_data.response_text = conversationResult.response_text;

                // Add assistant response to history
                updatedHistory.push({
                    role: 'assistant',
                    content: response.response_data.response_text,
                    timestamp: new Date().toISOString()
                });

                response.response_data.conversation_history = updatedHistory;
                response.response_data.status = 'completed';
                return response;
            } else {
                // Stage 2: Generate presentation with confirmed slide count
                console.log('Stage 2: Generating presentation with user-confirmed slide count');

                if (!hasDocumentContent && !hasConversationContent) {
                    throw new Error('Cannot generate presentation without document content or conversation content');
                }

                // Step 2: Content Processing
                console.log('Step 2: Processing content');
                const processingInput = {
                    user_context: conversationResult.user_context,
                    content_source: contentSource
                };

                // Add clarification answers if provided
                if (clarificationAnswers) {
                    processingInput.clarification_answers = clarificationAnswers;
                    console.log('Using clarification answers for content processing');
                }

                if (hasDocumentContent) {
                    processingInput.document_content = conversationResult.document_content;
                }

                if (hasConversationContent) {
                    processingInput.conversation_content = conversationResult.conversation_content;
                }

                const documentResult = await this.agents.DocumentProcessor.process(processingInput);

                response.response_data.pipeline_info.push('DocumentProcessor');
                response.response_data.processing_info.document_analysis = documentResult;

                // Step 3: Slide Estimation
                console.log('Step 3: Estimating slide count');
                const slideEstimateInput = {
                    processed_content: documentResult,
                    user_context: conversationResult.user_context
                };

                if (hasDocumentContent) {
                    slideEstimateInput.document_content = conversationResult.document_content;
                }

                if (hasConversationContent) {
                    slideEstimateInput.conversation_content = conversationResult.conversation_content;
                }

                // Pass requested slide count if specified by user
                if (requestedSlideCount) {
                    slideEstimateInput.requested_slide_count = requestedSlideCount;
                }

                const slideEstimate = await this.agents.SlideEstimator.process(slideEstimateInput);

                response.response_data.pipeline_info.push('SlideEstimator');
                response.response_data.processing_info.slide_estimate = slideEstimate;

                // Step 4: Content Structuring
                console.log('Step 4: Structuring content for slides');
                const structuringInput = {
                    processed_content: documentResult,
                    slide_estimate: slideEstimate,
                    user_context: conversationResult.user_context
                };

                // Add clarification answers for content structuring
                if (clarificationAnswers) {
                    structuringInput.clarification_answers = clarificationAnswers;
                }

                const structuredContent = await this.agents.ContentStructurer.process(structuringInput);

                response.response_data.pipeline_info.push('ContentStructurer');
                response.response_data.processing_info.content_structure = structuredContent;

                // Step 5: PowerPoint Generation
                console.log('Step 5: Generating PowerPoint file');
                const pptxResult = await this.agents.PptxGenerator.process({
                    structured_content: structuredContent,
                    slide_estimate: slideEstimate,
                    session_id: sessionId
                });

                response.response_data.pipeline_info.push('PptxGenerator');
                response.response_data.powerpoint_output = pptxResult;

                // Prepare final response
                response.response_data.response_text = this.formatGenerationResponse(slideEstimate, pptxResult);

                // Add assistant response to history
                updatedHistory.push({
                    role: 'assistant',
                    content: response.response_data.response_text,
                    timestamp: new Date().toISOString(),
                    powerpoint_generated: true
                });

                response.response_data.conversation_history = updatedHistory;
                response.response_data.status = 'completed';

                console.log('PowerPoint generation completed successfully');
                return response;
            }

        } catch (error) {
            console.error('Error in orchestrator:', error);
            
            return {
                response_data: {
                    status: 'error',
                    session_id: requestData.session_id || 'unknown',
                    error_message: error.message,
                    pipeline_info: [],
                    conversation_history: requestData.conversation_history || []
                }
            };
        }
    }

    formatConversationResponse(conversationResult, slideEstimate = null) {
        let response = conversationResult.response_text;
        
        if (slideEstimate) {
            response += `\n\nBased on your document, I estimate this presentation would have approximately ${slideEstimate.estimated_slides} slides. When you're ready, click "Create Presentation" to generate the PowerPoint file.`;
        }
        
        return response;
    }

    formatGenerationResponse(slideEstimate, pptxResult) {
        return `PowerPoint presentation generated successfully!\n\nPresentation Details:\n- Slides: ${slideEstimate.estimated_slides}\n- File: ${pptxResult.filename}\n- Size: ${Math.round(pptxResult.file_size_kb)}KB\n\nYour presentation is ready for download.`;
    }
}

module.exports = { PowerPointOrchestrator };