# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a document generation system with two independent Azure Functions services. The system processes PDF/Word documents using AI agents to generate PDF analysis reports, and provides intelligent presentation requirements preprocessing for third-party PowerPoint generation services.

### Architecture

The project consists of two main services:

1. **PDF Processing Service** (`azure_function_pdf/`) - Converts documents to PDF reports with strategic analysis
2. **PowerPoint Requirements Service v2** (`azure_function_ppt_v2/`) - Intelligent presentation requirements preprocessing service for third-party PowerPoint generators

Note: PowerPoint Generation Service v1 (`azure_function_ppt/`) has been retired and removed from the codebase.

## Development Commands

### Azure Functions Services

#### Python Service (PDF Processing)
```bash
# Install dependencies for PDF service
cd azure_function_pdf
pip install -r requirements.txt

# Run PDF service locally (requires Azure Functions Core Tools)
func start  # Runs on localhost:7071
```

#### Node.js Service (PowerPoint Requirements v2)
```bash
# Install dependencies for PowerPoint requirements service v2
cd azure_function_ppt_v2
npm install

# Run PowerPoint requirements service locally (requires Azure Functions Core Tools)
npm start  # Runs on localhost:7071
```

### Service Testing

Each service can be tested independently:

1. Start Azure Functions service: `func start` (in either service directory - runs on localhost:7071)
2. Use the provided test scripts for direct API testing

## Service Architecture

### PDF Processing Service (azure_function_pdf/)
- **Endpoint**: `/api/pdf_processing`
- **Pipeline**: SmartIntentProcessor → skill agents → MarkdownFormatterAgent → PDF output
- **Key Feature**: Consolidated routing (1 AI call vs 2-3 previously) for 40% faster processing
- **Skills**: Strategic CV analysis, document summarization, quick summaries
- **Processing time**: 2-6 seconds depending on pipeline
- **Output**: Professional PDF reports with strategic analysis

### PowerPoint Requirements Service v2 (azure_function_ppt_v2/)
- **Endpoint**: `/api/powerpointGeneration`
- **Pipeline**: 2-stage clarification workflow with 2 AI agents
- **Output**: Structured presentation requirements (`consolidated_info`) for third-party PowerPoint generators
- **Processing time**: 8-12 seconds (Stage 1: 2-3s, Stage 2: 6-9s)
- **Key Feature**: AI-powered slide estimation and dynamic contextual clarification questions (no hardcoded questions)
- **Technology**: Node.js with intelligent requirements preprocessing and centralized prompt management
- **Integration**: Feeds processed requirements to third-party PowerPoint generation services
- **Status**: Production ready as preprocessing service for PowerPoint generators

## Key Configuration Files

### Azure Functions Configuration
- `config.js` - Agent settings, token limits, slide configurations, pipeline definitions (Node.js)
- `local.settings.json` - Local environment variables (git ignored)
- `host.json` - Azure Functions host configuration
- `.env` - Environment variables in parent directory (git ignored)

### Environment Variables Required
Create a `.env` file in the project root with:
```
ENDPOINT_URL=https://your-ai-foundry-endpoint.openai.azure.com/
DEPLOYMENT_NAME=gpt-4.1-ncsgpt-dev
AZURE_OPENAI_API_KEY=your-api-key
API_VERSION=2025-01-01-preview
```

## Agent System Architecture

Both services use Semantic Kernel with specialized agents operating in sequential pipelines:

### PDF Service Pipeline (3 steps, 1 AI routing call)
1. **SmartIntentProcessor** - Consolidated intent detection + document classification (replaces 2-3 separate calls)
2. **Skill Agents** (conditional):
   - **CVAnalysisSkill** - Strategic CV analysis with future skills roadmap
   - **DocumentExtractionSkill** - Intelligent document analysis and summarization
   - **DocumentQuickSummarySkill** - Fast text summaries for information requests
3. **MarkdownFormatterAgent** - PDF generation with reportlab

### PowerPoint Requirements Service v2 Pipeline (2-Stage Clarification Workflow)

