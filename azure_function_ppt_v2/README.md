# PowerPoint Requirements Service v2

Intelligent presentation requirements preprocessing service for third-party PowerPoint generation integration.

## Overview

This Node.js Azure Function acts as an **intelligent preprocessing layer** that transforms conversational content into structured presentation requirements. It uses a 2-stage clarification workflow to gather user preferences and outputs comprehensive `consolidated_info` for third-party PowerPoint generation services.

### Current Implementation Status

**Conversational Interface** - COMPLETE - Multi-turn conversations with session management  
**Smart Slide Estimation** - COMPLETE - AI-powered slide count recommendation (3-60 slides)  
**Clarification Questions** - COMPLETE - Context-aware questions with "Let agent decide" options  
**Consolidated Information** - COMPLETE - Structured `consolidated_info` output for third-party PowerPoint services  
**Requirements Preprocessing** - COMPLETE - 2-stage workflow transforming conversations into structured requirements

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

### Requirements Preprocessing Workflow
1. **Context Building** - User discusses presentation needs through conversation
2. **Auto-Trigger** - Conversation history automatically triggers clarification workflow
3. **Clarification Questions** - System generates 3-4 contextual questions with AI slide recommendations
4. **Requirements Consolidation** - User answers are processed into structured `consolidated_info` for third-party PowerPoint generation services

## API Usage

### Endpoint
```
POST /api/powerpointGeneration
```

### Database Field Mapping

The service uses the following database field mapping:

- `user_message` - Main content field (required)
- `sessionhistory_entra_id` - User identifier (can be empty, replaces `entra_id`)
- `sessionhistory_session_id` - Session identifier (can be empty, no autogeneration)
- `conversation_history` - Conversation context (array, can be empty)

### Workflow Example
```json
// Stage 1: Auto-trigger clarification questions (conversation history provided)
{
  "user_message": "{\"session_id\": \"abc-123\", \"conversation\": [{\"question\": \"Tell me about stock market\", \"response\": \"Stock market involves...\"}]}",
  "sessionhistory_session_id": "PPTV2...",
  "conversation_history": [
    {
      "session_id": "PPTV2...",
      "conversation": [
        {"question": "Tell me about stock market", "response": "Stock market involves..."}
      ]
    }
  ],
  "sessionhistory_entra_id": "user-123"
}

// Stage 2: Submit clarification answers
{
  "user_message": "[clarification_answers]{\"slide_count\": 12, \"audience_level\": \"Intermediate\", \"include_examples\": true, \"content_depth\": \"Moderate detail\"}",
  "sessionhistory_session_id": "PPTV2...",
  "conversation_history": [...],
  "sessionhistory_entra_id": "user-123"
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
- **Recommended**: `npm run restart` (auto-kills existing processes using kill-port)
- **Manual**: Use `npm run kill-port` or `npx kill-port 7076`
- **Change port**: Update both `config.js` and `package.json` scripts

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
- Create contextual clarification questions (3-4 questions) with field types: select, boolean only
- Provide "Let agent decide" options for all select questions as default
- Process user clarification answers with tolerant JSON parsing
- Output structured `consolidated_info` with detailed content summary for third-party services
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
        "field_type": "select",
        "options": [6, 9, 12, 15, 18, 21],
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

### Stage 2: Consolidated Requirements
```json
{
  "response_data": {
    "status": "completed",
    "consolidated_info": {
      "content_summary": "The presentation will provide an intermediate-level, moderately detailed overview of the stock market, with balanced coverage of both general stock market fundamentals and notable figures in stock market prediction...\n\n**Presentation Structure and Content Requirements:**\n\n1. **Title Slide**\n   - Title: \"Understanding the Stock Market and Its Legendary Predictors\"\n   - Layout: 1_title_slide\n   - Placeholders: Presenter name, date, relevant image",
      "user_preferences": {
        "slide_count": 12,
        "audience_level": "Intermediate",
        "content_depth": "Moderate detail",
        "include_examples": true
      },
      "main_topics": [...],
      "intent": "PRESENTATION_GENERATE"
    },
    "powerpoint_output": null
  }
}
```

---

**PowerPoint Requirements Service v2** - Complete 2-stage requirements preprocessing workflow for third-party PowerPoint generation services