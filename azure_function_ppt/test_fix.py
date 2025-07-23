#!/usr/bin/env python3
"""
Quick test to verify the PowerPoint generation fixes work
"""
import requests
import json
import base64

# Test data
test_request = {
    "user_message": "[word_document_extraction]Project Phoenix: A Strategic Overview\n\n1. Executive Summary\n\nProject Phoenix is a company-wide initiative to modernize our legacy customer relationship management (CRM) platform. The primary goal is to improve operational efficiency, enhance data security, and provide a superior user experience for our sales and support teams. This project will be executed over three phases and is expected to deliver a 30% reduction in customer support tickets and a 15% increase in sales productivity upon completion.\n\n2. Key Objectives\n\nOur mission is to achieve three core objectives:\n- Modernize Technology Stack: Migrate from the outdated on-premise system to a cloud-native, scalable architecture.\n- Enhance User Experience: Design an intuitive and responsive user interface that minimizes training time and reduces user error.\n- Improve Data Analytics: Implement a centralized data warehouse with real-time reporting dashboards to enable data-driven decision-making.\n\n3. Project Scope\n\nThe scope of Project Phoenix is clearly defined to ensure timely delivery.\n- In Scope:\n\t- Full data migration of active customer accounts from the old CRM.\n\t- Development of core modules: Contact Management, Sales Pipeline, and Support Ticketing.\n\t- Integration with our existing billing system.\n- Out of Scope:\n\t- Mobile application development (scheduled for a future initiative).\n\t- Integration with third-party marketing platforms.\n\n4. Project Timeline and Milestones\n\nThe project is divided into three distinct phases:\n- Phase 1 (Q3 2024): Discovery & Planning: Finalize technical requirements, assemble the project team, and develop a detailed project plan. Milestone: Project Plan Sign-off.\n- Phase 2 (Q4 2024 - Q1 2025): Development & Implementation: Agile development sprints for core modules and begin data migration. Milestone: Alpha version ready for internal testing.\n- Phase 3 (Q2 2025): Testing & Deployment: Conduct User Acceptance Testing (UAT), train staff, and execute the final go-live deployment. Milestone: Project Go-Live.\n\n5. Conclusion and Next Steps\n\nProject Phoenix is critical for our company's long-term growth and competitiveness. It represents a significant investment in our technological infrastructure. The immediate next step is to secure final budget approval from the steering committee and officially kick off Phase 1.",
    "entra_id": "test-user-123"
}

def test_powerpoint_generation():
    """Test the PowerPoint generation endpoint"""
    url = "http://localhost:7072/api/powerpoint_generation"
    
    try:
        print("Testing PowerPoint generation...")
        print("Sending request to:", url)
        
        response = requests.post(url, json=test_request, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS!")
            print(f"Session ID: {result.get('response_data', {}).get('session_id', 'N/A')}")
            print(f"Status: {result.get('response_data', {}).get('status', 'N/A')}")
            
            # Check if PowerPoint was generated
            ppt_output = result.get('response_data', {}).get('powerpoint_output')
            if ppt_output:
                print(f"PowerPoint generated: {ppt_output.get('filename', 'N/A')}")
                print(f"File size: {len(ppt_output.get('ppt_data', '')) // 1024}KB (base64)")
            else:
                print("No PowerPoint output found")
            
            # Check pipeline info
            pipeline = result.get('response_data', {}).get('pipeline_info', [])
            print(f"Pipeline: {' -> '.join(pipeline)}")
            
        else:
            print(f"FAILED with status {response.status_code}")
            print("Response:", response.text[:500])
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_powerpoint_generation()