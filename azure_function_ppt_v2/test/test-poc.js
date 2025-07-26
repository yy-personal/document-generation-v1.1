#!/usr/bin/env node

/**
 * Test script for PowerPoint Generation Service v2
 * Tests the conversational interface and agent pipeline
 */

const http = require('http');
const { getApiUrl, getLocalUrl } = require('../src/config/config');

class PowerPointV2Test {
    constructor(apiUrl = getApiUrl()) {
        this.apiUrl = apiUrl;
        this.testDocument = `Digital Marketing Strategy 2024

Executive Summary
Our company needs to modernize its digital marketing approach to compete effectively in the evolving marketplace. This strategy focuses on three key areas: social media engagement, content marketing excellence, and data-driven decision making.

Key Objectives
1. Increase brand awareness by 40% through targeted social media campaigns
2. Generate 25% more qualified leads through content marketing initiatives  
3. Improve customer retention by 15% using personalized marketing automation

Implementation Plan
Phase 1: Social Media Optimization (Q1 2024)
- Audit current social media presence across all platforms
- Develop content calendar with daily posting schedule
- Implement social listening tools for brand monitoring
- Launch influencer partnership program

Phase 2: Content Marketing Excellence (Q2 2024)  
- Create comprehensive content library including blogs, videos, and infographics
- Implement SEO best practices to improve organic search rankings
- Develop email marketing campaigns with personalized messaging
- Launch customer success story program

Phase 3: Data-Driven Optimization (Q3-Q4 2024)
- Implement advanced analytics tracking across all digital channels
- Create automated reporting dashboards for real-time insights
- Develop A/B testing framework for continuous improvement
- Launch predictive analytics for customer behavior forecasting

Expected Results
By the end of 2024, we anticipate:
- 40% increase in social media engagement rates
- 25% growth in website traffic from organic search
- 30% improvement in email open rates through personalization
- 15% increase in customer lifetime value

Budget Requirements
Total investment: $125,000 across 12 months
- Technology and tools: $45,000
- Content creation: $35,000  
- Advertising spend: $30,000
- Training and development: $15,000

Success Metrics
We will measure success through:
- Monthly brand awareness surveys
- Lead quality scoring and conversion rates
- Customer satisfaction and retention metrics
- Revenue attribution to digital marketing channels`;
    }

    async checkServiceAvailability() {
        return new Promise((resolve) => {
            const req = http.get(getLocalUrl(), (res) => {
				resolve(true);
			});
            
            req.on('error', () => {
                resolve(false);
            });
            
            req.setTimeout(5000, () => {
                req.destroy();
                resolve(false);
            });
        });
    }

    async makeRequest(requestData, testName) {
        return new Promise((resolve, reject) => {
            const postData = JSON.stringify(requestData);
            
            const { LOCAL_DEV_CONFIG } = require('../src/config/config');
            const options = {
				hostname: LOCAL_DEV_CONFIG.host,
				port: LOCAL_DEV_CONFIG.port,
				path: LOCAL_DEV_CONFIG.api_path,
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"Content-Length": Buffer.byteLength(postData),
				},
				timeout: 60000,
			};

            const startTime = Date.now();
            const req = http.request(options, (res) => {
                let data = '';
                
                res.on('data', (chunk) => {
                    data += chunk;
                });
                
                res.on('end', () => {
                    const processingTime = (Date.now() - startTime) / 1000;
                    
                    try {
                        const result = JSON.parse(data);
                        resolve({ ...result, processingTime, statusCode: res.statusCode });
                    } catch (error) {
                        reject(new Error(`Failed to parse response: ${error.message}`));
                    }
                });
            });

            req.on('error', (error) => {
                reject(new Error(`Request failed: ${error.message}`));
            });

            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Request timed out'));
            });

