/**
 * Hybrid API Orchestrator - Coordinates Python AI agents with Node.js PptxGenJS
 */
const axios = require('axios');
const PptxGenJS = require('pptxgenjs');
const { v4: uuidv4 } = require('uuid');
const { 
    API_CONFIG, 
    PRESENTATION_CONFIG, 
    generateSessionId,
    getOptimalSlideCount 
} = require('./config');
const SlideBuilder = require('./utils/slide_builder');
const DocumentParser = require('./utils/document_parser');

class HybridOrchestrator {
    constructor() {
        this.slideBuilder = new SlideBuilder();
        this.documentParser = new DocumentParser();
    }

    /**
     * Main request processing pipeline
     */
    async processRequest(requestBody, sessionId, context) {
        context.log('HybridOrchestrator: Starting request processing');
        
        try {
            const conversation = requestBody.conversation_history || [];
            const userMessage = requestBody.user_message?.trim();
            
            if (!userMessage) {
                return this.buildErrorResponse(sessionId, conversation, 'User message required');
            }

            // Add user message to conversation
            conversation.push({ role: 'user', content: userMessage });

            // Parse document content from message
            const { documentContent, cleanUserInput, fileType } = this.parseDocumentExtraction(userMessage);
            
            // Handle different request types
            if (!documentContent) {
                // Check for continuation request from conversation history
                const { content: previousDoc, type: prevType } = this.extractFromConversationHistory(conversation);
                
                if (previousDoc && this.isContinuationRequest(userMessage, conversation)) {
                    return await this.processPresentation(previousDoc, userMessage, prevType, sessionId, conversation, context);
                } else {
                    return this.handleNoDocumentRequest(userMessage, sessionId, conversation);
                }
            } else {
                // Process new document
                return await this.processPresentation(documentContent, cleanUserInput, fileType, sessionId, conversation, context);
            }

        } catch (error) {
            context.log(`HybridOrchestrator error: ${error.message}`);
            return this.buildErrorResponse(sessionId, requestBody.conversation_history || [], error.message);
        }
    }

    /**
     * Process presentation generation pipeline
     */
    async processPresentation(documentContent, userInput, fileType, sessionId, conversation, context) {
        context.log('Processing presentation generation');
        
        try {
            // Step 1: Analyze content with Python agent
            context.log('Step 1: Analyzing content with Python AI agent');
            const contentAnalysis = await this.analyzeContentWithPython(documentContent, userInput, context);
            
            // Step 2: Generate PowerPoint with PptxGenJS
            context.log('Step 2: Generating PowerPoint with PptxGenJS');
            const pptResult = await this.generatePowerPointWithPptxGenJS(contentAnalysis, sessionId, context);
            
            // Build successful response
            const responseText = `I've created a professional business presentation from your ${fileType?.toUpperCase() || 'document'}. ` +
                               `The presentation contains ${contentAnalysis.slideCount || 12} slides with corporate branding and enhanced formatting.`;
            
            conversation.push({ role: 'assistant', content: responseText });
            
            return {
                response_data: {
                    status: 'completed',
                    session_id: sessionId,
                    conversation_history: conversation,
                    processing_info: {
                        content_analysis: contentAnalysis,
                        file_type: fileType,
                        response_type: 'powerpoint_generation',
                        architecture: 'hybrid',
                        ai_agent: 'python',
                        presentation_engine: 'pptxgenjs'
                    },
                    powerpoint_output: {
                        ppt_data: pptResult.base64Data,
                        filename: `presentation_v2_${sessionId}.pptx`,
                        slides_count: contentAnalysis.slideCount,
                        generation_time_ms: pptResult.generationTime
                    }
                }
            };
            
        } catch (error) {
            context.log(`Presentation processing error: ${error.message}`);
            throw new Error(`Failed to generate presentation: ${error.message}`);
        }
    }

