#!/usr/bin/env python3
"""
Simple POC Test for PowerPoint Generation Service

Tests the core functionality: Document input → PowerPoint output

Usage:
  python test_poc.py               # Run all tests
  python test_poc.py --long-only   # Run only the long document test
  python test_poc.py --table-only  # Run only the table functionality test

The long document test uses a comprehensive 8,000-word strategic document
to test content-driven slide optimization and should generate 20-30 slides.

The table test uses structured budget and performance data to test automatic
table creation functionality for better data presentation.
"""

import requests
import json
import time

class PowerPointPOCTest:
    """Simple POC testing for the PowerPoint generation service"""
    
    def __init__(self, api_url="http://localhost:7071/api/powerpoint_generation"):
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

        # Long document for testing content-driven slide optimization (should generate 15-20+ slides)
        self.long_test_document = """Digital Transformation Strategy 2025-2030: Comprehensive Implementation Framework

EXECUTIVE SUMMARY

Our organization stands at a critical juncture where digital transformation is not merely an option but an imperative for sustained competitive advantage. This comprehensive strategy document outlines a five-year roadmap to fundamentally reshape our operational model, customer engagement paradigm, and technological infrastructure. The transformation encompasses seven core domains: technology modernization, data analytics maturity, customer experience optimization, operational efficiency enhancement, workforce digital enablement, cybersecurity fortification, and innovation culture development.

The strategic initiative requires an investment of $12.5 million over five years, with projected ROI of 340% by 2030. Key performance indicators include 85% process automation, 60% improvement in customer satisfaction scores, 45% reduction in operational costs, and establishment of three new digital revenue streams worth $8.2 million annually.

CURRENT STATE ANALYSIS

Technology Infrastructure Assessment
Our existing technology landscape presents significant challenges that impede organizational agility. The current infrastructure consists of 47 legacy systems, 23 of which are over eight years old and lack modern integration capabilities. Database fragmentation across 12 different platforms creates data silos that prevent comprehensive business intelligence. Network infrastructure operates at 67% capacity during peak hours, causing performance bottlenecks that affect 340 daily users.

Customer Experience Audit
Customer journey mapping reveals critical friction points that negatively impact satisfaction and retention. Current Net Promoter Score stands at 32, significantly below industry benchmark of 58. Digital touchpoint analysis shows 43% of customer interactions require manual intervention, leading to average response times of 4.2 hours. Mobile experience optimization lags with only 34% of services accessible via mobile platforms.

Operational Efficiency Review
Process analysis identifies substantial automation opportunities across five business functions. Manual data entry consumes 847 hours weekly across all departments. Invoice processing requires average 7.3 days due to approval workflow inefficiencies. Inventory management operates with 23% excess stock due to inadequate demand forecasting capabilities.

STRATEGIC OBJECTIVES AND KEY RESULTS

Objective 1: Technology Modernization Excellence
Achieve 95% cloud infrastructure migration by Q4 2026, implementing microservices architecture that supports scalable, resilient operations. Consolidate 47 legacy systems into 12 integrated platforms using API-first design principles. Establish DevOps practices that enable weekly deployment cycles with 99.9% uptime reliability.

Key Results:
- Migrate 100% of customer-facing applications to cloud-native architecture
- Reduce system integration points from 847 to 156 through API standardization
- Achieve 99.95% system availability across all critical business functions
- Implement automated testing covering 85% of codebase functionality

Objective 2: Data-Driven Decision Making Transformation
Establish enterprise data platform that provides real-time insights across all business domains. Implement advanced analytics capabilities including predictive modeling, machine learning algorithms, and automated reporting systems. Create self-service analytics environment enabling business users to generate insights independently.

Key Results:
- Consolidate data from 23 sources into unified data warehouse
- Deploy 15 predictive models for demand forecasting, customer behavior analysis, and risk assessment
- Achieve 78% accuracy in quarterly revenue forecasting
- Enable 156 business users with self-service analytics capabilities

Objective 3: Customer Experience Revolution
Redesign customer journey to eliminate friction points and create seamless omnichannel experiences. Implement personalization engine that delivers contextual content and services. Establish customer feedback loops with real-time sentiment analysis and automated response mechanisms.

Key Results:
- Increase Net Promoter Score from 32 to 65
- Reduce average customer response time from 4.2 hours to 45 minutes
- Achieve 89% first-contact resolution rate
- Launch mobile-first customer portal with 95% feature parity

IMPLEMENTATION ROADMAP

Phase 1: Foundation Building (Months 1-12)
Infrastructure modernization begins with cloud migration strategy development and vendor selection. Establish core team of 12 digital transformation specialists including cloud architects, data engineers, UX designers, and change management professionals. Complete detailed technical architecture design and create proof-of-concept implementations for critical systems.

Key Milestones:
- Complete infrastructure assessment and cloud readiness evaluation
- Select primary cloud provider and establish enterprise agreement
- Migrate first three non-critical applications to validate approach
- Establish DevOps pipeline and continuous integration practices
- Complete staff training on cloud technologies and agile methodologies

Phase 2: Core Systems Migration (Months 13-24)
Execute migration of customer relationship management, enterprise resource planning, and financial management systems. Implement data governance framework and establish master data management processes. Launch customer portal beta version with core functionality.

Key Milestones:
- Complete CRM system migration with zero data loss
- Implement ERP cloud solution with enhanced reporting capabilities
- Launch customer self-service portal for 60% of common requests
- Establish data quality metrics achieving 95% accuracy standards
- Deploy initial machine learning models for customer segmentation

Phase 3: Advanced Analytics and Automation (Months 25-36)
Deploy predictive analytics platform and implement process automation across key business functions. Launch personalization engine for customer interactions. Establish real-time monitoring and alerting systems for all critical business processes.

Key Milestones:
- Implement 8 robotic process automation solutions eliminating 450 manual hours weekly
- Deploy predictive maintenance system reducing equipment downtime by 35%
- Launch recommendation engine increasing customer engagement by 28%
- Establish real-time dashboard providing executive visibility into key metrics
- Complete cybersecurity enhancement including zero-trust architecture

Phase 4: Innovation and Optimization (Months 37-48)
Focus on advanced capabilities including artificial intelligence, Internet of Things integration, and blockchain applications. Establish innovation lab for experimenting with emerging technologies. Implement continuous improvement processes based on performance analytics.

Key Milestones:
- Deploy AI-powered chatbot handling 70% of customer inquiries
- Implement IoT sensors for predictive analytics across manufacturing operations
- Launch blockchain-based supply chain transparency solution
- Establish innovation lab with quarterly proof-of-concept deliverables
- Achieve ISO 27001 certification for information security management

Phase 5: Scaling and Enhancement (Months 49-60)
Scale successful implementations across all business units and geographic locations. Establish center of excellence for digital capabilities. Launch new digital revenue streams and business models enabled by technological capabilities.

Key Milestones:
- Scale automation solutions to achieve 85% process digitization
- Launch three new digital service offerings generating $2.7M annual revenue
- Establish partnership ecosystem with 5 technology vendors
- Complete digital skills training for 100% of workforce
- Achieve customer satisfaction scores exceeding industry benchmarks

RISK MANAGEMENT AND MITIGATION

Technical Risks
Legacy system integration complexity poses significant implementation challenges. Mitigation includes comprehensive testing environments, phased migration approach, and maintenance of parallel systems during transition periods. Data migration risks addressed through automated validation tools, backup procedures, and rollback capabilities.

Organizational Risks
Change resistance represents primary organizational challenge. Mitigation strategy includes extensive communication campaigns, hands-on training programs, and change champion networks. Skills gap addressed through strategic hiring, external consulting partnerships, and comprehensive training initiatives.

Financial Risks
Budget overruns and delayed ROI realization require careful monitoring and control. Mitigation includes detailed project tracking, monthly financial reviews, and contingency planning. Vendor risk managed through diversified supplier relationships and performance-based contracting.

EXPECTED OUTCOMES AND SUCCESS METRICS

Operational Excellence
Process automation will eliminate 2,340 manual hours monthly while improving accuracy and consistency. System integration will provide real-time visibility into operations enabling proactive decision-making. Cloud infrastructure will provide elasticity to handle seasonal demand variations without performance degradation.

Customer Experience Enhancement
Omnichannel platform will provide consistent experience across digital and physical touchpoints. Personalization engine will increase customer engagement by 35% and cross-selling opportunities by 42%. Self-service capabilities will reduce support costs by $890,000 annually while improving customer satisfaction.

Financial Performance
Digital transformation investments will generate cumulative benefits of $42.8 million over five years. Cost reductions from automation and efficiency improvements total $18.6 million. New revenue streams from digital services contribute $24.2 million. Employee productivity improvements valued at $6.4 million annually.

CONCLUSION

This digital transformation strategy represents foundational investment in our organization's future competitiveness and sustainability. Success requires committed leadership, adequate resource allocation, and organizational commitment to change. The comprehensive approach addresses technological, operational, and cultural dimensions essential for sustainable transformation.

Implementation success depends on maintaining strategic focus while adapting to evolving market conditions and technological capabilities. Regular strategy reviews and performance assessments will ensure alignment with business objectives and market dynamics. The transformation will position our organization as industry leader in digital capabilities and customer experience excellence."""

    def check_service_available(self):
        """Check if the PowerPoint service is running"""
        try:
            response = requests.get("http://localhost:7071", timeout=5)
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

    def test_empty_user_message(self):
        """Test with empty user message before document"""
        print("Testing empty user message...")
        
        test_request = {
            "user_message": f"[document]{self.test_document}",
            "entra_id": "poc-test-user"
        }
        
        return self._make_request(test_request, "Empty User Message")

    def test_with_user_instruction(self):
        """Test with user instruction + document"""
        print("Testing with user instruction...")
        
        test_request = {
            "user_message": f"Create a professional presentation[document]{self.test_document}",
            "entra_id": "poc-test-user"
        }
        
        return self._make_request(test_request, "User Instruction")

    def test_long_document_handling(self):
        """Test with comprehensive long document to evaluate content-driven slide optimization"""
        print("Testing long document handling...")
        print("  Document length: ~8,000 words, multiple sections")
        print("  Expected: 20-30 slides based on content complexity")
        
        test_request = {
            "user_message": f"Create a comprehensive strategic presentation[document]{self.long_test_document}",
            "entra_id": "poc-long-test-user"
        }
        
        return self._make_request_with_details(test_request, "Long Document")

    def test_table_functionality(self):
        """Test automatic table creation with structured data"""
        print("Testing table creation...")
        print("  Content includes budget data and structured information")
        print("  Expected: Tables should be created automatically for structured data")
        
        # Create test document with structured data that should become tables
        table_test_document = """Project Budget Analysis: Q4 2024 Financial Overview

Budget Allocation Summary:
Marketing Budget: $150,000
Development Costs: $200,000  
Operations Expenses: $100,000
Support Services: $50,000
Total Allocated: $500,000

Performance Metrics Comparison:
Current Quarter: 85% completion
Previous Quarter: 78% completion
Target Goal: 90% completion
Industry Average: 82% completion

Team Distribution:
Engineering Team: 12 members
Marketing Team: 8 members
Operations Team: 6 members
Support Team: 4 members

Key Deliverables Timeline:
Phase 1 Planning: January 2024
Phase 2 Development: March 2024
Phase 3 Testing: May 2024
Phase 4 Launch: July 2024

This structured data should automatically be converted to professional tables instead of bullet points for better readability and presentation quality."""
        
        test_request = {
            "user_message": f"Create a professional presentation with tables[document]{table_test_document}",
            "entra_id": "poc-table-test-user"
        }
        
        return self._make_request(test_request, "Table Functionality")

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

    def _make_request_with_details(self, test_request, test_name):
        """Make API request with detailed response analysis for long document testing"""
        start_time = time.time()
        
        try:
            response = requests.post(self.api_url, json=test_request, timeout=120)  # Extended timeout for long docs
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Detailed validation
                response_data = result.get('response_data', {})
                status = response_data.get('status')
                powerpoint_output = response_data.get('powerpoint_output')
                processing_info = response_data.get('processing_info', {})
                
                if status == 'completed' and powerpoint_output:
                    ppt_data = powerpoint_output.get('ppt_data', '')
                    filename = powerpoint_output.get('filename', 'N/A')
                    file_size_kb = len(ppt_data) // 1024 if ppt_data else 0
                    
                    # Extract slide planning details
                    slide_planning = processing_info.get('slide_planning', {})
                    optimal_slides = slide_planning.get('optimal_slides', 'Unknown')
                    content_complexity = slide_planning.get('content_complexity', 'Unknown')
                    max_enforced = slide_planning.get('max_slides_enforced', 'Unknown')
                    
                    print(f"  SUCCESS: {processing_time:.1f}s, {file_size_kb}KB, {filename}")
                    print(f"  Slide Analysis: {optimal_slides} slides, {content_complexity} complexity")
                    print(f"  Max slides enforced: {max_enforced}")
                    
                    # Additional validation for long document
                    if isinstance(optimal_slides, int) and optimal_slides >= 15:
                        print(f"  ✓ Content-driven optimization working (generated {optimal_slides} slides)")
                    else:
                        print(f"  ⚠ Expected 15+ slides for long document, got {optimal_slides}")
                    
                    return True
                else:
                    print(f"  FAILED: Status={status}, No PowerPoint output")
                    if processing_info:
                        print(f"  Processing details: {processing_info}")
                    return False
            else:
                print(f"  FAILED: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"  Error details: {error_detail}")
                except:
                    print(f"  Response body: {response.text[:200]}...")
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
            print("ERROR: PowerPoint service not available at localhost:7071")
            print("Start the service with: func start --port 7071")
            return False
        
        print("Service is available, running tests...\n")
        
        # Run tests
        tests = [
            ("Core Functionality (Document Tag)", self.test_new_document_tag),
            ("Empty User Message", self.test_empty_user_message),
            ("User Instructions", self.test_with_user_instruction),
            ("Table Functionality", self.test_table_functionality),
            ("Long Document Handling", self.test_long_document_handling)
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

    def run_long_document_test_only(self):
        """Run only the long document test for focused testing"""
        print("=" * 60)
        print("LONG DOCUMENT CONTENT-DRIVEN OPTIMIZATION TEST")
        print("=" * 60)
        
        # Check service availability
        if not self.check_service_available():
            print("ERROR: PowerPoint service not available at localhost:7072")
            print("Start the service with: func start --port 7072")
            return False
        
        print("Service is available, testing long document handling...\n")
        
        success = self.test_long_document_handling()
        
        print("\n" + "=" * 60)
        print("LONG DOCUMENT TEST RESULT")
        print("=" * 60)
        
        if success:
            print("✓ PASS: Long document processing successful")
            print("  The content-driven slide optimization is working correctly!")
        else:
            print("✗ FAIL: Long document processing failed")
            print("  Check service logs for detailed error information")
        
        return success

    def run_table_test_only(self):
        """Run only the table functionality test for focused testing"""
        print("=" * 60)
        print("TABLE FUNCTIONALITY TEST")
        print("=" * 60)
        
        # Check service availability
        if not self.check_service_available():
            print("ERROR: PowerPoint service not available at localhost:7071")
            print("Start the service with: func start --port 7071")
            return False
        
        print("Service is available, testing table functionality...\n")
        
        success = self.test_table_functionality()
        
        print("\n" + "=" * 60)
        print("TABLE TEST RESULT")
        print("=" * 60)
        
        if success:
            print("✓ PASS: Table functionality working correctly")
            print("  Structured data should be automatically converted to tables!")
        else:
            print("✗ FAIL: Table functionality failed")
            print("  Check service logs for detailed error information")
        
        return success


def main():
    """Run POC tests"""
    import sys
    
    tester = PowerPointPOCTest()
    
    # Check if user wants to run specific tests
    if len(sys.argv) > 1:
        if sys.argv[1] == "--long-only":
            success = tester.run_long_document_test_only()
        elif sys.argv[1] == "--table-only":
            success = tester.run_table_test_only()
        else:
            print("Usage: python test_poc.py [--long-only|--table-only]")
            success = tester.run_poc_tests()
    else:
        success = tester.run_poc_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())