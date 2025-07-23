import azure.functions as func
import json
import sys
import os

# Add project root to Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, current_dir)

from pdf_orchestrator import PDFOrchestrator

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """PDF Processing endpoint - handles document processing and conversation"""
    
    try:
        # Parse request
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Create fresh orchestrator instance per request (stateless)
        orchestrator = PDFOrchestrator()
        result = await orchestrator.process_conversation_request(req_body)
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": f"Server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
