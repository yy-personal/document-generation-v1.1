# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a document generation system with three independent Azure Functions services. The system processes PDF/Word documents using AI agents to generate either PDF analysis reports or PowerPoint presentations.

### Architecture

The project consists of three main services:

1. **PDF Processing Service** (`azure_function_pdf/`) - Converts documents to PDF reports with strategic analysis
2. **PowerPoint Generation Service v1** (`azure_function_ppt/`) - Creates business presentations using python-pptx
3. **PowerPoint Generation Service v2** (`azure_function_ppt_v2/`) - Next-generation conversational PowerPoint service using PptxGenJS

## Development Commands

### Azure Functions Services

#### Python Services (PDF and PowerPoint v1)
```bash
# Install dependencies for PDF service
cd azure_function_pdf
pip install -r requirements.txt

# Install dependencies for PowerPoint service v1
cd azure_function_ppt  
pip install -r requirements.txt

# Run either Python service locally (requires Azure Functions Core Tools)
func start  # Runs on localhost:7071
```

#### Node.js Service (PowerPoint v2)
```bash
# Install dependencies for PowerPoint service v2
cd azure_function_ppt_v2
npm install

# Run Node.js service locally (requires Azure Functions Core Tools)
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

### PowerPoint Generation Service v1 (azure_function_ppt/)
- **Endpoint**: `/api/powerpoint_generation`
- **Pipeline**: 4 AI agents + 1 rule-based builder (SmartPresentationProcessor → DocumentContentExtractor → PresentationStructureAgent → SlideContentGenerator → PowerPointBuilderAgent)
- **Output**: Content-driven presentations (3-30 slides) with 16:9 format
- **Processing time**: 12-15 seconds
- **Key Feature**: Smart slide count determination based on content complexity
- **Theme**: Purple (#584dc1) and Gold (#d1b95b) color scheme
- **Technology**: Python with python-pptx library

### PowerPoint Generation Service v2 (azure_function_ppt_v2/)
- **Endpoint**: `/api/powerpointGeneration`
- **Pipeline**: 2-stage clarification workflow with 5 AI agents
- **Output**: Customized PowerPoint presentations based on user preferences
- **Processing time**: 8-12 seconds (Stage 1: 2-3s, Stage 2: 6-9s)
- **Key Feature**: Interactive clarification questions for presentation customization
- **Technology**: Node.js with PptxGenJS library
- **Status**: Production ready with full clarification workflow

## Key Configuration Files

### Azure Functions Configuration
- `config.py` - Agent settings, token limits, slide configurations, pipeline definitions
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

### PowerPoint Service v1 Pipeline (5 steps, 4 AI calls)
1. **SmartPresentationProcessor** - Intent classification only
2. **DocumentContentExtractor** - Content organization and topic extraction
3. **PresentationStructureAgent** - Content analysis + optimal slide count determination (3-30 slides)
4. **SlideContentGenerator** - Detailed slide content creation
5. **PowerPointBuilderAgent** - Rule-based .pptx file generation with python-pptx

### PowerPoint Service v2 Pipeline (2-Stage Clarification Workflow)

**Stage 1: Clarification Questions** (3-4 seconds)
1. **ConversationManager** - Detects `[create_presentation]` trigger
2. **SlideEstimator** - AI-powered slide count recommendation
3. **ConversationManager** - Generates up to 5 contextual clarification questions
4. **Frontend Response** - Shows popup with questions and AI recommendations

**Stage 2: Customized Generation** (6-9 seconds) 
1. **ConversationManager** - Processes `[clarification_answers]` with user preferences
2. **DocumentProcessor** - Content extraction and organization with user context
3. **Slide Decision** - Uses user-specified slide count (skips SlideEstimator)
4. **ContentStructurer** - Structures content based on user preferences
5. **PptxGenerator** - Creates PowerPoint with PptxGenJS library

## Input/Output Formats

### Input Format

**PDF and PowerPoint v1 Services:**
- PDF documents (.pdf) via base64 encoding
- Word documents (.docx) via base64 encoding  
- Message format: `[document]base64_content` or `user_question[document]base64_content`

**PowerPoint v2 Service (Clarification Workflow):**
- **Stage 1**: `[create_presentation]` with conversation history
- **Stage 2**: `[clarification_answers]{JSON_answers}` with user preferences
- **Conversation History Format**: Q&A pairs from frontend chat

### Output Format
- **PDF service**: Base64 encoded PDF reports + JSON response with text summaries
- **PowerPoint v1**: Base64 encoded .pptx files + JSON response with metadata
- **PowerPoint v2 Stage 1**: Clarification questions array with field types and AI recommendations
- **PowerPoint v2 Stage 2**: Base64 encoded .pptx files + customization metadata

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

**PowerPoint v2 Service (Node.js):**
```javascript
// Conversation management (high tokens for context)
"ConversationManager": {"max_tokens": 20000}

// Content processing (medium tokens)
"DocumentProcessor": {"max_tokens": 8000}
"SlideEstimator": {"max_tokens": 4000}

// Content generation (higher tokens)
"ContentStructurer": {"max_tokens": 12000}
"PptxGenerator": {"max_tokens": 10000}
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
- `azure_function_ppt/test_poc.py` - PowerPoint v1 service testing including long document handling
- `azure_function_ppt_v2/test/test-poc.js` - PowerPoint v2 conversational flow testing with Node.js
- Each test script includes complete request/response validation

