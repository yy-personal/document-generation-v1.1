# PowerPoint Requirements Service v2 - Complete Function Explanation

## Overview

The PowerPoint Requirements Service v2 is an intelligent preprocessing service that transforms conversational content into structured presentation requirements for third-party PowerPoint generators. It operates as a 2-stage clarification workflow using AI agents to analyze content and gather user preferences.

## Architecture Overview

```
Frontend Request → Azure Function (index.js) → PowerPointOrchestrator → AI Agents → Structured Requirements Output
```

### Key Components

1. **Azure Function Entry Point** (`powerpointGeneration/index.js`)
2. **PowerPointOrchestrator** (`src/orchestrator/pptOrchestrator.js`)
3. **ConversationManager Agent** (`src/agents/conversationManager_agent.js`)
4. **ClarificationQuestionGenerator Agent** (`src/agents/clarificationQuestionGenerator_skill.js`)
5. **Configuration System** (`src/config/config.js`)
6. **Centralized Prompt Management** (`src/prompts/`)

---

## Detailed Step-by-Step Flow

### Step 1: Azure Function Entry Point
**File**: `powerpointGeneration/index.js:3-53`

```javascript
module.exports = async function (context, req) {
    // GET request returns service status
    if (req.method === 'GET') {
        return service status and version info
    }
    
    // POST request processing
    const orchestrator = new PowerPointOrchestrator();
    const response = await orchestrator.processConversationRequest(req.body);
    return JSON response;
}
```

**What happens:**
- Handles both GET (status check) and POST (processing) requests
- Creates a new PowerPointOrchestrator instance
- Delegates all processing logic to the orchestrator
- Returns structured JSON responses with error handling

### Step 2: Request Processing Initialization
**File**: `src/orchestrator/pptOrchestrator.js:20-51`

```javascript
async processConversationRequest(requestData) {
    // Extract request data with database field mapping
    const {
        user_message,
        sessionhistory_entra_id: entra_id,
        sessionhistory_session_id,
        conversation_history = []
    } = requestData;

    // Initialize response structure
    const response = {
        response_data: {
            status: 'processing',
            session_id: sessionId,
            conversation_history: conversation_history,
            response_text: '',
            powerpoint_output: null,
            processing_info: {}
        }
    };
}
```

**What happens:**
- Extracts user message, session ID, and conversation history from request
- Maps database field names (e.g., `sessionhistory_entra_id` → `entra_id`)
- Initializes standardized response structure with processing metadata
- Sets up conversation history tracking

### Step 3: ConversationManager Processing
**File**: `src/orchestrator/pptOrchestrator.js:52-66`

```javascript
// Step 1: Conversation Management
const conversationResult = await this.agents.ConversationManager.process({
    user_message,
    session_id: sessionId,
    conversation_history,
    entra_id
});
```

**What the ConversationManager does** (`src/agents/conversationManager_agent.js`):

#### 3a. Bracket Trigger Detection
**File**: `src/agents/conversationManager_agent.js:190-223`

```javascript
detectBracketTriggers(userMessage) {
    // Stage 1: [create_presentation]
    if (normalizedMessage.includes('[create_presentation]')) {
        return { type: 'create_presentation', stage: 1 };
    }

    // Stage 2: [clarification_answers]{JSON}
    const answersMatch = normalizedMessage.match(/\[clarification_answers\](.+)/);
    if (answersMatch) {
        return { type: 'clarification_answers', stage: 2, answers: parsedAnswers };
    }
}
```

#### 3b. Conversation Content Extraction
**File**: `src/agents/conversationManager_agent.js:277-307`

```javascript
extractConversationContent(conversationHistory) {
    // Handle new Q&A format
    if (conversationHistory[0] && conversationHistory[0].conversation) {
        conversations.forEach((conv, index) => {
            content += `Topic ${index + 1}: ${conv.question}\n`;
            content += `Details: ${conv.response}\n\n`;
        });
    }
    return content;
}
```

