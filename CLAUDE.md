# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a document generation system with two independent Azure Functions services. The system processes PDF/Word documents using AI agents to generate either PDF analysis reports or PowerPoint presentations.

### Architecture

The project consists of two main services:

1. **PDF Processing Service** (`azure_function_pdf/`) - Converts documents to PDF reports with strategic analysis
2. **PowerPoint Generation Service** (`azure_function_ppt/`) - Creates business presentations from documents

## Development Commands

### Azure Functions (PDF and PowerPoint services)

```bash
# Install dependencies for PDF service
cd azure_function_pdf
pip install -r requirements.txt

# Install dependencies for PowerPoint service
cd azure_function_ppt  
pip install -r requirements.txt

# Run either service locally (requires Azure Functions Core Tools)
func start  # Runs on localhost:7071
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

### PowerPoint Generation Service (azure_function_ppt/)
- **Endpoint**: `/api/powerpoint_generation`
- **Pipeline**: 4 AI agents + 1 rule-based builder (SmartPresentationProcessor → DocumentContentExtractor → PresentationStructureAgent → SlideContentGenerator → PowerPointBuilderAgent)
- **Output**: Content-driven presentations (3-30 slides) with 16:9 format
- **Processing time**: 12-15 seconds
- **Key Feature**: Smart slide count determination based on content complexity
- **Theme**: Purple (#584dc1) and Gold (#d1b95b) color scheme

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

### PowerPoint Service Pipeline (5 steps, 4 AI calls)
1. **SmartPresentationProcessor** - Intent classification only
2. **DocumentContentExtractor** - Content organization and topic extraction
3. **PresentationStructureAgent** - Content analysis + optimal slide count determination (3-30 slides)
4. **SlideContentGenerator** - Detailed slide content creation
5. **PowerPointBuilderAgent** - Rule-based .pptx file generation with python-pptx

## Input/Output Formats

### Input Format
- PDF documents (.pdf) via base64 encoding
- Word documents (.docx) via base64 encoding  
- Message format: `[document]base64_content` or `user_question[document]base64_content`
- Test scripts handle file conversion to base64 format

### Output Format
- **PDF service**: Base64 encoded PDF reports + JSON response with text summaries
- **PowerPoint service**: Base64 encoded .pptx files + JSON response with metadata
- Test scripts can save output files locally for validation

## Agent Configuration Patterns

### Token Limits by Agent Type
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
- `azure_function_ppt/test_poc.py` - PowerPoint service testing including long document handling
- Each test script includes complete request/response validation

### Common Development Issues
- **Missing environment variables**: Services fail without proper Azure OpenAI credentials
- **Port conflicts**: Azure Functions default to 7071 (only one service can run at a time)
- **Token limits**: Large documents may exceed agent token limits (configurable in config.py)
- **File encoding**: Documents must be properly base64 encoded for processing
- **Service isolation**: Each service runs independently - choose the appropriate service for your testing needs

## Performance Characteristics

### PDF Service Optimization
- **Routing efficiency**: 60% reduction in AI calls (1 vs 2-3 previously)
- **Response time**: 25% faster (4-6s vs 6-8s previously)
- **Clarification requests**: 85% reduction through smart defaults

### PowerPoint Service Scaling
- **Slide optimization**: Content-driven slide count (3-30 slides vs fixed 12)
- **Processing time**: Consistent 12-15 seconds regardless of slide count
- **Memory usage**: <500MB per request

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
Test scripts use standard Python libraries:
- `requests` for HTTP API calls
- `json` for request/response handling  
- `asyncio` for async operations (PDF service)
- `time` for performance measurement

## Project Structure Understanding

### Service Separation
- Each Azure Function service is completely independent and self-contained
- Services share no code or dependencies between them
- Each has its own config.py with service-specific agent configurations
- Services can be developed, tested, and deployed independently
- Only one service can run locally at a time (both use port 7071)

### Agent Pattern
- All agents inherit from `core/base_agent.py`
- Agents are stateless and operate in defined pipelines
- Configuration is centralized in each service's `config.py`
- Orchestrators (`pdf_orchestrator.py`, `ppt_orchestrator.py`) manage pipeline execution

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

### Direct API Usage
Both services accept POST requests with JSON payloads:

**PDF Service** (`/api/pdf_processing`):
```json
{
  "user_message": "[document]base64_content",
  "entra_id": "user-id",
  "session_id": "optional-session-id",
  "conversation_history": []
}
```

**PowerPoint Service** (`/api/powerpoint_generation`):
```json
{
  "user_message": "Create presentation[document]base64_content", 
  "entra_id": "user-id"
}
```

### Output Validation
- Test scripts automatically validate JSON response structure
- Base64 output can be decoded and saved as actual files for manual inspection
- PowerPoint service saves files to `local_output/` directory automatically
- PDF service test script includes comprehensive pipeline validation