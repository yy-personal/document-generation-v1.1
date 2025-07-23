# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a document generation system with three Azure Functions services and a React frontend for testing. The system processes PDF/Word documents using AI agents to generate either PDF analysis reports or PowerPoint presentations.

### Architecture

The project consists of three main components:

1. **PDF Processing Service** (`azure_function_pdf/`) - Converts documents to PDF reports
2. **PowerPoint Generation Service** (`azure_function_ppt/`) - Creates business presentations from documents  
3. **React Frontend** (`frontend/`) - Test interface for both services

## Development Commands

### Azure Functions (PDF and PowerPoint services)

```bash
# Install dependencies
cd azure_function_pdf
pip install -r requirements.txt

cd azure_function_ppt  
pip install -r requirements.txt

# Run locally (requires Azure Functions Core Tools)
func start
```

### React Frontend

```bash
cd frontend
npm install
npm start       # Development server
npm run build   # Production build
npm test        # Run tests
```

## Service Architecture

### PDF Processing Service (azure_function_pdf/)
- **Endpoint**: `/api/pdf_processing`
- **Pipeline**: SmartIntentProcessor → skill agents → MarkdownFormatterAgent → PDF output
- **Skills**: CV analysis, document summarization, quick summary
- **Processing time**: 2-6 seconds depending on pipeline

### PowerPoint Generation Service (azure_function_ppt/)
- **Endpoint**: `/api/powerpoint_generation`
- **Pipeline**: 4 AI agents + 1 rule-based builder
- **Output**: 12-slide business presentations with company branding
- **Processing time**: 12-15 seconds
- **Slide limit**: Configurable max 15 slides in `config.py`

## Key Configuration Files

### Azure Functions Configuration
- `config.py` - Agent settings, token limits, slide configurations
- `local.settings.json` - Local environment variables (not tracked)
- `host.json` - Azure Functions host configuration

### Environment Variables Required
```
ENDPOINT_URL=https://your-ai-foundry-endpoint.openai.azure.com/
DEPLOYMENT_NAME=gpt-4.1-ncsgpt-dev
AZURE_OPENAI_API_KEY=your-api-key
API_VERSION=2025-01-01-preview
```

## Agent System

Both services use Semantic Kernel with specialized agents:

### PDF Service Agents
- **SmartIntentProcessor** - Consolidated intent + document classification
- **CVAnalysisSkill** - Strategic CV analysis with skills roadmap
- **DocumentExtractionSkill** - Document summarization and analysis
- **DocumentQuickSummarySkill** - Fast text summaries
- **MarkdownFormatterAgent** - PDF generation with reportlab

### PowerPoint Service Agents
- **SmartPresentationProcessor** - Intent analysis only
- **DocumentContentExtractor** - Content organization
- **PresentationStructureAgent** - Slide planning (12-slide target)
- **SlideContentGenerator** - Detailed slide content
- **PowerPointBuilderAgent** - .pptx file generation with python-pptx

## Input/Output Formats

### Input
- PDF documents (via base64)
- Word documents (.docx, via base64)
- Format: `[pdf_extraction]base64_content` or `[word_document_extraction]base64_content`

### Output
- PDF service: Base64 PDF reports + text responses
- PowerPoint service: Base64 .pptx files with standard business template

## Testing

### Local Testing
1. Start Azure Functions: `func start` (runs on localhost:7071)
2. Start React frontend: `npm start` (runs on localhost:3000)
3. Upload documents through the frontend interface

### API Testing
Use the test files in each service directory:
- `azure_function_pdf/test_simplified.py`
- `azure_function_ppt/test_builder.py`

## Common Issues

- Services require Azure OpenAI credentials in environment variables
- Frontend proxy configured for localhost:7071 in package.json
- Large documents may hit token limits (configured per agent in config.py)
- PowerPoint generation has slide count limits (configurable in PRESENTATION_CONFIG)

## Dependencies

### Python (both Azure Functions)
- azure-functions
- semantic-kernel==1.30.0
- openai>=1.0.0
- python-dotenv>=1.0.0
- reportlab>=4.0.0 (PDF service)
- python-pptx>=0.6.23 (PowerPoint service)

### JavaScript (frontend)
- react ^18.2.0
- lucide-react ^0.263.1
- Tailwind CSS (via CDN)