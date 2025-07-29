/**
 * Test script for conversation history workflow
 * Tests the new use case where:
 * 1. User has chat conversation history
 * 2. User clicks "Create PowerPoint" button
 * 3. Popup asks for slide count
 * 4. System generates presentation from conversation content
 */

const fs = require('fs');
const path = require('path');

// Test conversation history from your example
const conversationHistoryExample = {
  "session_id": "c951086d-df7e-4c57-9f21-580f98516e3e",
  "total_questions": 3,
  "conversation": [
    {
      "question_id": "55d72dfe-2d96-4448-a4bb-1d7dc6fc7956",
      "question": "Tell me about robotics in Work place",
      "response_id": "e51e784f-2072-420f-86bd-3d6c4e38e57f",
      "response": "Robotics in the workplace refers to the integration and use of robotic systems—machines that can be programmed to perform tasks automatically—within various work environments, from factories to offices. Here's an overview of how robotics is impacting the workplace: **1. Manufacturing and Automation:** Robots have been used in manufacturing for decades. They handle repetitive tasks such as welding, painting, assembly, and packaging with high speed and accuracy. This increases productivity, reduces errors, and improves safety by taking over dangerous tasks. **2. Logistics and Warehousing:** In warehouses, robots move goods, sort packages, and manage inventory. Technologies like automated guided vehicles (AGVs) and robotic arms help organizations streamline operations and meet the demands of e-commerce. **3. Healthcare:** Robotics is widely used for precision surgeries (like the da Vinci robot), transportation of medications and supplies within hospitals, and supporting rehabilitation and elderly care. **4. Office and Service Industries:** Robotic Process Automation (RPA) refers to software robots that automate routine office tasks such as data entry, invoice processing, and report generation, freeing up employees for higher-value work. **5. Collaborative Robots (Cobots):** Unlike traditional industrial robots, cobots are designed to work safely alongside humans. They're being used in small and medium-sized businesses to assist with assembly, packaging, and even customer service. ### **Benefits** - Increased efficiency and speed - Improved safety - Consistent quality - Cost savings over time ### **Challenges** - High initial investment - Need for employee retraining and upskilling - Potential job displacement concerns - Integration with existing systems ### **Future Trends** With advances in Artificial Intelligence (AI) and Machine Learning (ML), robots are becoming smarter and more adaptable, able to handle complex tasks and interact more naturally with human coworkers. In summary, robotics is transforming various aspects of the workplace, making operations more efficient but also requiring businesses to adapt through workforce development and thoughtful integration.",
      "response_timestamp": "2025-07-29T06:02:15.905Z"
    },
    {
      "question_id": "ea0ac72d-f63f-4f40-8cac-25929ce9eb1b",
      "question": "What about the history of robotics?",
      "response_id": "cdee95d6-cffc-4eac-8ab1-9dc74309f06e",
      "response": "The history of robotics is a fascinating journey, stretching from ancient myths to the high-tech machines transforming industries today. Here's a quick overview: **Ancient Times** - Ancient stories (like Greek myths of mechanical servants) and simple mechanical automata, such as water clocks and moving statues, are the earliest imaginings of robots. **Renaissance to 18th Century** - Inventors like Leonardo da Vinci designed mechanical knights, and many clockmakers built elaborate automatons—mechanical dolls that could move, draw, or play instruments. **19th & Early 20th Century** - With the industrial revolution, automated machinery for weaving, printing, and other tasks began to appear. - In 1920, the word robot was first used by Czech playwright Karel Čapek in his play R.U.R. (Rossum's Universal Robots), referring to artificial workers. **Post-World War II Era (1940s–1960s)** - Real advances in robotics began as technology improved. - In 1954, George Devol invented the first programmable robot, called Unimate. It was installed in a General Motors factory in 1961, revolutionizing manufacturing. **Late 20th Century** - Robotics technology spread from factories to new fields like medicine, exploration, and entertainment. - Mobile robots, industrial robots, and early experimental robots began taking shape. **21st Century** - Robotics advanced rapidly with developments in AI (Artificial Intelligence), sensors, and computing. - Robots moved beyond manufacturing to healthcare, homes, service industries, and even space and deep-sea exploration. **Today** - Robots can be autonomous, collaborative (cobots), or controlled by humans, and they continue to become smarter, more adaptable, and accessible. In short, robotics evolved from ancient dreams and mechanical curiosities to essential tools in modern society, with continued growth thanks to advances in AI, engineering, and sensor technology.",
      "response_timestamp": "2025-07-29T06:02:41.329Z"
    },
    {
      "question_id": "929aa2ca-6d90-4da6-ae90-e245860e3093",
      "question": "Tell me why are some companies that are famous for using robotics nowadays",
      "response_id": "93d934b1-e5cf-4df2-aa09-0cf947267ce0",
      "response": "Certainly, Yin Yao! Here are some companies that are widely recognized for their advanced use of robotics today, along with a quick note on what they're known for: **1. Amazon** - Uses thousands of robots in its fulfillment centers for picking, sorting, and transporting packages. Their acquisition of Kiva Systems allowed massive automation of warehouses. **2. Tesla** - Employs robots extensively in its car manufacturing plants for welding, painting, assembling, and logistics. Tesla's Gigafactories are famous for their robot-driven production lines. **3. Boston Dynamics** - Renowned for developing advanced, mobile robots such as Spot (robotic dog) and Atlas (humanoid robot). Their robots showcase impressive agility and AI-driven movement. **4. FANUC** - A leading supplier of industrial robots, used in manufacturing plants worldwide, especially in the automotive and electronics industries. **5. ABB** - This Swiss-based company provides robotic solutions for automation in various sectors including automotive, electronics, and food and beverage industries. **6. Foxconn** - Major supplier for Apple and other electronics giants, known for deploying thousands of assembly robots (Foxbots) in its factories in China. **7. Google (Alphabet)** - Through subsidiaries like Intrinsic and formerly Boston Dynamics, Google invests in AI and robotics for manufacturing, logistics, and everyday assistance. **8. iRobot** - Makers of the Roomba robotic vacuum, iRobot brought robotics into millions of homes worldwide, setting standards for consumer robotics. **Why these companies stand out:** - They use robotics not just for efficiency and cost savings, but also for innovation, safety, product quality, and sometimes even entirely new business models. - Their high-profile use of robotics often shapes industry trends and encourages broader adoption globally. If you want details about robotics in any specific company or industry, let me know!",
      "response_timestamp": "2025-07-29T06:10:58.305Z"
    }
  ]
};

