import azure.functions as func
import datetime
import json
import logging
from ppt_orchestrator import PowerPointOrchestrator

app = func.FunctionApp()

@app.route(route="powerpoint_generation", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def powerpoint_generation(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function endpoint for PowerPoint generation"""
    logging.info('PowerPoint generation function processed a request.')
    
    try:
        # Parse request
        req_body = req.get_json()
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Initialize orchestrator
        orchestrator = PowerPointOrchestrator()
        
        # Process request
        result = await orchestrator.process_conversation_request(req_body)
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"PowerPoint generation error: {str(e)}")
        
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
