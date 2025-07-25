/**
 * Azure Function PowerPoint Generation v2 - Main Entry Point
 * Hybrid architecture with Node.js + PptxGenJS
 */
const { app } = require('@azure/functions');
const fs = require('fs');
const path = require('path');
const { generateSessionId } = require('./config');
const orchestrator = require('./orchestrator');

// Ensure local output directory exists
const LOCAL_OUTPUT_DIR = path.join(__dirname, 'local_output');
if (!fs.existsSync(LOCAL_OUTPUT_DIR)) {
    fs.mkdirSync(LOCAL_OUTPUT_DIR, { recursive: true });
}

app.http('powerpoint_generation_v2', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        context.log('PowerPoint Generation v2 - Processing request');
        
        try {
            // Parse request body
            const requestBody = await request.json();
            
            if (!requestBody) {
                return {
                    status: 400,
                    jsonBody: {
                        status: 'error',
                        error_message: 'Invalid JSON in request body'
                    }
                };
            }

            // Generate session ID if not provided
            const sessionId = requestBody.session_id || generateSessionId();
            context.log(`Processing request with session ID: ${sessionId}`);

            // Process through hybrid orchestrator
            const result = await orchestrator.processRequest(requestBody, sessionId, context);

            // Save PowerPoint file locally if generated
            if (result.response_data?.powerpoint_output?.ppt_data) {
                try {
                    const pptData = result.response_data.powerpoint_output.ppt_data;
                    const filename = result.response_data.powerpoint_output.filename;
                    
                    // Decode base64 and save file
                    const pptBuffer = Buffer.from(pptData, 'base64');
                    const outputPath = path.join(LOCAL_OUTPUT_DIR, filename);
                    
                    fs.writeFileSync(outputPath, pptBuffer);
                    context.log(`PowerPoint file saved to: ${outputPath}`);
                    
                    // Add local save path to response
                    result.response_data.local_save_path = outputPath;
                    
                } catch (saveError) {
                    context.log(`Failed to save PowerPoint file: ${saveError.message}`);
                    result.response_data.local_save_error = saveError.message;
                }
            }

            return {
                status: 200,
                jsonBody: result
            };

        } catch (error) {
            context.log(`Unhandled error: ${error.message}`);
            context.log(`Stack trace: ${error.stack}`);
            
            const sessionId = generateSessionId();
            return {
                status: 500,
                jsonBody: {
                    response_data: {
                        status: 'error',
                        session_id: sessionId,
                        error_message: `Server error: ${error.message}`,
                        service_version: 'v2.0.0',
                        architecture: 'hybrid'
                    }
                }
            };
        }
    }
});

// Health check endpoint
app.http('health_v2', {
    methods: ['GET'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        return {
            status: 200,
            jsonBody: {
                status: 'healthy',
                service: 'PowerPoint Generation v2',
                version: '2.0.0',
                architecture: 'hybrid',
                timestamp: new Date().toISOString(),
                features: [
                    'PptxGenJS integration',
                    'Hybrid Python/Node.js architecture',
                    'Corporate slide masters',
                    'Advanced table and chart generation',
                    'Faster processing pipeline'
                ]
            }
        };
    }
});

context.log('Azure Function PowerPoint Generation v2 initialized successfully');