**Stage 1: Requirements Gathering** (2-3 seconds)
1. **ConversationManager** - Auto-detects conversation history and triggers clarification workflow
2. **ClarificationQuestionGenerator** - AI-powered slide count estimation + contextual question generation
3. **Frontend Response** - Shows popup with AI slide recommendation and 3-4 contextual questions

**Stage 2: Requirements Processing** (6-9 seconds) 
1. **ConversationManager** - Processes `[clarification_answers]` with user preferences and consolidates information
2. **Output Generation** - Creates detailed `consolidated_info` with slide-by-slide content structure
3. **Third-Party Integration** - Structured requirements ready for external PowerPoint generation services

**Third-Party PowerPoint Generation** (External Service)
- Consumes `consolidated_info.content_summary` as structured input
- Maps content to predefined slide layouts (14 layout templates available)
- Generates actual PowerPoint files using OpenXML SDK
- Supports tables, charts, multi-column layouts, and structured content

## Input/Output Formats

### Input Format

**PDF and PowerPoint v1 Services:**
- PDF documents (.pdf) via base64 encoding
- Word documents (.docx) via base64 encoding  
- Message format: `[document]base64_content` or `user_question[document]base64_content`

**PowerPoint Requirements v2 Service (Clarification Workflow):**
- **Stage 1**: Conversation history (JSON format) auto-triggers clarification questions
- **Stage 2**: `[clarification_answers]{JSON_answers}` with user preferences
- **Conversation History Format**: Q&A pairs from frontend chat sessions

### Output Format
- **PDF service**: Base64 encoded PDF reports + JSON response with text summaries
- **PowerPoint Requirements v2 Stage 1**: Clarification questions array with field types and AI slide recommendations
- **PowerPoint Requirements v2 Stage 2**: Structured `consolidated_info` object with detailed presentation requirements for third-party PowerPoint generators

## Agent Configuration Patterns

### Token Limits by Agent Type

**Python Services:**
```python
# Intent/routing agents (lower tokens)
"SmartIntentProcessor": {"max_tokens": 5000}
"SmartPresentationProcessor": {"max_tokens": 3000}

# Content processing (medium tokens)
"DocumentContentExtractor": {"max_tokens": 8000}
"DocumentExtractionSkill": {"max_tokens": 10000}

# Content generation (higher tokens)
"CVAnalysisSkill": {"max_tokens": 10000}
"SlideContentGenerator": {"max_tokens": 16000}
```

**PowerPoint Requirements v2 Service (Node.js):**
```javascript
// Conversation management (high tokens for context and consolidation)
"ConversationManager": {"max_tokens": 20000}

// Requirements analysis (medium-high tokens for slide estimation + question generation)
"ClarificationQuestionGenerator": {"max_tokens": 8000}
```

### Temperature Settings by Purpose
- **Analysis/Classification**: 0.3-0.4 (more focused)
- **Content Organization**: 0.4-0.5 (balanced)
- **Creative Content**: 0.5-0.6 (more creative)
- **File Generation**: 0.2-0.3 (consistent formatting)

## Testing and Development

### Local Development Setup
1. Ensure Azure Functions Core Tools installed
2. Create `.env` file with required environment variables in project root
3. Install Python dependencies in each service directory (pip install -r requirements.txt)

### API Testing Files
- `azure_function_pdf/test_simplified.py` - Comprehensive PDF service testing with multiple scenarios
- `azure_function_ppt_v2/test/test-clarification-workflow.js` - PowerPoint Requirements v2 clarification workflow testing with Node.js
- Each test script includes complete request/response validation

### Common Development Issues
- **Missing environment variables**: Services fail without proper Azure OpenAI credentials
- **Port conflicts**: Azure Functions default to 7071 (only one service can run at a time)
- **Token limits**: Large documents may exceed agent token limits (configurable in config.py)
- **File encoding**: Documents must be properly base64 encoded for processing
- **Service isolation**: Each service runs independently - choose the appropriate service for your testing needs

## PowerPoint Requirements v2 Clarification Questions Workflow

### Dynamic Question Generation (2-4 Questions + Slide Count)

The system generates contextual questions dynamically based on conversation analysis:

