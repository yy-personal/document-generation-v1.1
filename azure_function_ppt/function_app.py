import azure.functions as func
import logging
import json
import asyncio
import os
import base64
from ppt_orchestrator import PowerPointOrchestrator

# It will create a folder named 'local_output' inside your 'azure_function_ppt' directory.
LOCAL_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "local_output")
if not os.path.exists(LOCAL_OUTPUT_DIR):
    os.makedirs(LOCAL_OUTPUT_DIR)

# Define the function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="powerpoint_generation")
async def powerpoint_generation(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main HTTP Trigger for the PowerPoint Generation Service.
    """
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get the request body as JSON
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
             "Invalid JSON in request body.",
             status_code=400
        )

    # Instantiate the orchestrator
    orchestrator = PowerPointOrchestrator()
    
    # Process the request using the orchestrator
    # We use asyncio.run to execute the async method within the sync function handler
    try:
        response_data = await orchestrator.process_conversation_request(req_body)
    except Exception as e:
        logging.error(f"Orchestrator failed with an unhandled exception: {e}")
        error_response = {
            "response_data": {
                "status": "error",
                "session_id": req_body.get('session_id', 'N/A'),
                "error_message": f"An unexpected server error occurred: {str(e)}"
            }
        }
        return func.HttpResponse(json.dumps(error_response), status_code=500, mimetype="application/json")

    # Check if the response contains PowerPoint data
    if response_data.get("response_data", {}).get("powerpoint_output"):
        ppt_output = response_data["response_data"]["powerpoint_output"]
        ppt_base64 = ppt_output.get("ppt_data")
        filename = ppt_output.get("filename", "presentation.pptx")
        
        if ppt_base64:
            try:
                # Decode the base64 string back into bytes
                ppt_bytes = base64.b64decode(ppt_base64)
                
                # Create the full path to save the file
                output_filepath = os.path.join(LOCAL_OUTPUT_DIR, filename)
                
                # Write the bytes to a new .pptx file
                with open(output_filepath, "wb") as f:
                    f.write(ppt_bytes)
                
                logging.info(f"SUCCESS: PowerPoint file saved locally to: {output_filepath}")
                
                # Add a note to the response so you know it was saved
                response_data["response_data"]["local_save_path"] = output_filepath

            except Exception as e:
                logging.error(f"Failed to save file locally: {e}")
                # Add an error note to the response
                response_data["response_data"]["local_save_error"] = str(e)

    # Return the complete JSON response to the client
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        mimetype="application/json"
    )