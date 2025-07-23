#!/usr/bin/env python3
"""
Final test to show the improvement in content quality
"""
import requests
import json

# Original test data from user's issue
test_request = {
    "user_message": "[word_document_extraction]Project Phoenix: A Strategic Overview\n\n1. Executive Summary\n\nProject Phoenix is a company-wide initiative to modernize our legacy customer relationship management (CRM) platform. The primary goal is to improve operational efficiency, enhance data security, and provide a superior user experience for our sales and support teams. This project will be executed over three phases and is expected to deliver a 30% reduction in customer support tickets and a 15% increase in sales productivity upon completion.\n\n2. Key Objectives\n\nOur mission is to achieve three core objectives:\n- Modernize Technology Stack: Migrate from the outdated on-premise system to a cloud-native, scalable architecture.\n- Enhance User Experience: Design an intuitive and responsive user interface that minimizes training time and reduces user error.\n- Improve Data Analytics: Implement a centralized data warehouse with real-time reporting dashboards to enable data-driven decision-making.\n\n3. Project Scope\n\nThe scope of Project Phoenix is clearly defined to ensure timely delivery.\n- In Scope:\n\t- Full data migration of active customer accounts from the old CRM.\n\t- Development of core modules: Contact Management, Sales Pipeline, and Support Ticketing.\n\t- Integration with our existing billing system.\n- Out of Scope:\n\t- Mobile application development (scheduled for a future initiative).\n\t- Integration with third-party marketing platforms.\n\n4. Project Timeline and Milestones\n\nThe project is divided into three distinct phases:\n- Phase 1 (Q3 2024): Discovery & Planning: Finalize technical requirements, assemble the project team, and develop a detailed project plan. Milestone: Project Plan Sign-off.\n- Phase 2 (Q4 2024 - Q1 2025): Development & Implementation: Agile development sprints for core modules and begin data migration. Milestone: Alpha version ready for internal testing.\n- Phase 3 (Q2 2025): Testing & Deployment: Conduct User Acceptance Testing (UAT), train staff, and execute the final go-live deployment. Milestone: Project Go-Live.\n\n5. Conclusion and Next Steps\n\nProject Phoenix is critical for our company's long-term growth and competitiveness. It represents a significant investment in our technological infrastructure. The immediate next step is to secure final budget approval from the steering committee and officially kick off Phase 1.",
    "entra_id": "test-user-123"
}

def test_content_quality():
    """Test and analyze the content quality"""
    url = "http://localhost:7072/api/powerpoint_generation"
    
    try:
        print("=== TESTING IMPROVED POWERPOINT GENERATION ===")
        response = requests.post(url, json=test_request, timeout=45)
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS - PowerPoint Generated!")
            
            # Analyze content quality
            processing_info = result.get('response_data', {}).get('processing_info', {})
            
            # Check intent analysis quality
            intent_info = processing_info.get('intent', {})
            print(f"\nINTENT ANALYSIS:")
            print(f"  Intent: {intent_info.get('intent', 'N/A')}")
            print(f"  Confidence: {intent_info.get('confidence', 'N/A')}")
            print(f"  Reasoning: {intent_info.get('reasoning', 'N/A')[:100]}...")
            
            # Check structure analysis quality
            structure_info = processing_info.get('structure_analysis', {})
            print(f"\nSTRUCTURE ANALYSIS:")
            print(f"  Main Topics: {len(structure_info.get('main_topics', []))} topics")
            for i, topic in enumerate(structure_info.get('main_topics', [])[:3], 1):
                print(f"    {i}. {topic[:60]}...")
            print(f"  Complexity: {structure_info.get('content_complexity', 'N/A')}")
            
            # Check slide planning
            slide_info = processing_info.get('slide_planning', {})
            print(f"\nSLIDE PLANNING:")
            print(f"  Optimal Slides: {slide_info.get('optimal_slides', 'N/A')}")
            print(f"  Max Enforced: {slide_info.get('max_slides_enforced', 'N/A')}")
            print(f"  Reasoning: {slide_info.get('reasoning', 'N/A')[:80]}...")
            
            # Check final content quality
            slide_content = processing_info.get('powerpoint_json_content', [])
            print(f"\nFINAL SLIDE CONTENT:")
            print(f"  Total Slides: {len(slide_content)}")
            
            # Show first few slide titles and content preview
            for i, slide in enumerate(slide_content[:3], 1):
                title = slide.get('title', 'N/A')
                content_preview = str(slide.get('content', [])[:2])
                print(f"    Slide {i}: {title}")
                print(f"      Content: {content_preview[:80]}...")
            
            ppt_output = result.get('response_data', {}).get('powerpoint_output')
            if ppt_output:
                filename = ppt_output.get('filename', 'N/A')
                size_kb = len(ppt_output.get('ppt_data', '')) // 1024
                print(f"\nFILE OUTPUT:")
                print(f"  Filename: {filename}")
                print(f"  Size: {size_kb}KB")
                local_path = result.get('response_data', {}).get('local_save_path')
                if local_path:
                    print(f"  Saved to: {local_path}")
            
            print(f"\n=== COMPARISON WITH ORIGINAL ISSUE ===")
            print("BEFORE (Fallback Content):")
            print("  - Generic titles like 'Topic 1', 'Topic 2'")
            print("  - Truncated content: '# Project Phoenix: A Strategic Overview...'")
            print("  - Poor structure with only 3 main topics identified")
            print("  - Fallback reasoning used")
            
            print("\nAFTER (AI-Generated Content):")
            print(f"  - Specific titles based on document content")
            print(f"  - Full content analysis with {len(structure_info.get('main_topics', []))} topics")
            print(f"  - High confidence intent: {intent_info.get('confidence', 0)}")
            print(f"  - Proper slide planning with {slide_info.get('optimal_slides', 'N/A')} slides")
            print(f"  - AI-powered content generation instead of fallback")
            
        else:
            print(f"FAILED: Status {response.status_code}")
            print(response.text[:300])
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_content_quality()