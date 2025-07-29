#!/usr/bin/env node

/**
 * Test script to verify document tag extraction functionality
 * Tests both new [document_start]/[document_end] and legacy [document] tags
 */

const { BaseAgent } = require('../src/agents/core/baseAgent');

class DocumentTagTest {
    constructor() {
        // Create a minimal agent instance to test document extraction
        this.agent = new class extends BaseAgent {
            constructor() {
                super('TestAgent');
            }
            async process(input) {
                return input;
            }
        }();
    }

    runTests() {
        console.log('=' .repeat(60));
        console.log('DOCUMENT TAG EXTRACTION TEST');
        console.log('=' .repeat(60));

        const tests = [
            {
                name: 'New format: [document_start] and [document_end]',
                input: 'Please analyze this document: [document_start]This is the document content with multiple lines.\nIt has various sections and detailed information.[document_end] What do you think?',
                expected: {
                    has_document: true,
                    document_content: 'This is the document content with multiple lines.\nIt has various sections and detailed information.',
                    user_text: 'Please analyze this document:  What do you think?'
                }
            },
            {
                name: 'Legacy format: [document] (backward compatibility)',
                input: 'Create presentation from [document]Legacy document content here',
                expected: {
                    has_document: true,
                    document_content: 'Legacy document content here',
                    user_text: 'Create presentation from'
                }
            },
            {
                name: 'No document tags',
                input: 'Create a presentation about artificial intelligence basics',
                expected: {
                    has_document: false,
                    document_content: null,
                    user_text: 'Create a presentation about artificial intelligence basics'
                }
            },
            {
                name: 'Document with complex content and user text',
                input: 'I need help with this report [document_start]Executive Summary:\nOur Q3 results show 15% growth.\n\nKey Metrics:\n- Revenue: $2.3M\n- Customers: 1,250\n- Retention: 89%[document_end] Can you make this into slides?',
                expected: {
                    has_document: true,
                    document_content: 'Executive Summary:\nOur Q3 results show 15% growth.\n\nKey Metrics:\n- Revenue: $2.3M\n- Customers: 1,250\n- Retention: 89%',
                    user_text: 'I need help with this report  Can you make this into slides?'
                }
            }
        ];

        let passed = 0;
        let total = tests.length;

        tests.forEach((test, index) => {
            console.log(`\nTest ${index + 1}: ${test.name}`);
            console.log('-'.repeat(50));
            
            try {
                const result = this.agent.extractDocumentContent(test.input);
                
                const success = this.compareResults(result, test.expected);
                
                if (success) {
                    console.log('✅ PASS');
                    passed++;
                } else {
                    console.log('❌ FAIL');
                    console.log('Expected:', JSON.stringify(test.expected, null, 2));
                    console.log('Got:', JSON.stringify(result, null, 2));
                }
            } catch (error) {
                console.log('❌ ERROR:', error.message);
            }
        });

        console.log('\n' + '='.repeat(60));
        console.log('TEST RESULTS SUMMARY');
        console.log('='.repeat(60));
        console.log(`Passed: ${passed}/${total} tests`);
        
        if (passed === total) {
            console.log('\n🎉 ALL TESTS PASSED!');
            console.log('Document tag extraction is working correctly.');
        } else {
            console.log(`\n⚠️  ${total - passed} TEST(S) FAILED`);
            console.log('Document tag extraction needs fixes.');
        }

        return passed === total;
    }

    compareResults(actual, expected) {
        return (
            actual.has_document === expected.has_document &&
            actual.document_content === expected.document_content &&
            actual.user_text.trim() === expected.user_text.trim()
        );
    }
}

// Run tests if called directly
if (require.main === module) {
    const tester = new DocumentTagTest();
    const success = tester.runTests();
    process.exit(success ? 0 : 1);
}

module.exports = { DocumentTagTest };