async function testConversationWorkflow() {
    console.log('Testing conversation history workflow...\n');

    const LOCAL_URL = 'http://localhost:7071/api/powerpointGeneration';

    // Test case 1: User wants to create presentation with 15 slides
    const testRequest = {
        user_message: "Create PowerPoint presentation with 15 slides",
        entra_id: "test-user-123",
        session_id: conversationHistoryExample.session_id,
        conversation_history: [conversationHistoryExample]
    };

    try {
        console.log('Sending request to PowerPoint service...');
        console.log('Request payload:', JSON.stringify(testRequest, null, 2));

        const response = await fetch(LOCAL_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(testRequest)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('\n=== Response received ===');
        console.log('Status:', result.response_data.status);
        console.log('Pipeline used:', result.response_data.pipeline_info);
        
        if (result.response_data.processing_info.slide_estimate) {
            console.log('Slide estimate:', result.response_data.processing_info.slide_estimate.estimated_slides);
            console.log('User specified:', result.response_data.processing_info.slide_estimate.user_specified);
        }

        if (result.response_data.powerpoint_output) {
            console.log('PowerPoint generated!');
            console.log('Filename:', result.response_data.powerpoint_output.filename);
            console.log('File size:', result.response_data.powerpoint_output.file_size_kb, 'KB');
        }

        console.log('\nResponse text:', result.response_data.response_text);

        return result;

    } catch (error) {
        console.error('Test failed:', error.message);
        throw error;
    }
}

// Run the test if this file is executed directly
if (require.main === module) {
    testConversationWorkflow()
        .then(() => {
            console.log('\n✅ Conversation workflow test completed successfully');
        })
        .catch((error) => {
            console.error('\n❌ Test failed:', error);
            process.exit(1);
        });
}

module.exports = { testConversationWorkflow, conversationHistoryExample };