#### 3c. AI Analysis (when needed)
**File**: `src/agents/conversationManager_agent.js:66-84`

For non-trigger messages, uses AI with centralized prompts to:
- Analyze user intent and context
- Determine if presentation generation is needed
- Extract document content if present
- Maintain conversation flow

### Step 4: Workflow Stage Determination
**File**: `src/orchestrator/pptOrchestrator.js:75-85`

```javascript
// Determine workflow stage
const shouldGeneratePresentation = conversationResult.should_generate_presentation;
const showSlideRecommendation = conversationResult.show_slide_recommendation;
const showClarificationQuestions = conversationResult.show_clarification_questions;
const needSlideEstimation = conversationResult.need_slide_estimation;
const clarificationAnswers = conversationResult.clarification_answers;
```

**The system determines one of four paths:**
1. **Stage 1**: Show clarification questions with AI slide estimation
2. **Stage 2**: Process clarification answers and generate requirements
3. **Legacy Stage 1**: Direct slide recommendation
4. **Regular Conversation**: No presentation workflow

---

## Stage 1: Clarification Questions Generation

### Step 5a: AI Slide Estimation + Question Generation
**File**: `src/orchestrator/pptOrchestrator.js:86-131`

```javascript
if (showClarificationQuestions && needSlideEstimation) {
    // Stage 1: Get AI slide recommendation, then generate clarification questions
    const clarificationInput = {
        conversation_content: conversationResult.conversation_content,
        conversation_history: conversation_history,
        requested_slide_count: conversationResult.requested_slide_count
    };
    
    const clarificationResult = await this.agents.ClarificationQuestionGenerator.process(clarificationInput);
}
```

### Step 6a: ClarificationQuestionGenerator Processing
**File**: `src/agents/clarificationQuestionGenerator_skill.js:14-80`

#### 6a.1: Content Analysis with AI
**File**: `src/agents/clarificationQuestionGenerator_skill.js:83-125`

```javascript
createCombinedUserPrompt({ conversation_content, document_content, conversation_history }) {
    return `Analyze this content and perform BOTH slide estimation AND question generation:

## Conversation Content:
${conversation_content}

## Your Task:
1. **Slide Estimation**: Analyze content complexity, volume, and structure
2. **Content Analysis**: Identify content type, themes, and complexity factors  
3. **Question Generation**: Generate 3-4 highly relevant questions (select/boolean only)
4. Ensure questions help customize the presentation for maximum value

## Examples of Analysis:
**For Business Content:**
- Questions: "What's your primary audience role?" (select with options)
- Content Focus: "What level of detail should we include?" (select with options)

**IMPORTANT**: ALWAYS include "Let agent decide" as the FIRST option in ALL select questions`;
}
```

#### 6a.2: AI Response Processing
The AI analyzes content and returns:
- **Estimated slide count** based on content complexity and volume
- **Content analysis** identifying themes, technical level, and structure
- **3-4 contextual questions** dynamically generated based on content type
- **Reasoning** for slide count recommendation

#### 6a.3: Slide Range Generation
**File**: `src/agents/clarificationQuestionGenerator_skill.js:128-153`

```javascript
addSlideCountQuestion(generatedQuestions, aiRecommendedSlides) {
    const slideRange = this.generateSlideRange(aiRecommendedSlides);
    
    const slideCountQuestion = {
        id: "slide_count",
        question: `How many slides would you like? (Recommended: ${aiRecommendedSlides} slides based on AI analysis)`,
        field_type: "select",
        options: slideRange, // 11 options around AI recommendation
        default_value: aiRecommendedSlides,
        recommendation: aiRecommendedSlides,
        ai_generated: true
    };
    
    return [slideCountQuestion, ...generatedQuestions];
}
```

