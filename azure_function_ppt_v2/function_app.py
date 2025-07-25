import azure.functions as func
import logging
import json
import asyncio
import os
import base64
from ppt_orchestrator_v2 import PPTOrchestratorV2

# Local output directory for saving generated presentations
LOCAL_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "local_output")
if not os.path.exists(LOCAL_OUTPUT_DIR):
    os.makedirs(LOCAL_OUTPUT_DIR)

# Define the function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="powerpoint_generation_v2")
async def powerpoint_generation_v2(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main HTTP Trigger for the PowerPoint Generation Service V2.
    Uses Pandoc + Markdown approach for better consistency.
    """
    logging.info('PowerPoint V2 HTTP trigger function processed a request.')

    try:
        # Get the request body as JSON
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
             "Invalid JSON in request body.",
             status_code=400
        )

    # Instantiate the V2 orchestrator
    orchestrator = PPTOrchestratorV2()
    
    # Process the request using the V2 orchestrator
    try:
        response_data = await orchestrator.process_conversation_request(req_body)
    except Exception as e:
        logging.error(f"V2 Orchestrator failed with an unhandled exception: {e}")
        error_response = {
            "response_data": {
                "status": "error",
                "session_id": req_body.get('session_id', 'N/A'),
                "error_message": f"V2 system encountered an unexpected error: {str(e)}",
                "system_version": "V2_Pandoc_Markdown"
            }
        }
        return func.HttpResponse(json.dumps(error_response), status_code=500, mimetype="application/json")

    # Check if the response contains PowerPoint data
    if response_data.get("response_data", {}).get("powerpoint_output"):
        ppt_output = response_data["response_data"]["powerpoint_output"]
        ppt_base64 = ppt_output.get("ppt_data")
        filename = ppt_output.get("filename", "presentation_v2.pptx")
        
        if ppt_base64:
            try:
                # Decode the base64 string back into bytes
                ppt_bytes = base64.b64decode(ppt_base64)
                
                # Create the full path to save the file
                output_filepath = os.path.join(LOCAL_OUTPUT_DIR, filename)
                
                # Write the bytes to a new .pptx file
                with open(output_filepath, "wb") as f:
                    f.write(ppt_bytes)
                
                logging.info(f"SUCCESS: V2 PowerPoint file saved locally to: {output_filepath}")
                
                # Add V2-specific info to the response
                response_data["response_data"]["local_save_path"] = output_filepath
                response_data["response_data"]["file_size_bytes"] = len(ppt_bytes)
                response_data["response_data"]["generation_method"] = "pandoc_markdown"

            except Exception as e:
                logging.error(f"Failed to save V2 file locally: {e}")
                # Add an error note to the response
                response_data["response_data"]["local_save_error"] = str(e)

    # Add V2 system identifier to all responses
    if "response_data" in response_data:
        response_data["response_data"]["system_version"] = "V2_Pandoc_Markdown"

    # Return the complete JSON response to the client
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        mimetype="application/json"
    )