**Always Included:**
1. **Slide Count** - Select field with AI recommendation and 11 options (±15 slides around recommendation)

**Dynamically Generated (2-4 questions based on content):**
- **Audience Expertise** - ONLY if content has technical/complex concepts
- **Content Focus** - ONLY if conversation covers multiple distinct topics  
- **Detail Level** - ONLY if content could be presented at different depths
- **Include Written Examples** - ONLY if content involves concepts needing illustration
- **Content Organization** - ONLY if content could be structured differently

**No Hardcoded Questions:** All questions except slide_count are AI-generated based on specific conversation content.

### Question Field Types (Supported)
- `select` - Dropdown with predefined options (always includes "Let agent decide" as first option)
- `boolean` - True/false toggle for yes/no questions

### Text-Only PowerPoint Constraints
The system is optimized for PowerPoint generators that support:
- **Text content only** - No images, charts, graphs, or visual elements
- **Bullet points** - Structured text organization
- **Tables** - Text-based data presentation
- **No visual suggestions** - Questions and consolidation avoid referencing visual elements

### AI Slide Recommendation Logic
The ClarificationQuestionGenerator analyzes conversation content to recommend optimal slide count:
- **Content Volume**: Amount of information to present
- **Topic Complexity**: Technical/business complexity factors
- **Multiple Topics**: Each distinct topic requires coverage
- **Content Structure**: Logical flow and supporting materials needed

### Frontend Integration Example

**Stage 1 Request:**
```json
{
  "user_message": "[create_presentation]",
  "conversation_history": [
    {
      "session_id": "abc-123",
      "conversation": [
        {
          "question": "Tell me about robotics in workplace",
          "response": "Robotics in workplace involves..."
        }
      ]
    }
  ],
  "session_id": "abc-123",
  "entra_id": "user-123"
}
```

