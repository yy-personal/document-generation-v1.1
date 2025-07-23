import asyncio
import json
from agents.powerpoint_builder_agent import PowerPointBuilderAgent

# This is the "perfect" JSON data that the SlideContentGenerator *should* create.
# It's a list of dictionaries, where each dictionary is a slide.
SIMPLE_SLIDE_DATA = [
    {
        "title": "Project Kick-off: Agenda",
        "content": [
            "Introduction of Team Members",
            "Review of Project Goals",
            "Discussion of Timeline & Milestones"
        ],
        "layout": "TITLE_SLIDE"
    },
    {
        "title": "Project Goals",
        "content": [
            "Goal 1: Develop the core feature set.",
            "Goal 2: Complete user testing by end of Q3.",
            "Goal 3: Prepare for market launch in Q4."
        ],
        "layout": "CONTENT_SLIDE"
    },
    {
        "title": "Next Steps",
        "content": [
            "Finalize technical specifications this week.",
            "Schedule first sprint planning meeting.",
            "Distribute preliminary documentation to stakeholders."
        ],
        "layout": "CONTENT_SLIDE"
    }
]

async def run_test():
    """
    This function tests the PowerPointBuilderAgent in isolation.
    """
    print("--- Starting PowerPoint Builder Test ---")
    
    # 1. Instantiate the builder agent (just like the orchestrator does)
    builder = PowerPointBuilderAgent()
    
    # 2. Convert our simple slide data into a JSON string, which is what the agent expects
    slide_content_json = json.dumps(SIMPLE_SLIDE_DATA)
    
    print("Input to agent:\n", slide_content_json)
    
    # 3. Call the agent's process method to generate the PPTX bytes
    try:
        ppt_bytes = await builder.process(slide_content_json)
        
        # 4. Save the resulting bytes to a file so you can open it
        output_filename = "test_output.pptx"
        with open(output_filename, "wb") as f:
            f.write(ppt_bytes)
            
        print(f"\nSUCCESS: A readable PowerPoint file named '{output_filename}' has been created.")
        print("Please open it to verify it contains 3 slides with text.")

    except Exception as e:
        print(f"\nERROR: The test failed. Error: {e}")

# Run the asynchronous test function
if __name__ == "__main__":
    asyncio.run(run_test())