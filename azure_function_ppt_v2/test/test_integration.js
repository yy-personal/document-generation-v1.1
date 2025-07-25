/**
 * Integration Test for PowerPoint Generation v2
 */
const axios = require('axios');

// Test configuration
const API_BASE_URL = 'http://localhost:7071/api';
const TEST_TIMEOUT = 120000; // 2 minutes

// Sample test document content
const SAMPLE_DOCUMENT = `
Business Analysis Report

Executive Summary
This document presents a comprehensive analysis of market opportunities in the technology sector.
Our research indicates significant potential for growth and expansion.

Market Analysis
The technology market has shown consistent growth of 15% annually over the past three years.
Key drivers include digital transformation initiatives and increased cloud adoption.
Competitive landscape remains fragmented with opportunities for new entrants.

Financial Projections
- Revenue projection: $5M in Year 1, $12M in Year 2
- Initial investment required: $2M
- Break-even point: 18 months
- Projected ROI: 200% over 3 years

Strategic Recommendations
1. Immediate market entry with core product offering
2. Strategic partnerships with established technology vendors
3. Aggressive marketing campaign targeting enterprise customers
4. Investment in R&D for next-generation capabilities

Risk Assessment
Primary risks include market saturation, competitive response, and technology disruption.
Mitigation strategies have been developed for each identified risk factor.

Implementation Timeline
Phase 1: Product development and testing (6 months)
Phase 2: Market launch and initial customer acquisition (12 months)  
Phase 3: Scale operations and expand market presence (18 months)

Conclusion
The market opportunity presents a compelling business case with strong financial returns.
Immediate action is recommended to capitalize on current market conditions.
`;

class IntegrationTester {
    constructor() {
        this.testResults = [];
    }

    async runAllTests() {
        console.log('🚀 Starting PowerPoint Generation v2 Integration Tests');
        console.log('=' .repeat(60));

        try {
            await this.testHealthEndpoint();
            await this.testBasicPresentationGeneration();
            await this.testContinuationRequest();
            await this.testNoDocumentRequest();
            await this.testErrorHandling();
            
            this.printTestSummary();
            
        } catch (error) {
            console.error('❌ Test suite failed:', error.message);
            process.exit(1);
        }
    }

    async testHealthEndpoint() {
        console.log('\n📊 Testing Health Endpoint...');
        
        try {
            const response = await axios.get(`${API_BASE_URL}/health_v2`, {
                timeout: 5000
            });
            
            this.assert(response.status === 200, 'Health endpoint should return 200');
            this.assert(response.data.status === 'healthy', 'Health status should be healthy');
            this.assert(response.data.version === '2.0.0', 'Version should be 2.0.0');
            this.assert(response.data.architecture === 'hybrid', 'Architecture should be hybrid');
            
            console.log('✅ Health endpoint test passed');
            this.testResults.push({ test: 'Health Endpoint', status: 'PASSED' });
            
        } catch (error) {
            console.error('❌ Health endpoint test failed:', error.message);
            this.testResults.push({ test: 'Health Endpoint', status: 'FAILED', error: error.message });
        }
    }

    async testBasicPresentationGeneration() {
        console.log('\n📊 Testing Basic Presentation Generation...');
        
        try {
            const requestBody = {
                user_message: `Create a professional presentation from this document [document]${SAMPLE_DOCUMENT}`,
                conversation_history: []
            };
            
            const response = await axios.post(`${API_BASE_URL}/powerpoint_generation_v2`, requestBody, {
                timeout: TEST_TIMEOUT,
                headers: { 'Content-Type': 'application/json' }
            });
            
            this.assert(response.status === 200, 'Should return 200 status');
            
            const data = response.data;
            this.assert(data.response_data, 'Should have response_data');
            this.assert(data.response_data.status === 'completed', 'Status should be completed');
            this.assert(data.response_data.powerpoint_output, 'Should have powerpoint_output');
            this.assert(data.response_data.powerpoint_output.ppt_data, 'Should have base64 PowerPoint data');
            this.assert(data.response_data.powerpoint_output.filename, 'Should have filename');
            
            // Validate processing info
            const processingInfo = data.response_data.processing_info;
            this.assert(processingInfo.architecture === 'hybrid', 'Should use hybrid architecture');
            this.assert(processingInfo.presentation_engine === 'pptxgenjs', 'Should use PptxGenJS');
            
            console.log(`✅ Generated presentation with ${data.response_data.powerpoint_output.slides_count} slides`);
            console.log(`📁 Local file: ${data.response_data.local_save_path}`);
            
            this.testResults.push({ test: 'Basic Presentation Generation', status: 'PASSED' });
            
        } catch (error) {
            console.error('❌ Basic presentation generation test failed:', error.message);
            this.testResults.push({ test: 'Basic Presentation Generation', status: 'FAILED', error: error.message });
        }
    }

