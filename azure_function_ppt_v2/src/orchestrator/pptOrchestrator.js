const { 
    AGENT_PIPELINE, 
    QUICK_RESPONSE_PIPELINE,
    PRESENTATION_CONFIG,
    PRESENTATION_FORMAT_CONFIG,
    generateSessionId 
} = require('../config/config');

// Import agents with updated naming convention
const { ConversationManager } = require('../agents/conversationManager_agent');
const { ClarificationQuestionGenerator } = require('../agents/clarificationQuestionGenerator_skill');

class PowerPointOrchestrator {
    constructor() {
        this.agents = {
            ConversationManager: new ConversationManager(),
            ClarificationQuestionGenerator: new ClarificationQuestionGenerator()
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
                    response_text: '',
                    powerpoint_output: null,
                    // Keep minimal processing info for debugging only
                    processing_info: {}
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

            // Minimal processing info for debugging
            response.response_data.processing_info = {
                intent: conversationResult.intent || 'conversation',
                content_source: conversationResult.content_source,
                has_errors: !!conversationResult.error_info
            };

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
            const needSlideEstimation = conversationResult.need_slide_estimation;
            const clarificationAnswers = conversationResult.clarification_answers;
            const hasDocumentContent = conversationResult.has_document_content;
            const hasConversationContent = conversationResult.conversation_content && conversationResult.conversation_content.trim();
            const contentSource = conversationResult.content_source || 'unknown';
            const requestedSlideCount = conversationResult.requested_slide_count;

            if (showClarificationQuestions && needSlideEstimation) {
                // Stage 1: Get AI slide recommendation, then generate clarification questions
                console.log('Stage 1: Getting AI slide recommendation for clarification questions');
                
                if (!hasDocumentContent && !hasConversationContent) {
                    throw new Error('Cannot generate slide recommendation without content');
                }

                // Generate slide estimation AND clarification questions in one AI call
                const clarificationInput = {
                    conversation_content: conversationResult.conversation_content,
                    conversation_history: conversation_history,
                    requested_slide_count: conversationResult.requested_slide_count
                };
                
                const clarificationResult = await this.agents.ClarificationQuestionGenerator.process(clarificationInput);
                const clarificationQuestions = clarificationResult.questions;

                response.response_data.processing_info.slide_estimate = {
                    estimated_slides: clarificationResult.estimated_slides,
                    content_complexity: clarificationResult.content_complexity,
                    slide_breakdown: clarificationResult.slide_breakdown,
                    complexity_factors: clarificationResult.complexity_factors,
                    reasoning: clarificationResult.reasoning,
                    confidence: clarificationResult.confidence,
                    user_specified: clarificationResult.user_specified
                };
                response.response_data.processing_info.clarification_analysis = {
                    content_analysis: clarificationResult.content_analysis,
                    reasoning: clarificationResult.reasoning
                };
                response.response_data.show_clarification_popup = true;
                response.response_data.clarification_questions = clarificationQuestions;
                response.response_data.response_text = "Please answer these questions to customize your presentation:";
                
                // Add assistant response to history
                updatedHistory.push({
                    role: 'assistant',
                    content: response.response_data.response_text,
                    timestamp: new Date().toISOString()
                });

                response.response_data.conversation_history = updatedHistory;
                response.response_data.status = 'completed';
                return response;
                
            } else if (showClarificationQuestions) {
                // Legacy: Direct clarification questions (shouldn't happen with new flow)
                console.log('Stage 1: Direct clarification questions (legacy)');
                
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
                    const slideEstimateInput = {
                        conversation_content: conversationResult.conversation_content,
                        conversation_history: conversation_history,
                        requested_slide_count: conversationResult.requested_slide_count
                    };
                    
                    // Add document content if available
                    if (hasDocumentContent) {
                        slideEstimateInput.document_content = conversationResult.document_content;
                    }

                    const clarificationResult = await this.agents.ClarificationQuestionGenerator.process(slideEstimateInput);
                    
                    const slideEstimate = {
                        estimated_slides: clarificationResult.estimated_slides,
                        content_complexity: clarificationResult.content_complexity,
                        reasoning: clarificationResult.reasoning,
                        confidence: clarificationResult.confidence,
                        user_specified: clarificationResult.user_specified
                    };
                    
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
                
                // Ensure we use clean response text, not raw JSON
                const cleanResponseText = conversationResult.response_text || "I understand your message. Please let me know if you'd like to create a presentation.";
                response.response_data.response_text = cleanResponseText;
                
                console.log('Setting response_text to:', cleanResponseText.substring(0, 100) + '...');

                // Add assistant response to history
                updatedHistory.push({
                    role: 'assistant',
                    content: cleanResponseText,
                    timestamp: new Date().toISOString()
                });

                response.response_data.conversation_history = updatedHistory;
                
                // Explicitly ensure status is correct
                response.response_data.status = 'completed';
                
                console.log('Final response status:', response.response_data.status);
                console.log('Final response_text (first 100 chars):', cleanResponseText.substring(0, 100));
                
                return response;
            } else {
                // Stage 2: Process clarification answers and return consolidated information
                console.log('Stage 2: Processing clarification answers and preparing consolidated information');

                if (!hasConversationContent) {
                    throw new Error('Cannot process clarification answers without conversation content');
                }

                // Finalize slide count based on user's choice
                let finalSlideCount = PRESENTATION_CONFIG.default_slides;
                if (clarificationAnswers && clarificationAnswers.slide_count) {
                    finalSlideCount = parseInt(clarificationAnswers.slide_count);
                    console.log(`Using user-specified slide count: ${finalSlideCount}`);
                } else if (requestedSlideCount) {
                    finalSlideCount = parseInt(requestedSlideCount);
                    console.log(`Using requested slide count: ${finalSlideCount}`);
                }

                // Prepare user preferences object
                const userPreferences = {
                    slide_count: finalSlideCount,
                    audience_level: clarificationAnswers.audience_level || clarificationAnswers.audience_level_select || 'General',
                    content_depth: clarificationAnswers.content_depth || 'Moderate detail',
                    content_focus: clarificationAnswers.content_focus || clarificationAnswers.content_focus_select || 'Balanced coverage',
                    include_examples: clarificationAnswers.include_examples || clarificationAnswers.include_examples_boolean || false,
                    ...this.extractAdditionalPreferences(clarificationAnswers)
                };

                // Prepare final consolidated information for third-party service
                const consolidatedInfo = {
                    // Combined summary: conversation topics + user preferences
                    content_summary: this.createCombinedSummary(conversationResult.conversation_content, conversationResult.user_context, userPreferences),
                    
                    // User's presentation preferences from clarification answers
                    user_preferences: userPreferences
                };

                response.response_data.consolidated_info = consolidatedInfo;
                response.response_data.response_text = `Presentation requirements processed successfully. ${finalSlideCount} slides will be created based on your preferences.`;

                // Add assistant response to history
                updatedHistory.push({
                    role: 'assistant',
                    content: response.response_data.response_text,
                    timestamp: new Date().toISOString(),
                    consolidated_info_prepared: true
                });

                response.response_data.conversation_history = updatedHistory;
                response.response_data.status = 'completed';

                console.log('Consolidated information preparation completed successfully');
                return response;
            }

        } catch (error) {
            console.error('Error in orchestrator:', error);
            
            return {
                response_data: {
                    status: 'error',
                    session_id: requestData.session_id || 'unknown',
                    error_message: error.message,
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

    // Helper method to extract original conversation Q&A pairs
    extractOriginalConversation(conversation_history) {
        try {
            // Find the conversation data in the history
            const conversationEntry = conversation_history.find(entry => 
                entry.content && typeof entry.content === 'string' && entry.content.includes('conversation')
            );
            
            if (conversationEntry) {
                const content = JSON.parse(conversationEntry.content);
                if (content.conversation && Array.isArray(content.conversation)) {
                    return content.conversation.map(item => ({
                        question: item.question,
                        response: item.response,
                        question_id: item.question_id,
                        response_timestamp: item.response_timestamp
                    }));
                }
            }
            
            // Fallback: extract from regular conversation flow
            return conversation_history
                .filter(entry => entry.role === 'user')
                .map((entry, index) => ({
                    question: entry.content,
                    response: conversation_history[conversation_history.indexOf(entry) + 1]?.content || null,
                    sequence: index + 1,
                    timestamp: entry.timestamp
                }));
                
        } catch (error) {
            console.warn('Could not parse conversation history:', error.message);
            return [];
        }
    }

    // Helper method to extract main topics from conversation
    extractMainTopics(originalConversation) {
        try {
            if (!originalConversation || originalConversation.length === 0) {
                return [];
            }
            
            // Simple topic extraction based on questions
            return originalConversation.map((item, index) => ({
                topic_id: index + 1,
                topic_question: item.question,
                topic_summary: item.response ? item.response.substring(0, 150) + '...' : 'No response',
                importance: index === 0 ? 'high' : 'medium' // First question usually most important
            }));
            
        } catch (error) {
            console.warn('Could not extract main topics:', error.message);
            return [];
        }
    }

    // Helper method to extract additional preferences from clarification answers
    extractAdditionalPreferences(clarificationAnswers) {
        const preferences = {};
        
        // Extract any preferences not already captured in main config
        Object.keys(clarificationAnswers || {}).forEach(key => {
            if (!['slide_count', 'audience_level', 'audience_level_select', 'content_depth', 
                  'content_focus', 'content_focus_select', 'include_examples', 'include_examples_boolean'].includes(key)) {
                preferences[key] = clarificationAnswers[key];
            }
        });
        
        return preferences;
    }

    // Helper method to create combined summary (conversation content + user preferences)
    createCombinedSummary(conversationContent, userContext, userPreferences) {
        try {
            // Extract conversation topics
            const topics = [];
            
            if (conversationContent) {
                // Extract topics from conversation content
                const lines = conversationContent.split('\n').filter(line => line.trim());
                
                for (const line of lines) {
                    // Look for topic indicators
                    if (line.includes('Topics discussed:') || line.includes('topics:')) {
                        const topicMatch = line.match(/\d+\)\s*([^(]+?)(?:\s*\(|$)/g);
                        if (topicMatch) {
                            topicMatch.forEach(match => {
                                const topic = match.replace(/\d+\)\s*/, '').trim();
                                if (topic && topic.length > 3) topics.push(topic);
                            });
                        }
                    }
                }
            }
            
            // Fallback: extract from user context
            if (topics.length === 0 && userContext) {
                if (userContext.toLowerCase().includes('stock market')) {
                    topics.push('stock market basics', 'notable market prediction figures');
                }
            }
            
            // Build combined summary
            let summary = '';
            
            // Part 1: What topics were discussed
            if (topics.length > 0) {
                summary = `User discussed ${topics.join(' and ')}.`;
            } else {
                summary = `User provided conversation content for presentation.`;
            }
            
            // Part 2: How they want it presented (user preferences)
            const preferences = userPreferences;
            const prefParts = [];
            
            if (preferences.slide_count) {
                prefParts.push(`${preferences.slide_count}-slide presentation`);
            }
            if (preferences.audience_level && preferences.audience_level !== 'General') {
                prefParts.push(`for ${preferences.audience_level.toLowerCase()} audience`);
            }
            if (preferences.content_depth && preferences.content_depth !== 'Moderate detail') {
                prefParts.push(`with ${preferences.content_depth.toLowerCase()}`);
            }
            if (preferences.content_focus && preferences.content_focus !== 'Balanced coverage') {
                prefParts.push(`focusing on ${preferences.content_focus.toLowerCase()}`);
            }
            if (preferences.include_examples) {
                prefParts.push('including practical examples');
            }
            
            if (prefParts.length > 0) {
                summary += ` They want a ${prefParts.join(', ')}.`;
            }
            
            return summary;
            
        } catch (error) {
            console.warn('Could not create combined summary:', error.message);
            return `User provided presentation content with ${userPreferences.slide_count || 'multiple'} slides for ${userPreferences.audience_level || 'general'} audience.`;
        }
    }

    // Helper method to extract the original clarification questions from conversation history
    getOriginalClarificationQuestions(sessionId, conversation_history) {
        try {
            // Look for the assistant response that contained clarification questions
            const clarificationResponse = conversation_history.find(entry => 
                entry.role === 'assistant' && 
                entry.content.includes('Please answer these questions to customize')
            );
            
            // In a real implementation, you might store questions in session or extract from response
            // For now, return a placeholder structure that third-party services can understand
            return {
                note: "Clarification questions were generated dynamically based on conversation analysis",
                question_types: [
                    "slide_count (AI-recommended based on content analysis)",
                    "target_audience (select from predefined options)",
                    "content_depth (level of detail preference)",
                    "content_focus (emphasis areas)",
                    "include_examples (boolean preference)"
                ],
                generation_timestamp: clarificationResponse?.timestamp || new Date().toISOString(),
                ai_generated: true
            };
            
        } catch (error) {
            console.warn('Could not extract clarification questions:', error.message);
            return {
                note: "Questions were generated but could not be retrieved from history",
                ai_generated: true
            };
        }
    }
}

module.exports = { PowerPointOrchestrator };