**Range generation logic** (`src/agents/clarificationQuestionGenerator_skill.js:155-198`):
- Creates ±15 slides around AI recommendation in steps of 3
- Ensures 11 total options within system bounds (3-60 slides)
- Always includes the AI-recommended count

### Step 7a: Stage 1 Response Assembly
**File**: `src/orchestrator/pptOrchestrator.js:104-131`

```javascript
response.response_data.processing_info.slide_estimate = {
    estimated_slides: clarificationResult.estimated_slides,
    content_complexity: clarificationResult.content_complexity,
    slide_breakdown: clarificationResult.slide_breakdown,
    reasoning: clarificationResult.reasoning,
    confidence: clarificationResult.confidence
};

response.response_data.show_clarification_popup = true;
response.response_data.clarification_questions = clarificationQuestions;
response.response_data.response_text = "Please answer these questions to customize your presentation:";
```

**Stage 1 Output Example:**
```json
{
  "response_data": {
    "show_clarification_popup": true,
    "clarification_questions": [
      {
        "id": "slide_count",
        "question": "How many slides would you like? (Recommended: 12 slides based on AI analysis)",
        "field_type": "select",
        "options": [3, 6, 9, 12, 15, 18, 21, 24, 27],
        "default_value": 12
      },
      {
        "id": "audience_level",
        "question": "What is the technical level of your audience?",
        "field_type": "select", 
        "options": ["Let agent decide", "Beginner", "Intermediate", "Advanced"],
        "default_value": "Let agent decide"
      }
    ],
    "processing_info": {
      "slide_estimate": {
        "estimated_slides": 12,
        "content_complexity": "moderate",
        "reasoning": "Content covers multiple stock market topics requiring detailed explanation"
      }
    }
  }
}
```

---

## Stage 2: Requirements Processing

### Step 5b: Clarification Answers Processing
**File**: `src/orchestrator/pptOrchestrator.js:207-269`

```javascript
// Stage 2: Process clarification answers and return consolidated information
const clarificationAnswers = conversationResult.clarification_answers;

// Finalize slide count based on user's choice
let finalSlideCount = PRESENTATION_CONFIG.default_slides;
if (clarificationAnswers && clarificationAnswers.slide_count) {
    finalSlideCount = parseInt(clarificationAnswers.slide_count);
}

// Prepare user preferences object
const userPreferences = {
    slide_count: finalSlideCount,
    ...this.extractAllUserPreferences(clarificationAnswers)
};
```

### Step 6b: Content Consolidation
**File**: `src/orchestrator/pptOrchestrator.js:229-235`

```javascript
// Use ConversationManager to generate a unified content_summary
const consolidationResult = await this.agents.ConversationManager.process({
    user_message: '[consolidate_info]',
    conversation_history: conversation_history,
    clarification_answers: clarificationAnswers
});
const contentSummary = consolidationResult.consolidated_summary;
```

#### 6b.1: ConversationManager Consolidation
**File**: `src/agents/conversationManager_agent.js:20-53`

```javascript
// Special: Consolidate info trigger
if (user_message && user_message.trim().startsWith('[consolidate_info]')) {
    // Load consolidation system prompt from file
    const systemPrompt = promptLoader.loadPrompt('consolidation_system');

    // Build user prompt with conversation history and clarification answers
    let userPrompt = `## Conversation History:\n`;
    // Extract Q&A pairs from conversation_history
    
    userPrompt += `\n## Clarified Presentation Preferences:\n`;
    // Add user's clarification answers
    
    userPrompt += `\n## Task:\nWrite a single, well-structured summary that combines the above into clear presentation requirements.`;
    
    const aiResponse = await this.callAI(messages);
    return { consolidated_summary: aiResponse.content };
}
```

### Step 7b: Final Requirements Assembly  
**File**: `src/orchestrator/pptOrchestrator.js:237-268`

```javascript
// Prepare final consolidated information for third-party service
const consolidatedInfo = {
    // Unified summary generated by agent
    content_summary: contentSummary,

    // Rich context fields (for traceability/debugging)
    user_context: conversationResult.user_context || "",
    main_topics: this.extractMainTopics(this.extractOriginalConversation(conversation_history)),
    intent: conversationResult.intent || "",
    reasoning: conversationResult.reasoning || "",

    // User's presentation preferences from clarification answers
    user_preferences: userPreferences
};