    async testContinuationRequest() {
        console.log('\n📊 Testing Continuation Request...');
        
        try {
            // First, send document
            const initialRequest = {
                user_message: `Here's my business document [document]${SAMPLE_DOCUMENT}`,
                conversation_history: []
            };
            
            // Then, request presentation creation
            const continuationRequest = {
                user_message: 'Create a presentation from this',
                conversation_history: [
                    { role: 'user', content: initialRequest.user_message },
                    { role: 'assistant', content: 'I have received your business document.' }
                ]
            };
            
            const response = await axios.post(`${API_BASE_URL}/powerpoint_generation_v2`, continuationRequest, {
                timeout: TEST_TIMEOUT,
                headers: { 'Content-Type': 'application/json' }
            });
            
            this.assert(response.status === 200, 'Should return 200 status');
            this.assert(response.data.response_data.status === 'completed', 'Should complete presentation generation');
            this.assert(response.data.response_data.powerpoint_output, 'Should generate PowerPoint');
            
            console.log('✅ Continuation request test passed');
            this.testResults.push({ test: 'Continuation Request', status: 'PASSED' });
            
        } catch (error) {
            console.error('❌ Continuation request test failed:', error.message);
            this.testResults.push({ test: 'Continuation Request', status: 'FAILED', error: error.message });
        }
    }

    async testNoDocumentRequest() {
        console.log('\n📊 Testing No Document Request...');
        
        try {
            const requestBody = {
                user_message: 'Can you help me create a presentation?',
                conversation_history: []
            };
            
            const response = await axios.post(`${API_BASE_URL}/powerpoint_generation_v2`, requestBody, {
                timeout: 10000,
                headers: { 'Content-Type': 'application/json' }
            });
            
            this.assert(response.status === 200, 'Should return 200 status');
            this.assert(response.data.response_data.status === 'waiting_for_file', 'Should be waiting for file');
            this.assert(response.data.response_data.capabilities, 'Should provide capabilities info');
            
            console.log('✅ No document request test passed');
            this.testResults.push({ test: 'No Document Request', status: 'PASSED' });
            
        } catch (error) {
            console.error('❌ No document request test failed:', error.message);
            this.testResults.push({ test: 'No Document Request', status: 'FAILED', error: error.message });
        }
    }

    async testErrorHandling() {
        console.log('\n📊 Testing Error Handling...');
        
        try {
            // Test with invalid JSON
            const response = await axios.post(`${API_BASE_URL}/powerpoint_generation_v2`, 'invalid json', {
                timeout: 10000,
                headers: { 'Content-Type': 'application/json' }
            });
            
            // Should not reach here, but if it does, check for error response
            this.assert(response.status >= 400, 'Should return error status for invalid JSON');
            
        } catch (error) {
            // Axios throws for 4xx/5xx status codes, which is expected
            if (error.response && error.response.status === 400) {
                console.log('✅ Error handling test passed (correctly rejected invalid JSON)');
                this.testResults.push({ test: 'Error Handling', status: 'PASSED' });
            } else {
                throw error;
            }
        }
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(`Assertion failed: ${message}`);
        }
    }

    printTestSummary() {
        console.log('\n' + '='.repeat(60));
        console.log('📋 TEST SUMMARY');
        console.log('='.repeat(60));
        
        let passed = 0;
        let failed = 0;
        
        this.testResults.forEach(result => {
            const status = result.status === 'PASSED' ? '✅' : '❌';
            console.log(`${status} ${result.test}: ${result.status}`);
            
            if (result.error) {
                console.log(`   Error: ${result.error}`);
            }
            
            if (result.status === 'PASSED') passed++;
            else failed++;
        });
        
        console.log('\n' + '-'.repeat(40));
        console.log(`Total Tests: ${this.testResults.length}`);
        console.log(`Passed: ${passed}`);
        console.log(`Failed: ${failed}`);
        console.log(`Success Rate: ${Math.round((passed / this.testResults.length) * 100)}%`);
        
        if (failed === 0) {
            console.log('\n🎉 All tests passed! PowerPoint Generation v2 is working correctly.');
        } else {
            console.log(`\n⚠️  ${failed} test(s) failed. Please review the errors above.`);
        }
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    const tester = new IntegrationTester();
    tester.runAllTests().catch(error => {
        console.error('Test execution failed:', error);
        process.exit(1);
    });
}

module.exports = IntegrationTester;