            req.write(postData);
            req.end();
        });
    }

    async testConversationalFlow() {
        console.log('Testing Conversational Flow...\n');

        try {
            // Test 1: Document upload with question
            console.log('Test 1: Document upload with clarifying question');
            const test1Request = {
                user_message: `What kind of presentation would work best for this? [document]${this.testDocument}`,
                entra_id: 'test-user-1'
            };

            const test1Response = await this.makeRequest(test1Request, 'Document Question');
            console.log(`Status: ${test1Response.statusCode}`);
            console.log(`Time: ${test1Response.processingTime.toFixed(1)}s`);
            console.log(`Pipeline: ${test1Response.response_data?.pipeline_info?.join(' → ') || 'N/A'}`);
            console.log(`Response: ${test1Response.response_data?.response_text?.substring(0, 100)}...`);
            console.log(`Should Generate: ${test1Response.response_data?.processing_info?.conversation?.should_generate_presentation}`);

            // Get session context for next test
            const sessionId = test1Response.response_data?.session_id;
            const conversationHistory = test1Response.response_data?.conversation_history || [];

            // Test 2: Follow-up conversation
            console.log('\nTest 2: Follow-up conversation');
            const test2Request = {
                user_message: 'Make it focus on the implementation timeline and key metrics',
                session_id: sessionId,
                conversation_history: conversationHistory,
                entra_id: 'test-user-1'
            };

            const test2Response = await this.makeRequest(test2Request, 'Follow-up Context');
            console.log(`Status: ${test2Response.statusCode}`);
            console.log(`Time: ${test2Response.processingTime.toFixed(1)}s`);
            console.log(`Response: ${test2Response.response_data?.response_text?.substring(0, 100)}...`);
            console.log(`Estimated Slides: ${test2Response.response_data?.processing_info?.slide_estimate?.estimated_slides || 'N/A'}`);

            // Test 3: Generation request
            console.log('\nTest 3: Presentation generation request');
            const test3Request = {
                user_message: 'Create the presentation now',
                session_id: sessionId,
                conversation_history: test2Response.response_data?.conversation_history || [],
                entra_id: 'test-user-1'
            };

            const test3Response = await this.makeRequest(test3Request, 'Generate Presentation');
            console.log(`Status: ${test3Response.statusCode}`);
            console.log(`Time: ${test3Response.processingTime.toFixed(1)}s`);
            console.log(`Pipeline: ${test3Response.response_data?.pipeline_info?.join(' → ') || 'N/A'}`);
            
            if (test3Response.response_data?.powerpoint_output) {
                const pptOutput = test3Response.response_data.powerpoint_output;
                console.log(`PowerPoint Generated: YES`);
                console.log(`Filename: ${pptOutput.filename}`);
                console.log(`File Size: ${pptOutput.file_size_kb}KB`);
                console.log(`Slide Count: ${pptOutput.slide_count}`);
            } else {
                console.log(`PowerPoint Generated: NO`);
            }

            return true;

        } catch (error) {
            console.error(`Conversational flow test failed: ${error.message}`);
            return false;
        }
    }

    async testServiceStatus() {
        console.log('Testing Service Status...\n');

        try {
            const response = await this.makeRequest({}, 'Service Status');
            console.log(`Status: ${response.statusCode}`);
            console.log(`Service Info:`, response);
            return response.statusCode === 200;
        } catch (error) {
            console.error(`Service status test failed: ${error.message}`);
            return false;
        }
    }

    async runTests() {
        console.log('=' .repeat(60));
        console.log('POWERPOINT GENERATION V2 - POC TEST');
        console.log('=' .repeat(60));

        // Check service availability
        console.log('Checking service availability...');
        const isAvailable = await this.checkServiceAvailability();
        
        if (!isAvailable) {
            const { LOCAL_DEV_CONFIG } = require('../src/config/config');
            console.log(`Service not available at ${LOCAL_DEV_CONFIG.host}:${LOCAL_DEV_CONFIG.port}`);
            console.log('Start the service with:');
            console.log('  cd azure_function_ppt_v2');
            console.log('  npm install');
            console.log('  npm start');
            return false;
        }

        console.log('Service is available\n');

        // Run tests
        const tests = [
            { name: 'Service Status', fn: () => this.testServiceStatus() },
            { name: 'Conversational Flow', fn: () => this.testConversationalFlow() }
        ];

        const results = [];
        
        for (const test of tests) {
            console.log(`\n${'='.repeat(40)}`);
            console.log(`TEST: ${test.name.toUpperCase()}`);
            console.log(`${'='.repeat(40)}`);
            
            try {
                const success = await test.fn();
                results.push({ name: test.name, success });
            } catch (error) {
                console.error(`${test.name} failed:`, error.message);
                results.push({ name: test.name, success: false });
            }
        }

        // Summary
        console.log('\n' + '='.repeat(60));
        console.log('TEST RESULTS SUMMARY');
        console.log('='.repeat(60));

        const passed = results.filter(r => r.success).length;
        const total = results.length;

        results.forEach(result => {
            const status = result.success ? 'PASS' : 'FAIL';
            console.log(`${result.name}: ${status}`);
        });

        console.log(`\nOverall: ${passed}/${total} tests passed`);

        if (passed === total) {
            console.log('\nALL TESTS PASSED!');
            console.log('The PowerPoint Generation v2 service is working correctly.');
        } else {
            console.log(`\n${total - passed} TEST(S) FAILED`);
            console.log('Check the service logs for detailed error information.');
        }

        return passed === total;
    }
}

// Run tests if called directly
if (require.main === module) {
    const tester = new PowerPointV2Test();
    tester.runTests().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error('Test execution failed:', error);
        process.exit(1);
    });
}

module.exports = { PowerPointV2Test };