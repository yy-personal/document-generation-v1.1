# PowerPoint Generation Service v2

Next-generation conversational PowerPoint generation using PptxGenJS for enhanced presentation capabilities.

## Overview

This Node.js Azure Function provides a conversational interface for creating PowerPoint presentations from documents. Unlike the previous Python-based service, this version uses PptxGenJS for superior PowerPoint generation and supports multi-turn conversations for iterative refinement.

### Key Features

✅ **Conversational Interface** - Multi-turn conversations for presentation refinement  
✅ **Document Processing** - Supports PDF and Word documents via `[document]` tags  
✅ **Smart Slide Estimation** - AI-powered slide count estimation based on content complexity  
✅ **Intelligent Content Structuring** - Organized slide-by-slide content planning  
⏳ **PptxGenJS Integration** - Enhanced PowerPoint generation (to be implemented)  
⏳ **Company Template Support** - Custom template integration (future feature)  

## Architecture

### Agent Pipeline
```
ConversationManager → DocumentProcessor → SlideEstimator → ContentStructurer → PptxGenerator
        ↓                    ↓                ↓                ↓                ↓
   Intent Analysis    Content Extraction   Slide Planning   Content Structure   PowerPoint File
```

### Conversational Flow
1. **Document Upload** - User uploads document and asks questions
2. **Context Building** - User provides additional requirements/clarifications  
3. **Slide Estimation** - System estimates slide count and presents plan
4. **Generation Request** - User confirms and requests presentation creation
5. **PowerPoint Delivery** - System generates and returns base64 PowerPoint file

## Quick Start

### Prerequisites
- Node.js 18+ 
- Azure Functions Core Tools
- Azure OpenAI access

### Installation
```bash
cd azure_function_ppt_v2
npm install
```

### Environment Setup
Configure environment variables in `local.settings.json`:
```json
{
  "Values": {
    "ENDPOINT_URL": "https://your-ai-foundry-endpoint.openai.azure.com/",
    "DEPLOYMENT_NAME": "gpt-4.1-ncsgpt-dev",
    "AZURE_OPENAI_API_KEY": "your-api-key",
    "API_VERSION": "2025-01-01-preview"
  }
}
```

### Run Locally
```bash
npm start
# Service runs on http://localhost:7071
```

### Test the Service
```bash
npm test
```

## Agent Architecture

### ConversationManager
- **Purpose**: Manages conversation flow and user intent analysis
- **Input**: User messages, conversation history, session context
- **Output**: Intent classification, generation decisions, contextual responses

### DocumentProcessor  
- **Purpose**: Extracts and organizes document content for presentation structure
- **Input**: Raw document content, user context
- **Output**: Structured topics, content classification, complexity analysis

### SlideEstimator
- **Purpose**: Analyzes content complexity and estimates optimal slide count
- **Input**: Document content or processed structure
- **Output**: Slide count estimate, complexity assessment, breakdown rationale

### ContentStructurer
- **Purpose**: Creates detailed slide-by-slide structure with layouts and content
- **Input**: Processed content, slide estimates, user requirements
- **Output**: Complete slide structure with layouts, content, and formatting guidance

### PptxGenerator
- **Purpose**: Generates PowerPoint files using PptxGenJS
- **Status**: ⏳ **Placeholder** - PptxGenJS integration pending
- **Input**: Structured slide content, session info
- **Output**: Base64 PowerPoint file

## API Usage

### Endpoint
```
POST /api/powerpointGeneration
```

### Request Format
```json
{
  "user_message": "Create a presentation [document]<base64_content>",
  "entra_id": "user-123",
  "session_id": "optional-session-id",
  "conversation_history": []
}
```

### Response Format
```json
{
  "response_data": {
    "status": "completed",
    "session_id": "PPTV220240726ABC123",
    "conversation_history": [...],
    "pipeline_info": ["ConversationManager", "DocumentProcessor", ...],
    "processing_info": {
      "conversation": {...},
      "slide_estimate": {...},
      "content_structure": {...}
    },
    "response_text": "Generated presentation with 12 slides...",
    "powerpoint_output": {
      "ppt_data": "base64_encoded_powerpoint",
      "filename": "presentation_PPTV220240726ABC123.pptx",
      "file_size_kb": 145,
      "slide_count": 12
    }
  }
}
```