**Stage 1 Response:**
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
        "validation": {"min": 5, "max": 50}
      },
      {
        "id": "audience_level", 
        "question": "What is the technical level of your audience?",
        "field_type": "select",
        "options": ["Beginner", "Intermediate", "Advanced", "Mixed audience"],
        "default_value": "Intermediate"
      }
    ]
  }
}
```

**Stage 2 Request:**
```json
{
  "user_message": "[clarification_answers]{\"slide_count\": 15, \"audience_level\": \"Advanced\", \"include_examples\": true, \"content_depth\": \"Moderate detail\"}",
  "conversation_history": [same_as_stage_1],
  "session_id": "abc-123",
  "entra_id": "user-123"
}
```

**Stage 2 Response:**
```json
{
  "response_data": {
    "status": "completed",
    "consolidated_info": {
      "content_summary": "Detailed slide-by-slide presentation structure with titles, key points, layout suggestions, and content organization based on conversation history and user preferences",
      "user_preferences": {
        "slide_count": 15,
        "audience_level": "Advanced",
        "include_examples": true,
        "content_depth": "Moderate detail"
      },
      "main_topics": [...],
      "intent": "PRESENTATION_GENERATE"
    }
  }
}
```

## Performance Characteristics

### PDF Service Optimization
- **Routing efficiency**: 60% reduction in AI calls (1 vs 2-3 previously)
- **Response time**: 25% faster (4-6s vs 6-8s previously)
- **Clarification requests**: 85% reduction through smart defaults

### PowerPoint Requirements v2 Performance
- **Stage 1 (Questions)**: 2-3 seconds for AI slide recommendation + contextual question generation
- **Stage 2 (Processing)**: 6-9 seconds for requirements consolidation and structured output generation
- **Total Processing Time**: 8-12 seconds for complete requirements preprocessing
- **Memory Usage**: <300MB per request (lightweight processing, no PowerPoint generation)
- **AI Efficiency**: 2 AI calls total (ClarificationQuestionGenerator + ConversationManager consolidation)
- **Third-Party Integration**: Output ready for immediate consumption by PowerPoint generators

## Third-Party PowerPoint Generation Integration

### Integration Architecture

The PowerPoint Requirements v2 service acts as an **intelligent preprocessing layer** that transforms conversational content into structured presentation requirements. The `consolidated_info.content_summary` output is specifically designed to integrate with third-party PowerPoint generation services.

### Third-Party Service Requirements

The external PowerPoint generation service expects:

**Input Format:**
- User messages containing structured presentation requirements
- Slide-by-slide content breakdown with titles and key points
- Layout and formatting suggestions
- Content type indicators (tables, charts, bullet points)

**Supported Template Layouts (14 Available):**
1. `1_title_slide` - Title and subtitle placeholders
2. `2_agenda` - Agenda/outline slides  
3. `2_divider_1` - Section dividers
4. `3_divider_1` - Content dividers
5. `4_content_white_1_col` - Single column content
6. `4_content_white_1_title_col` - Single column with title
7. `4_content_title_2_col` - Two column layout
8. `4_content_title_3_col` - Three column layout
9. `4_content_title_4_col` - Four column layout
10. `4_content_white_content` - Standard content layout
11. `4_content_white_table` - Table layout
12. `4_content_white_chart` - Chart/visualization layout
13. `4_slide_bg` - Background slide
14. `5_ending_slide` - Closing/thank you slide

**Output Format:**
- PowerPoint files generated using OpenXML SDK
- Support for complex layouts, tables, and charts
- Professional formatting with predefined templates

### Integration Workflow

1. **Frontend** → **PowerPoint Requirements v2**: User conversation and clarification answers
2. **PowerPoint Requirements v2** → **Third-Party Service**: `consolidated_info.content_summary` as structured input
3. **Third-Party Service** → **Frontend**: Generated PowerPoint file

### Sample Integration Data Flow

```json
// PowerPoint Requirements v2 Output (consumed by third-party service)
{
  "consolidated_info": {
    "content_summary": "The presentation will provide an intermediate-level, moderately detailed overview of the stock market, with balanced coverage of both general stock market fundamentals and notable figures in stock market prediction...\n\n**Presentation Structure and Content Requirements:**\n\n1. **Title Slide**\n   - Title: \"Understanding the Stock Market and Its Legendary Predictors\"\n   - Layout: 1_title_slide\n   - Placeholders: Presenter name, date, relevant image\n\n2. **Introduction to the Stock Market**\n   - Key Points: Definition, importance, role for companies and investors\n   - Layout: 4_content_white_1_col\n   - Supporting image: global stock exchanges",
    "user_preferences": {
      "slide_count": 12,
      "audience_level": "Intermediate",
      "content_depth": "Moderate detail",
      "include_examples": true
    }
  }
}

// Third-Party Service Expected Output
[
  {
    "layout": "1_title_slide",
    "placeholders": {
      "title": "Understanding the Stock Market and Its Legendary Predictors",
      "body[12]": "A Balanced Overview for Intermediate Learners"
    }
  },
  {
    "layout": "4_content_white_1_col", 
    "placeholders": {
      "title": "Introduction to the Stock Market",
      "body[10]": "• Definition and importance in the global economy\n• Role for companies and investors\n• Foundation of modern financial systems"
    }
  }
]
```

### Benefits of This Architecture

1. **Separation of Concerns**: Requirements gathering vs PowerPoint generation
2. **AI Optimization**: Complex conversation analysis handled by specialized agents
3. **Flexibility**: Third-party service can focus on layout and formatting excellence
4. **Scalability**: Requirements service can support multiple PowerPoint generators
5. **Quality**: Rich context and user preferences ensure high-quality output

## Dependencies

### Python Services (requirements.txt)
```
azure-functions
semantic-kernel==1.30.0
openai>=1.0.0
python-dotenv>=1.0.0
reportlab>=4.0.0        # PDF service only
python-pptx>=0.6.23     # PowerPoint service only
```

### Testing Dependencies

**Python Services:**
- `requests` for HTTP API calls
- `json` for request/response handling  
- `asyncio` for async operations (PDF service)
- `time` for performance measurement

**Node.js Service (PowerPoint v2):**
- `@azure/functions` for Azure Functions runtime
- `pptxgenjs` for PowerPoint generation  
- `openai` for OpenAI API integration
- `dotenv` for environment variable management

## Project Structure Understanding

### Service Separation
- Each Azure Function service is completely independent and self-contained
- Services share no code or dependencies between them
- Python services have config.py files, Node.js service has config.js
- Services can be developed, tested, and deployed independently
- Only one service can run locally at a time (all use port 7071)
- PowerPoint v2 service uses different technology stack (Node.js vs Python)

### Agent Pattern
- **Python services**: All agents inherit from `core/base_agent.py`
- **Node.js service**: All agents inherit from `baseAgent.js`
- Agents are stateless and operate in defined pipelines
- Configuration is centralized (Python: `config.py`, Node.js: `config.js`)
- Orchestrators manage pipeline execution:
  - `pdf_orchestrator.py` (PDF service)
  - `ppt_orchestrator.py` (PowerPoint v1)
  - `pptOrchestrator.js` (PowerPoint v2)

## Service Testing and Usage

### PDF Service Testing (`azure_function_pdf/test_simplified.py`)
```bash
cd azure_function_pdf
func start &  # Start service in background
python test_simplified.py  # Run comprehensive tests
```

Test scenarios include:
- Information requests (quick summaries without PDF output)
- Processing requests (full analysis with PDF generation)
- Conversation continuation handling
- CV analysis vs general document processing

### PowerPoint Requirements v2 Testing (`azure_function_ppt_v2/test/`)
```bash
cd azure_function_ppt_v2
npm start &  # Start service in background

