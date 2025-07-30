const { PowerPointOrchestrator } = require('../src/orchestrator/pptOrchestrator');

module.exports = async function (context, req) {
    context.log('PowerPoint Generation v2 function processed a request.');

    if (req.method === 'GET') {
        context.res = {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                service: 'Presentation Planning Service v2',
                status: 'running',
                version: '2.1.0',
                description: 'Conversational presentation requirements gathering for third-party PowerPoint services'
            })
        };
        return;
    }

    try {
        // Get request body
        const requestBody = req.body;
        
        // Initialize orchestrator
        const orchestrator = new PowerPointOrchestrator();
        
        // Process the conversation request
        const response = await orchestrator.processConversationRequest(requestBody);
        
        context.res = {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
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
        
        context.res = {
            status: 500,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(errorResponse)
        };
    }
};