## Configuration

### Slide Limits
```javascript
PRESENTATION_CONFIG = {
    max_slides: 30,        // Maximum allowed slides
    min_slides: 5,         // Minimum slides required  
    default_slides: 12     // Default target for medium complexity
}
```

### Agent Settings
Each agent has configurable token limits and temperature settings:
- **ConversationManager**: 3,000 tokens, temp 0.3 (focused conversation)
- **DocumentProcessor**: 8,000 tokens, temp 0.4 (balanced analysis)
- **SlideEstimator**: 4,000 tokens, temp 0.3 (precise estimation)
- **ContentStructurer**: 12,000 tokens, temp 0.5 (creative structuring)
- **PptxGenerator**: 6,000 tokens, temp 0.2 (consistent generation)

## Current Status

### ✅ Completed
- [x] Node.js Azure Function structure
- [x] Agent architecture and pipeline
- [x] Conversation management system
- [x] Document processing and analysis
- [x] Slide count estimation
- [x] Content structuring with layouts
- [x] Session and conversation history management
- [x] Test script and API validation

### ⏳ In Progress
- [ ] **PptxGenJS Integration** (next session priority)
  - PptxGenJS documentation understanding agent
  - Slide creation with proper formatting
  - Table and multi-column layout support
  - Positioning and styling optimization

### 🔮 Future Features
- [ ] Company template integration
- [ ] Advanced visual design options
- [ ] Image and chart placeholders
- [ ] Multi-language support
- [ ] Batch presentation generation

## Next Steps

### Immediate Priority: PptxGenJS Integration
The service is currently using a placeholder for PowerPoint generation. The next development session should focus on:

1. **PptxGenJS Documentation Agent** - Create an agent that understands PptxGenJS API
2. **Slide Creation Logic** - Implement proper slide generation with formatting
3. **Layout Implementation** - Support for different slide layouts (title, content, table, two-column)
4. **Styling and Positioning** - Proper text formatting, colors, and element positioning
5. **Testing and Validation** - Ensure generated PowerPoint files are properly formatted

### Development Approach for PptxGenJS
1. Study PptxGenJS documentation and examples
2. Create agent that can generate PptxGenJS code
3. Implement slide-by-slide generation logic
4. Add support for tables, bullet points, and multi-column layouts  
5. Test with various content types and complexity levels

## Testing

### Test Scenarios
The test script validates:
- Service availability and health check
- Conversational flow (question → context → generation)
- Agent pipeline execution
- Session and conversation history management
- Response format validation

### Running Tests
```bash
# Start the service first
npm start

# In another terminal, run tests
npm test
```

## Dependencies

### Core Dependencies
- `@azure/functions`: Azure Functions runtime
- `pptxgenjs`: PowerPoint generation library  
- `openai`: OpenAI API client
- `dotenv`: Environment variable management

### Development
- `@azure/functions-core-tools`: Local development tools

## Project Structure
```
azure_function_ppt_v2/
├── src/
│   ├── functions/
│   │   └── powerpointGeneration.js    # Main HTTP trigger
│   ├── agents/
│   │   ├── baseAgent.js               # Base agent class
│   │   ├── conversationManager.js     # Conversation flow management
│   │   ├── documentProcessor.js       # Document content extraction  
│   │   ├── slideEstimator.js          # Slide count estimation
│   │   ├── contentStructurer.js       # Slide structure creation
│   │   └── pptxGenerator.js           # PowerPoint generation (placeholder)
│   ├── orchestrator/
│   │   └── pptOrchestrator.js         # Main pipeline orchestration
│   └── config/
│       └── config.js                  # Service configuration
├── test/
│   └── test-poc.js                    # Test script
├── package.json                       # Node.js dependencies
├── host.json                          # Azure Functions configuration
├── local.settings.json                # Local environment variables
└── README.md                          # This file
```

---

**PowerPoint Generation Service v2** - Conversational presentation creation with enhanced capabilities using PptxGenJS.