response.response_data.consolidated_info = consolidatedInfo;
response.response_data.response_text = `Presentation requirements processed successfully. ${finalSlideCount} slides will be created.`;
```

**Stage 2 Output Example:**
```json
{
  "response_data": {
    "status": "completed",
    "consolidated_info": {
      "content_summary": "The presentation will provide an intermediate-level overview of the stock market with 12 slides covering market fundamentals, key players, and investment strategies. Content should include practical examples and focus on educating an intermediate audience about stock market basics and notable prediction methodologies.",
      "user_preferences": {
        "slide_count": 12,
        "audience_level": "Intermediate", 
        "content_depth": "Moderate detail",
        "include_examples": true
      },
      "main_topics": [
        {
          "topic_id": 1,
          "topic_question": "Tell me about the stock market",
          "topic_summary": "Stock market basics and fundamentals..."
        }
      ],
      "intent": "PRESENTATION_GENERATE"
    },
    "response_text": "Presentation requirements processed successfully. 12 slides will be created based on your preferences."
  }
}
```

---

## Configuration System

### Environment Configuration
**File**: `src/config/config.js:14-35`

```javascript
const loadEnvironment = () => {
    // Check if running in Azure vs local development
    if (process.env.WEBSITE_SITE_NAME) {
        console.log('Running in Azure - using Function App environment variables');
    } else {
        console.log('Running locally - loading from root .env file');
    }
    
    const requiredEnvVars = ['ENDPOINT_URL', 'DEPLOYMENT_NAME', 'AZURE_OPENAI_API_KEY', 'API_VERSION'];
    // Validate all required environment variables
};
```

### Agent Configuration
**File**: `src/config/config.js:64-76`

```javascript
const AGENT_CONFIGS = {
    ConversationManager: {
        max_tokens: 20000,  // High for context and consolidation
        temperature: 0.3,   // Focused analysis
        purpose: "Manage conversation flow, understand user intent, and maintain context"
    },
    
    ClarificationQuestionGenerator: {
        max_tokens: 8000,   // Medium-high for slide estimation + questions
        temperature: 0.4,   // Balanced creativity for questions
        purpose: "Analyze content complexity and generate contextual clarification questions"
    }
};
```

### Presentation Limits
**File**: `src/config/config.js:42-47`

```javascript
const PRESENTATION_CONFIG = {
    max_slides: 60,        // Maximum allowed slides (hard limit)
    min_slides: 3,         // Minimum slides for proper presentation structure  
    default_slides: 12,    // Default target when content complexity is medium
    use_case: "Conversational presentation planning and requirements gathering"
};
```

---

## Centralized Prompt Management

### Prompt Loading System
**File**: `src/utils/promptLoader.js`

```javascript
const promptLoader = {
    loadPrompt: function(promptName) {
        const promptPath = path.join(__dirname, '../prompts', `${promptName}.txt`);
        return fs.readFileSync(promptPath, 'utf8');
    }
};
```

### Available Prompts
**Directory**: `src/prompts/`

1. **`conversation_manager_system.txt`** - System prompt for ConversationManager agent
2. **`clarification_question_generator_system.txt`** - System prompt for question generation and slide estimation  
3. **`consolidation_system.txt`** - System prompt for final requirements consolidation

This ensures:
- Consistent AI behavior across deployments
- Easy prompt updates without code changes
- Version control for prompt evolution
- Separation of logic from AI instructions

---

## Error Handling and Resilience

### JSON Parsing Tolerance
**File**: `src/agents/conversationManager_agent.js:314-377`

```javascript
parseAnswersWithTolerance(rawJsonString) {
    // Strategy 1: Try direct parsing first
    try {
        return JSON.parse(rawJsonString);
    } catch (error) {}

    // Strategy 2: Clean and repair common JSON issues
    // - Remove extra quotes, braces, commas
    // - Fix unescaped quotes in values
    
    // Strategy 3: Extract key-value pairs using regex (last resort)
    // - Pattern matching for "key": "value" pairs
    // - Convert boolean and number strings
}
```

### AI Response Fallbacks  
**File**: `src/agents/conversationManager_agent.js:384-430`

```javascript
parseAIResponse(content) {
    try {
        return JSON.parse(content);
    } catch (error) {
        // Fallback 1: Extract JSON from markdown code blocks
        const jsonMatch = content.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
        
        // Fallback 2: Extract response_text from malformed JSON
        // Ultimate fallback: Return clean default structure
        return {
            should_generate_presentation: false,
            response_text: "I understand your message. Please let me know if you'd like to create a presentation.",
            error_info: { parsing_fallback_used: true }
        };
    }
}
```

### Request Processing Error Handling
**File**: `src/orchestrator/pptOrchestrator.js:271-283`

```javascript
} catch (error) {
    console.error('Error in orchestrator:', error);
    
    return {
        response_data: {
            status: 'error',
            session_id: requestData.sessionhistory_session_id || 'unknown',
            error_message: error.message,
            conversation_history: requestData.conversation_history || []
        }
    };
}
```

---

## Third-Party Service Integration

### Output Format for PowerPoint Generators
The `consolidated_info.content_summary` is specifically structured for third-party PowerPoint generation services:

```javascript
// Stage 2 output ready for external PowerPoint generators
{
  "consolidated_info": {
    "content_summary": "Slide-by-slide presentation structure with titles, key points, layout suggestions, and content organization based on conversation history and user preferences",
    "user_preferences": {
      "slide_count": 12,
      "audience_level": "Intermediate",
      "content_depth": "Moderate detail"
    }
  }
}
```

### Integration Benefits
1. **Separation of Concerns**: Requirements gathering vs PowerPoint generation
2. **AI Optimization**: Complex conversation analysis handled by specialized agents  
3. **Flexibility**: Third-party service can focus on layout and formatting excellence
4. **Scalability**: Requirements service can support multiple PowerPoint generators
5. **Quality**: Rich context and user preferences ensure high-quality output

---

## Performance Characteristics

### Processing Times
- **Stage 1 (Questions)**: 2-3 seconds for AI slide recommendation + contextual question generation
- **Stage 2 (Processing)**: 6-9 seconds for requirements consolidation and structured output generation  
- **Total Processing Time**: 8-12 seconds for complete requirements preprocessing

### AI Efficiency
- **2 AI calls total**: ClarificationQuestionGenerator + ConversationManager consolidation
- **Memory Usage**: <300MB per request (lightweight processing, no PowerPoint generation)
- **Token Optimization**: Tailored token limits per agent type and purpose

### Scalability Features
- **Stateless agents**: Each request is independent
- **Session management**: Conversation history preserved across stages
- **Error resilience**: Multiple fallback strategies for robust processing
- **Configuration-driven**: Easy adjustment of limits and behaviors

---

## Summary

The PowerPoint Requirements Service v2 is a sophisticated 2-stage AI workflow that:

1. **Analyzes conversational content** to understand presentation needs
2. **Generates intelligent clarification questions** with AI-powered slide recommendations  
3. **Processes user preferences** to create structured presentation requirements
4. **Outputs consolidated information** ready for third-party PowerPoint generation services

The system emphasizes **intelligent preprocessing**, **user customization**, and **seamless integration** with external PowerPoint generators, making it a powerful foundation for conversational presentation creation workflows.