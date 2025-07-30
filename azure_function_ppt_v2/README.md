# Presentation Planning Service v2

Conversational presentation requirements gathering service for third-party PowerPoint generation integration.

## Overview

This Node.js Azure Function provides a conversational interface for gathering presentation requirements through a 2-stage clarification workflow. It analyzes conversation history to generate contextual questions and consolidated information for third-party PowerPoint generation services.

### Current Implementation Status

**Conversational Interface** - COMPLETE - Multi-turn conversations with session management  
**Smart Slide Estimation** - COMPLETE - AI-powered slide count recommendation (3-60 slides)  
**Clarification Questions** - COMPLETE - Context-aware questions with "Let agent decide" options  
**Consolidated Information** - COMPLETE - Structured output for third-party PowerPoint services  
**Requirements Gathering** - COMPLETE - 2-stage workflow for presentation customization

## Quick Start

### Prerequisites
- Node.js 18+
- Azure Functions Core Tools
- Azure OpenAI access

### Installation & Setup
```bash
cd azure_function_ppt_v2
npm install

# Start service (kills any existing process on port first)
npm run restart

# Or manually
npm start    # Runs on port 7076
```

### Environment
Service uses the **root .env file** (same as Python services):
- File: `document-generation-v1.1/.env`
- No additional configuration needed

### Testing
```bash
npm test    # Run conversation flow tests
```

## Architecture

### Agent Pipeline
```
ConversationManager → ClarificationQuestionGenerator
        ↓                           ↓
   Intent Analysis            Slide Estimation & Questions
        ↓                           ↓
   Context Building           Consolidated Information
```

### Clarification Workflow
1. **Context Building** - User discusses presentation needs through conversation
2. **Create Trigger** - User sends `[create_presentation]` to start workflow
3. **Clarification Questions** - System generates up to 5 contextual questions with AI recommendations
4. **Requirements Processing** - User answers are processed into consolidated information for third-party services

## API Usage

### Endpoint
```
POST /api/powerpointGeneration
```

### Workflow Example
```json
// Stage 1: Request clarification questions
{
  "user_message": "[create_presentation]",
  "session_id": "PPTV2...",
  "conversation_history": [
    {
      "session_id": "PPTV2...",
      "conversation": [
        {"question": "Tell me about robotics in workplace", "response": "Robotics involves..."}
      ]
    }
  ],
  "entra_id": "user-123"
}

// Stage 2: Submit clarification answers
{
  "user_message": "[clarification_answers]{\"slide_count\": 15, \"audience_level\": \"Advanced\", \"include_examples\": true}",
  "session_id": "PPTV2...",
  "conversation_history": [...],
  "entra_id": "user-123"
}
```

## Agent Architecture

### Core Agents
- **ConversationManager** - Intent analysis, conversation flow, bracket trigger detection
- **ClarificationQuestionGenerator** - AI-powered slide estimation and contextual question generation

### Base Agent
All agents inherit from `core/baseAgent.js` which provides:
- OpenAI API integration
- Error handling
- JSON parsing
- Common utilities

## Configuration

### Centralized Settings
**File:** `src/config/config.js`

```javascript
// Service configuration
LOCAL_DEV_CONFIG = {
    port: 7076,  // Update both config.js and package.json if changing
    host: 'localhost',
    api_path: '/api/powerpointGeneration'
}

// Slide configuration
PRESENTATION_CONFIG = {
    max_slides: 60,
    min_slides: 3,
    default_slides: 12
}
```

### Port Management
If port 7076 is in use:
- **Recommended**: `npm run restart` (auto-kills existing processes)
- **Manual**: Use `netstat -ano | findstr :7076` then `taskkill /PID <PID> /F`
- **Change port**: Update both `config.js` (line 157) and `package.json` (line 6)

## Current Status

### Completed (Production Ready)
- [x] **2-Stage Clarification Workflow** - ConversationManager → ClarificationQuestionGenerator
- [x] **Conversational Interface** - Multi-turn conversations with bracket trigger detection
- [x] **AI-Powered Questions** - Context-aware clarification questions with "Let agent decide" options
- [x] **Smart Slide Estimation** - AI slide count recommendation (3-60 slides) based on conversation analysis
- [x] **Consolidated Information** - Structured output for third-party PowerPoint generation services
- [x] **Session Management** - Conversation history tracking with unique session IDs
- [x] **Tolerant JSON Parsing** - 3-layer parsing strategy for malformed clarification answers
- [x] **Centralized Configuration** - Single config file with simplified agent pipeline
- [x] **Testing Infrastructure** - Comprehensive test scripts for both workflow stages
- [x] **Port Management** - Auto-restart functionality with process cleanup

### Functional Capabilities (Current)
- Process conversation history to understand presentation context
- Generate AI-powered slide count recommendations based on content complexity
- Create contextual clarification questions (max 5) with field types: select, boolean, number
- Provide "Let agent decide" options for all select questions as default
- Process user clarification answers with tolerant JSON parsing
- Output consolidated presentation requirements for third-party services
- Maintain session context across 2-stage workflow

### Integration Ready
- [x] **Third-Party Service Integration** - Consolidated information output format ready
- [x] **Question Generation** - Contextual questions based on conversation analysis
- [x] **Slide Recommendations** - AI-powered slide count estimation with ranges
- [x] **User Preferences** - Structured clarification answers processing
- [x] **Error Handling** - Tolerant parsing for frontend integration

## Project Structure
```
azure_function_ppt_v2/
├── powerpointGeneration/
│   ├── function.json              # Function binding
│   └── index.js                   # HTTP trigger
├── src/
│   ├── agents/
│   │   ├── core/
│   │   │   └── baseAgent.js                         # Base agent class
│   │   ├── conversationManager_agent.js             # Conversation flow & bracket triggers
│   │   └── clarificationQuestionGenerator_skill.js  # Slide estimation & question generation
│   ├── orchestrator/
│   │   └── pptOrchestrator.js     # Pipeline management
│   └── config/
│       └── config.js              # Centralized configuration
├── test/
│   ├── test-clarification-workflow.js  # 2-stage workflow tests
│   └── test-conversation-workflow.js   # Legacy conversation tests
├── package.json
├── host.json
└── local.settings.json
```

## Output Format

### Stage 1: Clarification Questions
```json
{
  "response_data": {
    "show_clarification_popup": true,
    "clarification_questions": [
      {
        "id": "slide_count",
        "question": "How many slides would you like? (Recommended: 12 slides based on AI analysis)",
        "field_type": "number",
        "default_value": 12,
        "validation": {"min": 3, "max": 60}
      },
      {
        "id": "audience_level",
        "question": "What is the technical level of your audience?",
        "field_type": "select",
        "options": ["Let agent decide", "Beginner", "Intermediate", "Advanced", "Mixed audience"],
        "default_value": "Let agent decide"
      }
    ]
  }
}
```

### Stage 2: Consolidated Information
```json
{
  "response_data": {
    "consolidated_info": {
      "conversation_content": "Discussion about robotics in workplace...",
      "user_context": "User wants comprehensive overview",
      "content_source": "conversation",
      "slide_count": 15,
      "user_preferences": {
        "slide_count": 15,
        "audience_level": "Advanced",
        "include_examples": true
      },
      "session_id": "PPTV2...",
      "entra_id": "user-123",
      "processed_timestamp": "2025-01-XX...",
      "service_version": "v2.1"
    }
  }
}
```

---

**Presentation Planning Service v2** - Complete 2-stage clarification workflow for third-party PowerPoint generation