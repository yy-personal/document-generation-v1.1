# PowerPoint Generation Service

Professional PowerPoint generation service that converts PDF/Word documents into standardized business presentations with configurable slide limits.

## Architecture

**Streamlined Pipeline**: Document-to-PowerPoint generation with 4 AI agents + 1 rule-based builder.

```
Document Upload → Intent Analysis → Content Extraction → Structure Planning → Content Generation → PowerPoint Building
      ↓              ↓(AI)             ↓(AI)              ↓(AI)            ↓(AI)              ↓(Rule-based)
   Base64 File     Intent Only    Organized Content   Slide Planning   Detailed Content      .pptx File
```

## Features

✅ **Configurable Slide Limits** - Maximum 15 slides (configurable in config.py)  
✅ **Smart Context Handling** - Continuation requests and conversation memory  
✅ **Simple 2-Color Theme** - Purple (#584dc1) and Gold (#d1b95b) proof of concept  
✅ **Integrated Document Processing** - PDF/Word files via base64 input  
✅ **Consistent Output** - Standard business presentation format  

## Agent Architecture

### Pipeline (5 Steps, 4 AI Calls)
```
1. SmartPresentationProcessor (AI) → Intent classification only
2. DocumentContentExtractor (AI) → Content organization  
3. PresentationStructureAgent (AI) → Content analysis + slide count + structure
4. SlideContentGenerator (AI) → Detailed slide content
5. PowerPointBuilderAgent (Rule-based) → .pptx file with simple theme
```

### Agent Responsibilities

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **SmartPresentationProcessor** | Intent analysis | User request | CREATE_PRESENTATION vs INFORMATION_REQUEST |
| **DocumentContentExtractor** | Content organization | Raw document | Organized topics |
| **PresentationStructureAgent** | Slide planning | Organized content | Slide count + structure |
| **SlideContentGenerator** | Content creation | Slide structure | Detailed content |
| **PowerPointBuilderAgent** | File generation | Slide content | Binary .pptx |

## Configuration

### Slide Limits (config.py)
```python
PRESENTATION_CONFIG = {
    "default_slides": 12,
    "max_slides": 15,        # CONFIGURABLE MAXIMUM
    "min_slides": 8
}
```

### Simple Theme
- **Primary**: #584dc1 (Purple) - Titles
- **Accent**: #d1b95b (Gold) - Available for highlights  
- **Text**: Dark gray - Content
- **Font**: Calibri family

## API Usage

### Endpoint
```
POST /api/powerpoint_generation
```

### Request Examples

**Direct Upload:**
```json
{
  "user_message": "[word_document_extraction]Functional Specification...",
  "entra_id": "user-123"
}
```

**Continuation Request:**
```json
{
  "user_message": "create presentation",
  "session_id": "PPT23072025ABC123",
  "entra_id": "user-123",
  "conversation_history": [...]
}
```

### Response Structure
```json
{
  "response_data": {
    "status": "completed",
    "session_id": "PPT23072025ABC123",
    "processing_info": {
      "intent": {...},
      "slide_planning": {
        "optimal_slides": 12,
        "max_slides_enforced": 15
      }
    },
    "pipeline_info": ["SmartPresentationProcessor", "DocumentContentExtractor", ...],
    "powerpoint_output": {
      "ppt_data": "base64_encoded_content",
      "filename": "presentation_PPT23072025ABC123.pptx"
    }
  }
}
```

## Setup

### Installation
```bash
cd azure_function_ppt
pip install -r requirements.txt
```

### Environment (.env in parent directory)
```env
ENDPOINT_URL=https://your-ai-foundry-endpoint.openai.azure.com/
DEPLOYMENT_NAME=gpt-4.1-ncsgpt-dev
AZURE_OPENAI_API_KEY=your-api-key
API_VERSION=2025-01-01-preview
```

### Local Development
```bash
func start
# Service: http://localhost:7071/api/powerpoint_generation
```

## File Structure
```
azure_function_ppt/
├── agents/
│   ├── smart_presentation_processor_skill.py    # Intent analysis
│   ├── document_content_extractor_skill.py      # Content organization
│   ├── presentation_structure_agent.py          # Slide planning
│   ├── slide_content_generator.py               # Content creation
│   ├── powerpoint_builder_agent.py              # File generation
│   └── core/base_agent.py
├── config.py                    # Configuration with slide limits
├── function_app.py              # Azure Functions entry
├── ppt_orchestrator.py          # Main orchestration logic
└── requirements.txt
```

## Key Features

**Simplified Architecture:**
- Single presentation format (standard business)
- Configurable maximum slides (15 default)
- 2-color theme for proof of concept
- No presentation type complexity

**Smart Processing:**
- Intent-only classification (no premature slide planning)
- Content analysis determines optimal slide count
- Maximum slide enforcement
- Conversation context handling

**Base64 Integration:**
- No server file storage
- Direct frontend download
- Scalable for concurrent users

## Performance

- **Generation Time**: ~12-15 seconds
- **Slide Range**: 8-15 slides (15 max enforced)
- **File Size**: ~50-200KB typical output
- **Memory Usage**: <500MB per request

## Dependencies

```txt
azure-functions
semantic-kernel==1.30.0
openai>=1.0.0
python-dotenv>=1.0.0
python-pptx>=1.0.2
```

---

**PowerPoint Generation Service** - Simplified architecture with configurable slide limits and 2-color theme for efficient business presentation generation.