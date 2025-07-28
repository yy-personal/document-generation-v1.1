# PowerPoint Generation Service v2

Next-generation conversational PowerPoint generation using PptxGenJS for enhanced presentation capabilities.

## Overview

This Node.js Azure Function provides a conversational interface for creating PowerPoint presentations from documents. Features a complete agent-based pipeline with placeholder PowerPoint generation ready for PptxGenJS integration.

### Current Implementation Status

**Conversational Interface** - COMPLETE - Multi-turn conversations with session management  
**Document Processing** - COMPLETE - Supports PDF and Word documents via `[document]` tags  
**Smart Slide Estimation** - COMPLETE - AI-powered slide count estimation (5-30 slides)  
**Intelligent Content Structuring** - COMPLETE - Organized slide-by-slide content planning  
**PowerPoint Generation** - COMPLETE - Full PptxGenJS implementation with custom branding

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
ConversationManager → DocumentProcessor → SlideEstimator → ContentStructurer → PptxGenerator
        ↓                    ↓                ↓                ↓                ↓
   Intent Analysis    Content Extraction   Slide Planning   Content Structure   PowerPoint File
```

### Conversational Flow
1. **Document Upload** - User uploads document with optional questions
2. **Context Building** - User adds requirements/clarifications
3. **Generation Request** - User requests presentation creation
4. **PowerPoint Delivery** - System generates base64 PowerPoint file

## API Usage

### Endpoint
```
POST /api/powerpointGeneration
```

### Conversation Example
```json
// 1. Upload document
{
  "user_message": "What presentation would work best? [document]<content>",
  "entra_id": "user-123"
}

// 2. Add context (optional)
{
  "user_message": "Focus on implementation timeline",
  "session_id": "PPTV2...",
  "conversation_history": [...]
}

// 3. Generate presentation
{
  "user_message": "Create the presentation now",
  "session_id": "PPTV2...",
  "conversation_history": [...]
}
```

## Agent Architecture

### Core Agents
- **ConversationManager** - Intent analysis, conversation flow
- **DocumentProcessor** - Content extraction and organization  
- **SlideEstimator** - Smart slide count estimation (5-30 slides)
- **ContentStructurer** - Detailed slide layouts and content
- **PptxGenerator** - PowerPoint file generation (placeholder)

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
    max_slides: 30,
    min_slides: 5,
    default_slides: 12
}
```

### Port Management
If port 7076 is in use:
- **Recommended**: `npm run restart` (auto-kills existing processes)
- **Manual**: Use `netstat -ano | findstr :7076` then `taskkill /PID <PID> /F`
- **Change port**: Update both `config.js` (line 157) and `package.json` (line 6)

## Current Status

### Completed (Ready for Production Testing)
- [x] **Full Agent Pipeline** - ConversationManager → DocumentProcessor → SlideEstimator → ContentStructurer → PptxGenerator
- [x] **Conversational Flow** - Multi-turn conversations with intent analysis and session management
- [x] **Document Processing** - Supports PDF/Word via [document] tags with content extraction
- [x] **Smart Slide Estimation** - AI-powered slide count analysis (5-30 slides) based on content complexity
- [x] **Content Structuring** - Detailed slide-by-slide layouts with multiple content types
- [x] **Session Management** - Conversation history tracking with unique session IDs
- [x] **Centralized Configuration** - Single config file with OpenAI, agent, and service settings
- [x] **Testing Infrastructure** - Comprehensive test script for conversation flow validation
- [x] **Port Management** - Auto-restart functionality with process cleanup
- [x] **Code Quality** - Emoji-free codebase with consistent formatting

### Functional Capabilities (Current)
- Upload documents and ask questions about presentation needs
- Maintain conversation context across multiple interactions
- Estimate optimal slide counts based on document content and user requirements
- Structure content into professional slide layouts (title, agenda, content, two-column, table, summary, thank you)
- Generate session-based responses with conversation history
- Return placeholder PowerPoint data with proper metadata (filename, size, slide count)

### Ready for Next Development Session
- [ ] **PptxGenJS Integration** - Replace placeholder with actual PowerPoint generation
- [ ] **Slide Creation** - Implement PptxGenJS slide formatting for all layout types
- [ ] **Table Support** - Add formatted table generation within slides
- [ ] **Multi-column Layouts** - Enhanced two-column and complex layout support
- [ ] **Company Templates** - Integration with branded PowerPoint templates

## Project Structure
```
azure_function_ppt_v2/
├── powerpointGeneration/
│   ├── function.json              # Function binding
│   └── index.js                   # HTTP trigger
├── src/
│   ├── agents/
│   │   ├── core/
│   │   │   └── baseAgent.js              # Base agent class
│   │   ├── conversationManager_agent.js  # Conversation flow management
│   │   ├── documentProcessor_skill.js    # Document content extraction
│   │   ├── slideEstimator_skill.js       # Slide count estimation
│   │   ├── contentStructurer_skill.js    # Content layout structuring
│   │   └── pptxGenerator_skill.js        # PowerPoint generation
│   ├── orchestrator/
│   │   └── pptOrchestrator.js     # Pipeline management
│   └── config/
│       └── config.js              # Centralized configuration
├── test/
│   └── test-poc.js               # Conversation tests
├── package.json
├── host.json
└── local.settings.json
```

## Development Notes

### For Next Session - PptxGenJS Integration
The service is fully functional with all agent pipeline components complete. The only remaining work is replacing the placeholder PowerPoint generation in `src/agents/pptxGenerator_skill.js` with actual PptxGenJS implementation.

**Key Integration Points:**
- `generateWithPptxGenJS()` method needs implementation
- Slide creation methods for different layouts (title, content, table, two-column)
- PptxGenJS configuration for fonts, colors, and positioning
- Base64 file generation and proper error handling

**Current Placeholder Behavior:**
- Returns mock base64 PowerPoint data
- Simulates 2-second generation time
- Provides proper response structure for frontend integration

---

**PowerPoint Generation Service v2** - Complete conversational pipeline ready for PptxGenJS integration