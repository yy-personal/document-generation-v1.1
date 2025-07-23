#!/usr/bin/env python3
"""
Test semantic kernel directly to see what's going wrong
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatMessageContent, AuthorRole
from config import get_ai_service

async def test_semantic_kernel():
    """Test semantic kernel directly"""
    print("Testing semantic kernel connection...")
    
    try:
        # Get AI service
        service, execution_settings = get_ai_service(max_tokens=500, temperature=0.3)
        print("AI service created successfully")
        
        # Create simple agent
        agent = ChatCompletionAgent(
            service=service,
            name="TestAgent",
            instructions="You are a helpful assistant. Respond with a simple JSON object."
        )
        print("Agent created successfully")
        
        # Prepare conversation with proper message objects
        conversation_history = [
            ChatMessageContent(role=AuthorRole.USER, content="Say hello in JSON format like {\"message\": \"hello\"}")
        ]
        arguments = KernelArguments(settings=execution_settings)
        
        print("Calling agent.get_response()...")
        response = await agent.get_response(
            messages=conversation_history,
            arguments=arguments
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        
        if hasattr(response, '__dict__'):
            print(f"Response attributes: {list(response.__dict__.keys())}")
        
        if isinstance(response, list) and len(response) > 0:
            print(f"Response is list with {len(response)} items")
            last_message = response[-1]
            print(f"Last message type: {type(last_message)}")
            print(f"Last message: {last_message}")
            
            if hasattr(last_message, 'content'):
                print(f"Content: {last_message.content}")
            else:
                print(f"Last message attributes: {list(last_message.__dict__.keys()) if hasattr(last_message, '__dict__') else 'No attributes'}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_semantic_kernel())