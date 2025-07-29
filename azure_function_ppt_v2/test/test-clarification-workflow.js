/**
 * Test script for clarification questions workflow
 * Stage 1: User clicks "Create Presentation" → Get clarification questions popup
 * Stage 2: User answers questions → Generate customized PowerPoint
 */

const fs = require('fs');
const path = require('path');

// Test conversation history with robotics topic
const conversationHistoryExample = {
  "session_id": "c951086d-df7e-4c57-9f21-580f98516e3e",
  "total_questions": 3,
  "conversation": [
    {
      "question_id": "55d72dfe-2d96-4448-a4bb-1d7dc6fc7956",
      "question": "Tell me about robotics in Work place",
      "response_id": "e51e784f-2072-420f-86bd-3d6c4e38e57f",
      "response": "Robotics in the workplace refers to the integration and use of robotic systems—machines that can be programmed to perform tasks automatically—within various work environments, from factories to offices. Here's an overview of how robotics is impacting the workplace: **1. Manufacturing and Automation:** Robots have been used in manufacturing for decades. They handle repetitive tasks such as welding, painting, assembly, and packaging with high speed and accuracy. This increases productivity, reduces errors, and improves safety by taking over dangerous tasks. **2. Logistics and Warehousing:** In warehouses, robots move goods, sort packages, and manage inventory. Technologies like automated guided vehicles (AGVs) and robotic arms help organizations streamline operations and meet the demands of e-commerce. **3. Healthcare:** Robotics is widely used for precision surgeries (like the da Vinci robot), transportation of medications and supplies within hospitals, and supporting rehabilitation and elderly care. **4. Office and Service Industries:** Robotic Process Automation (RPA) refers to software robots that automate routine office tasks such as data entry, invoice processing, and report generation, freeing up employees for higher-value work. **5. Collaborative Robots (Cobots):** Unlike traditional industrial robots, cobots are designed to work safely alongside humans. They're being used in small and medium-sized businesses to assist with assembly, packaging, and even customer service.",
      "response_timestamp": "2025-07-29T06:02:15.905Z"
    },
    {
      "question_id": "ea0ac72d-f63f-4f40-8cac-25929ce9eb1b",
      "question": "What about the history of robotics?",
      "response_id": "cdee95d6-cffc-4eac-8ab1-9dc74309f06e",
      "response": "The history of robotics is a fascinating journey, stretching from ancient myths to the high-tech machines transforming industries today. Here's a quick overview: **Ancient Times** - Ancient stories (like Greek myths of mechanical servants) and simple mechanical automata, such as water clocks and moving statues, are the earliest imaginings of robots. **Renaissance to 18th Century** - Inventors like Leonardo da Vinci designed mechanical knights, and many clockmakers built elaborate automatons—mechanical dolls that could move, draw, or play instruments. **19th & Early 20th Century** - With the industrial revolution, automated machinery for weaving, printing, and other tasks began to appear. - In 1920, the word robot was first used by Czech playwright Karel Čapek in his play R.U.R. (Rossum's Universal Robots), referring to artificial workers.",
      "response_timestamp": "2025-07-29T06:02:41.329Z"
    },
    {
      "question_id": "929aa2ca-6d90-4da6-ae90-e245860e3093",
      "question": "Tell me about famous companies using robotics nowadays",
      "response_id": "93d934b1-e5cf-4df2-aa09-0cf947267ce0",
      "response": "Here are some companies that are widely recognized for their advanced use of robotics today: **1. Amazon** - Uses thousands of robots in its fulfillment centers for picking, sorting, and transporting packages. Their acquisition of Kiva Systems allowed massive automation of warehouses. **2. Tesla** - Employs robots extensively in its car manufacturing plants for welding, painting, assembling, and logistics. **3. Boston Dynamics** - Renowned for developing advanced, mobile robots such as Spot (robotic dog) and Atlas (humanoid robot). **4. FANUC** - A leading supplier of industrial robots, used in manufacturing plants worldwide, especially in the automotive and electronics industries.",
      "response_timestamp": "2025-07-29T06:10:58.305Z"
    }
  ]
};

