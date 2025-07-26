const { app } = require('@azure/functions');
const { PowerPointOrchestrator } = require('../orchestrator/pptOrchestrator');

app.http('powerpointGeneration', {
    methods: ['GET', 'POST'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        context.log('PowerPoint Generation v2 function processed a request.');

        if (request.method === 'GET') {
            return { 
                status: 200, 
                body: JSON.stringify({
                    service: 'PowerPoint Generation v2',
                    status: 'running',
                    version: '1.0.0',
                    description: 'Conversational PowerPoint generation using PptxGenJS'
                })
            };
        }

        try {
            // Get request body
            const requestBody = await request.json();
            
            // Initialize orchestrator
            const orchestrator = new PowerPointOrchestrator();
            
            // Process the conversation request
            const response = await orchestrator.processConversationRequest(requestBody);
            
            return {
                status: 200,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(response)
            };

        } catch (error) {
            context.log.error('Error processing request:', error);
            
            const errorResponse = {
                response_data: {
                    status: 'error',
                    session_id: requestBody?.session_id || 'N/A',
                    error_message: `Server error: ${error.message}`
                }
            };
            
            return {
                status: 500,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(errorResponse)
            };
        }
    }
});