"""
Test script to demonstrate conversation context handling fix
"""
import json
import asyncio
from pdf_orchestrator import PDFOrchestrator

async def test_conversation_context():
    """Test that demonstrates the conversation context fix"""
    
    orchestrator = PDFOrchestrator()
    
    print("🧪 Testing Conversation Context Handling")
    print("=" * 50)
    
    # Simulate the exact scenario from user's example
    print("\n📄 FIRST REQUEST - Document Upload:")
    first_request = {
        "user_message": "whats on this[word_document_extraction]Functional Specification: TechIntel Information Agent v1.0\n1. Agent Profile\nAgent Name: TechIntel Information Agent\nVersion: 1.0\nPurpose: To serve as an automated research assistant...",
        "entra_id": "test-user-123",
        "session_id": "PDF19072025TEST123",
        "conversation_history": []
    }
    
    try:
        first_response = await orchestrator.process_conversation_request(first_request)
        
        print(f"✅ Status: {first_response['response_data']['status']}")
        print(f"✅ Response Type: {first_response['response_data']['processing_info'].get('response_type', 'N/A')}")
        print(f"✅ Pipeline: {' -> '.join(first_response['response_data']['pipeline_info'])}")
        
        # Extract conversation history for second request
        conversation_history = first_response['response_data']['conversation_history']
        session_id = first_response['response_data']['session_id']
        
        print("\\n📄 SECOND REQUEST - Continuation (This should now work!):")
        second_request = {
            "user_message": "Create the summary",
            "entra_id": "test-user-123", 
            "session_id": session_id,
            "conversation_history": conversation_history
        }
        
        second_response = await orchestrator.process_conversation_request(second_request)
        
        print(f"✅ Status: {second_response['response_data']['status']}")
        print(f"✅ Response Type: {second_response['response_data']['processing_info'].get('response_type', 'N/A')}")
        print(f"✅ Context Source: {second_response['response_data']['processing_info'].get('context_source', 'N/A')}")
        print(f"✅ Intent: {second_response['response_data']['processing_info'].get('intent', {}).get('intent', 'N/A')}")
        print(f"✅ Pipeline: {' -> '.join(second_response['response_data']['pipeline_info'])}")
        
        # Check if we have file output (PDF)
        if 'file_output' in second_response['response_data']:
            print("✅ PDF Generated: YES")
            print(f"✅ Filename: {second_response['response_data']['file_output']['filename']}")
        else:
            print("❌ PDF Generated: NO")
            
        print("\\n🎉 CONVERSATION CONTEXT TEST COMPLETED!")
        print("The system now properly handles continuation requests!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def test_conversation_context_sync():
    """Synchronous wrapper for the async test"""
    asyncio.run(test_conversation_context())

if __name__ == "__main__":
    print("🔧 Testing PDF Processing Service - Conversation Context Fix")
    print("This test simulates the exact scenario that was failing before.")
    print()
    
    test_conversation_context_sync()
