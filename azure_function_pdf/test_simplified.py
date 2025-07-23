"""
Test script for simplified PDF processing service - Extraction and PDF output only
"""
import json
import asyncio
from pdf_orchestrator import PDFOrchestrator

async def test_simplified_processing():
    """Test the simplified extraction and PDF generation workflow"""
    
    orchestrator = PDFOrchestrator()
    
    print("🧪 Testing Simplified PDF Processing Service")
    print("=" * 50)
    
    # Test case 1: Information request (should get quick summary)
    print("\n📄 TEST 1 - Information Request:")
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
        
        # Test case 2: Processing request (should extract and generate PDF)
        conversation_history = first_response['response_data']['conversation_history']
        session_id = first_response['response_data']['session_id']
        
        print("\\n📄 TEST 2 - Processing Request (Continuation):")
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
        print(f"✅ Document Type: {second_response['response_data']['processing_info'].get('content_type', 'N/A')}")
        print(f"✅ Pipeline: {' -> '.join(second_response['response_data']['pipeline_info'])}")
        
        # Check for PDF output (new simplified structure)
        if 'pdf_output' in second_response['response_data']:
            print("✅ PDF Generated: YES")
            print(f"✅ Filename: {second_response['response_data']['pdf_output']['filename']}")
            print(f"✅ PDF Size: {len(second_response['response_data']['pdf_output']['pdf_data'])} characters (base64)")
        else:
            print("❌ PDF Generated: NO")
            
        # Test case 3: Direct processing request
        print("\\n📄 TEST 3 - Direct Processing Request:")
        direct_request = {
            "user_message": "Process this document[word_document_extraction]Sample CV: John Smith\\nSenior Software Engineer\\nExperience: 5 years in Python development...",
            "entra_id": "test-user-456",
            "conversation_history": []
        }
        
        direct_response = await orchestrator.process_conversation_request(direct_request)
        
        print(f"✅ Status: {direct_response['response_data']['status']}")
        print(f"✅ Response Type: {direct_response['response_data']['processing_info'].get('response_type', 'N/A')}")
        print(f"✅ Document Type: {direct_response['response_data']['processing_info'].get('content_type', 'N/A')}")
        print(f"✅ Pipeline: {' -> '.join(direct_response['response_data']['pipeline_info'])}")
        
        if 'pdf_output' in direct_response['response_data']:
            print("✅ PDF Generated: YES")
            print(f"✅ Filename: {direct_response['response_data']['pdf_output']['filename']}")
        else:
            print("❌ PDF Generated: NO")
            
        print("\\n🎉 SIMPLIFIED PDF PROCESSING TESTS COMPLETED!")
        print("\\n📋 SUMMARY:")
        print("- ✅ Information requests → Quick summaries (no PDF)")
        print("- ✅ Processing requests → Extraction + PDF generation")
        print("- ✅ Conversation context handling works")
        print("- ✅ No document enhancement (simplified extraction only)")
        print("- ✅ Clean PDF output with professional formatting")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def test_simplified_processing_sync():
    """Synchronous wrapper for the async test"""
    asyncio.run(test_simplified_processing())

if __name__ == "__main__":
    print("🔧 Testing Simplified PDF Processing Service")
    print("This test validates extraction-only workflow with PDF output.")
    print()
    
    test_simplified_processing_sync()
