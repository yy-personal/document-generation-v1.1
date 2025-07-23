#!/usr/bin/env python3
"""
Simple POC Test for PowerPoint Generation Service

Tests the core functionality: Document input → PowerPoint output
"""

import requests
import json
import time

class PowerPointPOCTest:
    """Simple POC testing for the PowerPoint generation service"""
    
    def __init__(self, api_url="http://localhost:7072/api/powerpoint_generation"):
        self.api_url = api_url
        self.test_document = """Project Phoenix: Strategic Overview

1. Executive Summary
Project Phoenix is a company-wide initiative to modernize our legacy customer relationship management (CRM) platform. The primary goal is to improve operational efficiency, enhance data security, and provide a superior user experience for our sales and support teams.

2. Key Objectives
Our mission is to achieve three core objectives:
- Modernize Technology Stack: Migrate from the outdated on-premise system to a cloud-native, scalable architecture.
- Enhance User Experience: Design an intuitive and responsive user interface that minimizes training time and reduces user error.
- Improve Data Analytics: Implement a centralized data warehouse with real-time reporting dashboards to enable data-driven decision-making.

3. Project Timeline
The project is divided into three distinct phases:
- Phase 1 (Q3 2024): Discovery & Planning
- Phase 2 (Q4 2024 - Q1 2025): Development & Implementation  
- Phase 3 (Q2 2025): Testing & Deployment

4. Conclusion
Project Phoenix represents a significant investment in our technological infrastructure and is critical for long-term growth."""

    def check_service_available(self):
        """Check if the PowerPoint service is running"""
        try:
            response = requests.get("http://localhost:7072", timeout=5)
            return True
        except:
            return False

    def test_new_document_tag(self):
        """Test the new [document] tag format"""
        print("Testing new [document] tag...")
        
        test_request = {
            "user_message": f"[document]{self.test_document}",
            "entra_id": "poc-test-user"
        }
        
        return self._make_request(test_request, "New Document Tag")

    def test_legacy_tag_compatibility(self):
        """Test legacy tag still works for backward compatibility"""
        print("Testing legacy [word_document_extraction] tag...")
        
        test_request = {
            "user_message": f"[word_document_extraction]{self.test_document}",
            "entra_id": "poc-test-user"
        }
        
        return self._make_request(test_request, "Legacy Tag")

    def test_with_user_instruction(self):
        """Test with user instruction + document"""
        print("Testing with user instruction...")
        
        test_request = {
            "user_message": f"Create a professional presentation[document]{self.test_document}",
            "entra_id": "poc-test-user"
        }
        
        return self._make_request(test_request, "User Instruction")

    def _make_request(self, test_request, test_name):
        """Make API request and validate response"""
        start_time = time.time()
        
        try:
            response = requests.post(self.api_url, json=test_request, timeout=60)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Basic validation
                response_data = result.get('response_data', {})
                status = response_data.get('status')
                powerpoint_output = response_data.get('powerpoint_output')
                
                if status == 'completed' and powerpoint_output:
                    ppt_data = powerpoint_output.get('ppt_data', '')
                    filename = powerpoint_output.get('filename', 'N/A')
                    file_size_kb = len(ppt_data) // 1024 if ppt_data else 0
                    
                    print(f"  SUCCESS: {processing_time:.1f}s, {file_size_kb}KB, {filename}")
                    return True
                else:
                    print(f"  FAILED: Status={status}, No PowerPoint output")
                    return False
            else:
                print(f"  FAILED: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ERROR: {e}")
            return False

    def run_poc_tests(self):
        """Run the essential POC tests"""
        print("=" * 50)
        print("POWERPOINT GENERATION POC TEST")
        print("=" * 50)
        
        # Check service availability
        if not self.check_service_available():
            print("ERROR: PowerPoint service not available at localhost:7072")
            print("Start the service with: func start --port 7072")
            return False
        
        print("Service is available, running tests...\n")
        
        # Run tests
        tests = [
            ("Core Functionality (New Tag)", self.test_new_document_tag),
            ("Backward Compatibility", self.test_legacy_tag_compatibility),
            ("User Instructions", self.test_with_user_instruction)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"{test_name}:")
            success = test_func()
            results.append((test_name, success))
            print()
        
        # Summary
        print("=" * 50)
        print("POC TEST RESULTS")
        print("=" * 50)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "PASS" if success else "FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\nPOC VALIDATION: SUCCESS")
            print("The PowerPoint generation service is working correctly!")
        else:
            print(f"\nPOC VALIDATION: ISSUES DETECTED ({total-passed} failures)")
        
        return passed == total


def main():
    """Run POC tests"""
    tester = PowerPointPOCTest()
    success = tester.run_poc_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())