    /**
     * Analyze content using Python AI agent
     */
    async analyzeContentWithPython(documentContent, userInput, context) {
        context.log('Calling Python content analysis agent');
        
        try {
            const payload = {
                document_content: documentContent,
                user_input: userInput || 'Create a professional presentation from this document',
                analysis_type: 'presentation_planning',
                max_slides: PRESENTATION_CONFIG.maxSlides
            };

            const response = await axios.post(API_CONFIG.pythonAgentUrl, payload, {
                timeout: API_CONFIG.timeout,
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.data && response.data.analysis) {
                context.log('Python agent analysis completed successfully');
                return response.data.analysis;
            } else {
                throw new Error('Invalid response from Python agent');
            }

        } catch (error) {
            context.log(`Python agent error: ${error.message}`);
            
            // Fallback: Create basic analysis structure
            return this.createFallbackAnalysis(documentContent, userInput, context);
        }
    }

    /**
     * Generate PowerPoint using PptxGenJS
     */
    async generatePowerPointWithPptxGenJS(contentAnalysis, sessionId, context) {
        context.log('Generating PowerPoint with PptxGenJS');
        
        const startTime = Date.now();
        
        try {
            const pres = new PptxGenJS();
            
            // Configure presentation settings
            pres.layout = 'LAYOUT_16x9';
            pres.rtlMode = false;
            
            // Apply corporate template
            this.slideBuilder.applyCorperateTemplate(pres);
            
            // Generate slides from analysis
            const slides = contentAnalysis.slides || this.createDefaultSlides(contentAnalysis);
            
            for (let i = 0; i < slides.length; i++) {
                const slideData = slides[i];
                context.log(`Creating slide ${i + 1}: ${slideData.title} (${slideData.type})`);
                
                await this.slideBuilder.createSlide(pres, slideData, i === 0, i === slides.length - 1);
            }
            
            // Generate presentation buffer
            const pptxBuffer = await pres.write({ outputType: 'nodebuffer' });
            const base64Data = pptxBuffer.toString('base64');
            
            const generationTime = Date.now() - startTime;
            context.log(`PowerPoint generation completed in ${generationTime}ms`);
            
            return {
                base64Data,
                generationTime,
                slideCount: slides.length
            };
            
        } catch (error) {
            context.log(`PptxGenJS generation error: ${error.message}`);
            throw new Error(`PowerPoint generation failed: ${error.message}`);
        }
    }

    /**
     * Create fallback analysis when Python agent fails
     */
    createFallbackAnalysis(documentContent, userInput, context) {
        context.log('Creating fallback content analysis');
        
        const contentLength = documentContent.length;
        const optimalSlides = getOptimalSlideCount(contentLength);
        
        // Basic content extraction
        const paragraphs = documentContent.split('\n\n').filter(p => p.trim().length > 0);
        const sentences = documentContent.split(/[.!?]+/).filter(s => s.trim().length > 10);
        
        return {
            slideCount: optimalSlides,
            contentSummary: sentences.slice(0, 3).join('. ') + '.',
            keyPoints: paragraphs.slice(0, 8).map(p => p.trim().substring(0, 150) + '...'),
            slides: this.createDefaultSlides({
                slideCount: optimalSlides,
                contentSummary: sentences.slice(0, 3).join('. ') + '.',
                keyPoints: paragraphs.slice(0, 8).map(p => p.trim().substring(0, 150))
            }),
            analysisMethod: 'fallback',
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Create default slide structure
     */
    createDefaultSlides(analysis) {
        const slides = [];
        const slideCount = analysis.slideCount || 10;
        const keyPoints = analysis.keyPoints || [];
        
        // Title slide
        slides.push({
            type: 'TITLE_SLIDE',
            title: 'Business Presentation',
            subtitle: 'Generated from Document Analysis',
            content: []
        });
        
        // Agenda slide
        slides.push({
            type: 'AGENDA_SLIDE',
            title: 'Agenda',
            content: [
                'Overview and Context',
                'Key Analysis Points',
                'Findings and Insights',
                'Recommendations',
                'Next Steps'
            ]
        });
        
        // Content slides
        const contentSlideCount = slideCount - 4; // Exclude title, agenda, summary, thank you
        const pointsPerSlide = Math.ceil(keyPoints.length / contentSlideCount);
        
        for (let i = 0; i < contentSlideCount; i++) {
            const startIdx = i * pointsPerSlide;
            const slidePoints = keyPoints.slice(startIdx, startIdx + pointsPerSlide);
            
            slides.push({
                type: 'CONTENT_SLIDE',
                title: `Analysis Point ${i + 1}`,
                content: slidePoints.length > 0 ? slidePoints : ['Content extracted from document analysis']
            });
        }
        
        // Summary slide
        slides.push({
            type: 'SUMMARY_SLIDE',
            title: 'Summary',
            content: [
                'Key insights from document analysis',
                'Important findings and observations',
                'Strategic recommendations',
                'Proposed next steps'
            ]
        });
        
        // Thank you slide
        slides.push({
            type: 'THANK_YOU_SLIDE',
            title: 'Thank You',
            content: []
        });
        
        return slides.slice(0, slideCount);
    }

    /**
     * Parse document extraction from user message
     */
    parseDocumentExtraction(userMessage) {
        if (userMessage.includes('[document]')) {
            const parts = userMessage.split('[document]', 2);
            return {
                documentContent: parts[1]?.trim() || null,
                cleanUserInput: parts[0]?.trim() || null,
                fileType: 'document'
            };
        }
        
        return {
            documentContent: null,
            cleanUserInput: userMessage,
            fileType: null
        };
    }

    /**
     * Extract document from conversation history
     */
    extractFromConversationHistory(conversation) {
        for (const message of conversation.reverse()) {
            if (message.role === 'user' && message.content.includes('[document]')) {
                const parts = message.content.split('[document]', 2);
                return {
                    content: parts[1]?.trim() || null,
                    type: 'document'
                };
            }
        }
        return { content: null, type: null };
    }

    /**
     * Check if this is a continuation request
     */
    isContinuationRequest(userMessage, conversation) {
        const continuationKeywords = [
            'create', 'generate', 'make', 'build', 'produce', 'presentation',
            'slides', 'powerpoint', 'ppt', 'convert', 'proceed'
        ];
        
        const userLower = userMessage.toLowerCase();
        return (
            continuationKeywords.some(keyword => userLower.includes(keyword)) &&
            userMessage.split(' ').length <= 10
        );
    }

    /**
     * Handle requests without documents
     */
    handleNoDocumentRequest(userMessage, sessionId, conversation) {
        const responseText = userMessage.toLowerCase().includes('presentation') || 
                           userMessage.toLowerCase().includes('powerpoint')
            ? `Please upload a PDF or Word document to create a presentation from. I can generate professional PowerPoint presentations up to ${PRESENTATION_CONFIG.maxSlides} slides with corporate branding using advanced PptxGenJS technology.`
            : 'I can create professional PowerPoint presentations from PDF and Word documents. Upload a document to get started.';
        
        conversation.push({ role: 'assistant', content: responseText });
        
        return {
            response_data: {
                status: 'waiting_for_file',
                session_id: sessionId,
                conversation_history: conversation,
                capabilities: {
                    max_slides: PRESENTATION_CONFIG.maxSlides,
                    supported_formats: ['PDF', 'Word documents'],
                    features: ['Corporate branding', 'Advanced formatting', 'PptxGenJS integration']
                }
            }
        };
    }

    /**
     * Build error response
     */
    buildErrorResponse(sessionId, conversation, errorMessage) {
        conversation.push({ 
            role: 'assistant', 
            content: 'I encountered an error processing your request. Please try again or upload a different document.' 
        });
        
        return {
            response_data: {
                status: 'error',
                session_id: sessionId,
                conversation_history: conversation,
                error_message: errorMessage,
                architecture: 'hybrid'
            }
        };
    }
}

module.exports = new HybridOrchestrator();