async function testStage1_GetClarificationQuestions() {
    console.log('=== STAGE 1: Get Clarification Questions ===');
    
    const LOCAL_URL = 'http://localhost:7076/api/powerpointGeneration';

    const stage1Request = {
        user_message: "[create_presentation]",
        entra_id: "test-user-123",
        session_id: conversationHistoryExample.session_id,
        conversation_history: [conversationHistoryExample]
    };

    try {
        console.log('Sending Stage 1 request for clarification questions...');
        const response = await fetch(LOCAL_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(stage1Request)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        
        console.log('Status:', result.response_data.status);
        console.log('Show clarification popup:', result.response_data.show_clarification_popup);
        console.log('Response:', result.response_data.response_text);
        
        if (result.response_data.clarification_questions) {
            console.log('\n📋 Clarification Questions:');
            result.response_data.clarification_questions.forEach((q, index) => {
                console.log(`${index + 1}. ${q.question}`);
                console.log(`   Type: ${q.field_type}, Required: ${q.required}, Default: ${q.default_value}`);
                if (q.options) {
                    console.log(`   Options: ${q.options.join(', ')}`);
                }
                console.log('');
            });
        }
        
        return result.response_data.clarification_questions;

    } catch (error) {
        console.error('Stage 1 failed:', error.message);
        throw error;
    }
}

async function testStage2_GenerateWithAnswers(questions) {
    console.log('\n=== STAGE 2: Generate Presentation with Answers ===');
    
    const LOCAL_URL = 'http://localhost:7076/api/powerpointGeneration';
    
    // Simulate user answers to the clarification questions
    const userAnswers = {
        slide_count: 15,
        focus_area: "Workplace Integration", // If multiple topics detected
        audience_level: "Intermediate",
        include_examples: true,
        technical_depth: "Moderate detail" // For technical content
    };

    console.log('User answers:', JSON.stringify(userAnswers, null, 2));

    const stage2Request = {
        user_message: `[clarification_answers]${JSON.stringify(userAnswers)}`,
        entra_id: "test-user-123",
        session_id: conversationHistoryExample.session_id,
        conversation_history: [conversationHistoryExample]
    };

    try {
        console.log('Sending Stage 2 request with answers...');
        
        const response = await fetch(LOCAL_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(stage2Request)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        
        console.log('Status:', result.response_data.status);
        console.log('Pipeline used:', result.response_data.pipeline_info);
        
        if (result.response_data.processing_info.slide_estimate) {
            console.log('Slide count used:', result.response_data.processing_info.slide_estimate.estimated_slides);
            console.log('User specified:', result.response_data.processing_info.slide_estimate.user_specified);
        }
        
        if (result.response_data.powerpoint_output) {
            console.log('✅ Customized PowerPoint Generated!');
            console.log('Filename:', result.response_data.powerpoint_output.filename);
            console.log('File size:', result.response_data.powerpoint_output.file_size_kb, 'KB');
        }

        console.log('Final response:', result.response_data.response_text);
        return result;

    } catch (error) {
        console.error('Stage 2 failed:', error.message);
        throw error;
    }
}

async function testFullClarificationWorkflow() {
    console.log('Testing clarification questions workflow...\n');
    
    try {
        // Stage 1: Get clarification questions
        const questions = await testStage1_GetClarificationQuestions();
        
        // Stage 2: Generate with user answers
        await testStage2_GenerateWithAnswers(questions);
        
        console.log('\n✅ Clarification workflow completed successfully!');
        console.log('The presentation has been customized based on user answers.');
        
    } catch (error) {
        console.error('\n❌ Workflow failed:', error);
        process.exit(1);
    }
}

// Test different conversation types
async function testBusinessContent() {
    console.log('\n=== Testing Business Content Detection ===');
    
    const businessConversation = {
        "session_id": "business-test-123",
        "total_questions": 2,
        "conversation": [
            {
                "question_id": "1",
                "question": "Tell me about business strategy for digital transformation",
                "response": "Digital transformation strategy involves leveraging technology to fundamentally change business operations, customer experience, and value creation. Companies need to focus on data-driven decision making, automation, and digital customer touchpoints to remain competitive in the market."
            },
            {
                "question_id": "2", 
                "question": "What are the key revenue drivers for enterprise software companies?",
                "response": "Enterprise software companies typically focus on subscription revenue models, customer retention, expansion revenue from existing accounts, and strategic partnerships. The key is building sticky products that become integral to customer workflows."
            }
        ]
    };

    const request = {
        user_message: "[create_presentation]",
        entra_id: "test-user-123",
        session_id: "business-test-123",
        conversation_history: [businessConversation]
    };

    try {
        const response = await fetch('http://localhost:7076/api/powerpointGeneration', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        const result = await response.json();
        
        console.log('Business content questions generated:');
        result.response_data.clarification_questions.forEach((q, index) => {
            console.log(`${index + 1}. ${q.question} (${q.field_type})`);
        });
        
    } catch (error) {
        console.error('Business content test failed:', error.message);
    }
}

// Run the test if this file is executed directly
if (require.main === module) {
    testFullClarificationWorkflow()
        .then(() => testBusinessContent())
        .then(() => console.log('\n🎉 All tests completed!'));
}

module.exports = { 
    testStage1_GetClarificationQuestions, 
    testStage2_GenerateWithAnswers, 
    testFullClarificationWorkflow,
    conversationHistoryExample 
};