# Test 2-stage clarification workflow
node test/test-clarification-workflow.js

# Test legacy conversation workflow (if needed)
node test/test-conversation-workflow.js
```

**Clarification Workflow Tests:**
- Stage 1: AI slide recommendation and contextual question generation
- Stage 2: Requirements consolidation with `consolidated_info` output validation
- Context-dependent question generation (business vs technical content)
- Field type validation (select, boolean only)
- `content_summary` structure and quality verification

**Integration Tests:**
- Conversation history processing and content extraction
- User preference integration with clarification answers
- `consolidated_info` output format validation for third-party services
- Session and conversation history management

### Direct API Usage
All services accept POST requests with JSON payloads:

**PDF Service** (`/api/pdf_processing`):
```json
{
  "user_message": "[document]base64_content",
  "entra_id": "user-id",
  "session_id": "optional-session-id",
  "conversation_history": []
}
```

**PowerPoint Requirements v2** (`/api/powerpointGeneration`):

*Stage 1 - Auto-trigger Clarification Questions (Conversation History Provided):*
```json
{
  "user_message": "{\"session_id\": \"abc-123\", \"conversation\": [{\"question\": \"Tell me about stock market\", \"response\": \"Stock market basics...\"}]}", 
  "entra_id": "user-id",
  "session_id": "session-id",
  "conversation_history": [
    {
      "session_id": "session-id",
      "conversation": [
        {"question": "Tell me about stock market", "response": "Stock market involves..."}
      ]
    }
  ]
}
```

*Stage 2 - Process Clarification Answers:*
```json
{
  "user_message": "[clarification_answers]{\"slide_count\": 12, \"audience_level\": \"Intermediate\", \"include_examples\": true, \"content_depth\": \"Moderate detail\"}",
  "entra_id": "user-id", 
  "session_id": "session-id",
  "conversation_history": [same_as_stage_1]
}
```

### Output Validation
- Test scripts automatically validate JSON response structure
- PDF service: Base64 output can be decoded and saved as actual files for manual inspection
- PowerPoint Requirements v2: `consolidated_info` structure validation for third-party service integration
- PDF service test script includes comprehensive pipeline validation

### PowerPoint Requirements v2 Test Script Details

**test-clarification-workflow.js:**
- Tests complete 2-stage requirements preprocessing workflow
- Validates AI slide recommendation generation and contextual questions
- Tests question field types (select, boolean only)
- Validates `consolidated_info` output structure and content quality
- Demonstrates context-dependent questions (business vs technical content)
- Includes comprehensive third-party service integration validation

**test-conversation-workflow.js (Legacy):**
- Tests basic conversation history processing
- Validates session management for backwards compatibility
- Demonstrates simple Q&A pair handling