### Common Development Issues
- **Missing environment variables**: Services fail without proper Azure OpenAI credentials
- **Port conflicts**: Azure Functions default to 7071 (only one service can run at a time)
- **Token limits**: Large documents may exceed agent token limits (configurable in config.py)
- **File encoding**: Documents must be properly base64 encoded for processing
- **Service isolation**: Each service runs independently - choose the appropriate service for your testing needs

## PowerPoint v2 Clarification Questions Workflow

### Smart Question Generation (Max 5 Questions)

The system generates contextual questions based on conversation analysis:

**Always Included:**
1. **Slide Count** - Number field with AI recommendation (5-50 range)
2. **Audience Level** - Select: Beginner/Intermediate/Advanced/Mixed audience  
3. **Include Examples** - Boolean for detailed examples and case studies

**Context-Dependent Questions (2 additional):**
- **Multi-topic Focus** - Select from detected topics (if multiple topics found)
- **Content Style** - Adaptive based on content type:
  - **Business Content**: Executive Summary/Strategic Overview/Training Material/Detailed Analysis
  - **Technical Content**: High-level overview/Moderate detail/Deep technical dive/Implementation focused
  - **General Content**: More visuals/Balanced/More text/Minimal design

### Question Field Types
- `number` - Numeric input with min/max validation
- `select` - Dropdown with predefined options
- `boolean` - True/false toggle for yes/no questions
- `string` - Text input (when needed)

### AI Slide Recommendation Logic
The SlideEstimator analyzes conversation content to recommend optimal slide count:
- **Content Length**: More extensive content requires more slides
- **Topic Complexity**: Technical/business complexity adds slides
- **Multiple Topics**: Each distinct topic needs coverage
- **Content Type**: Business vs technical presentation requirements

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
  "user_message": "[clarification_answers]{\"slide_count\": 15, \"audience_level\": \"Advanced\", \"include_examples\": true, \"business_style\": \"Strategic Overview\"}",
  "conversation_history": [same_as_stage_1],
  "session_id": "abc-123",
  "entra_id": "user-123"
}
```

## Performance Characteristics

### PDF Service Optimization
- **Routing efficiency**: 60% reduction in AI calls (1 vs 2-3 previously)
- **Response time**: 25% faster (4-6s vs 6-8s previously)
- **Clarification requests**: 85% reduction through smart defaults

### PowerPoint Service v1 Scaling
- **Slide optimization**: Content-driven slide count (3-30 slides vs fixed 12)
- **Processing time**: Consistent 12-15 seconds regardless of slide count
- **Memory usage**: <500MB per request

### PowerPoint Service v2 Performance
- **Stage 1 (Questions)**: 2-3 seconds for AI slide recommendation + question generation
- **Stage 2 (Generation)**: 6-9 seconds for customized presentation creation
- **Total User Experience**: 8-12 seconds with interactive customization
- **Memory Usage**: <400MB per request
- **AI Efficiency**: Single SlideEstimator call in Stage 1, user choice respected in Stage 2

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

### PowerPoint Service Testing (`azure_function_ppt/test_poc.py`)
```bash
cd azure_function_ppt
func start &  # Start service in background
python test_poc.py  # Run standard tests
python test_poc.py --long-only  # Test content-driven slide optimization
```

Test scenarios include:
- Standard document processing (8-12 slides)
- Long document handling (20-30 slides based on content complexity)
- User instruction processing
- Content-driven slide count optimization

### PowerPoint Service v2 Testing (`azure_function_ppt_v2/test/`)
```bash
cd azure_function_ppt_v2
npm start &  # Start service in background

# Test 2-stage clarification workflow
node test/test-clarification-workflow.js

# Test legacy conversation workflow  
node test/test-conversation-workflow.js
```

**New Clarification Workflow Tests:**
- Stage 1: AI slide recommendation and question generation
- Stage 2: Customized presentation with user answers
- Context-dependent question generation (business vs technical content)
- Field type validation (number, select, boolean)

**Legacy Tests:**
- Basic conversation history processing
- Multi-turn conversations for context building
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

**PowerPoint Service v1** (`/api/powerpoint_generation`):
```json
{
  "user_message": "Create presentation[document]base64_content", 
  "entra_id": "user-id"
}
```

**PowerPoint Service v2** (`/api/powerpointGeneration`):

*Stage 1 - Get Clarification Questions:*
```json
{
  "user_message": "[create_presentation]", 
  "entra_id": "user-id",
  "session_id": "session-id",
  "conversation_history": [
    {
      "session_id": "session-id",
      "conversation": [
        {"question": "Tell me about robotics", "response": "Robotics involves..."}
      ]
    }
  ]
}
```

*Stage 2 - Generate with Answers:*
```json
{
  "user_message": "[clarification_answers]{\"slide_count\": 15, \"audience_level\": \"Advanced\", \"include_examples\": true}",
  "entra_id": "user-id", 
  "session_id": "session-id",
  "conversation_history": [same_as_stage_1]
}
```

### Output Validation
- Test scripts automatically validate JSON response structure
- Base64 output can be decoded and saved as actual files for manual inspection
- PowerPoint services save files to `local_output/` directory automatically
- PDF service test script includes comprehensive pipeline validation

### PowerPoint v2 Test Script Details

**test-clarification-workflow.js:**
- Tests complete 2-stage workflow with robotics conversation example
- Validates AI slide recommendation generation
- Tests question field types (number, select, boolean)
- Demonstrates context-dependent questions (business vs technical)
- Includes business content detection test

**test-conversation-workflow.js (Legacy):**
- Tests basic conversation history processing
- Validates session management
- Demonstrates simple Q&A pair handling