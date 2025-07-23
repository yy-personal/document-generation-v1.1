# PowerPoint Generation Service

Professional PowerPoint generation service that converts PDF/Word documents into standardized business presentations with company branding.

## Overview

**Streamlined Pipeline**: Document-to-PowerPoint generation with 4 AI skills + 1 rule-based builder. Creates professional 12-slide presentations with maximum 15-slide limit.

```
Document Upload → Intent Analysis → Content Extraction → Structure Creation → Slide Generation → PowerPoint Building
      ↓              ↓(AI Skill)      ↓(AI Skill)         ↓(AI Skill)        ↓(AI Skill)       ↓(Rule-based)
   Base64 File      Smart Analysis   Organized Content   Slide Structure    Detailed Content    .pptx File
```

## Features

✅ **Integrated Document Processing** - Handles PDF/Word files with base64 input  
✅ **Smart Slide Optimization** - AI determines optimal slide count (max 15)  
✅ **Professional Branding** - Company color scheme, fonts, and layouts  
✅ **Consistent Output** - Business presentation format with proper structure  
✅ **Efficient Generation** - 4 AI calls for complete presentation creation  
✅ **Base64 Response** - Direct file download via frontend conversion  

## Architecture

### Pipeline (5 Steps, 4 AI Calls)
```
1. Smart Presentation Processor (AI) → Intent detection + slide count estimation (max 15)
2. Document Content Extractor (AI) → Key points and structure identification  
3. Presentation Structure Agent (AI) → Slide sequence and narrative flow
4. Slide Content Generator (AI) → Detailed bullet points and formatting
5. PowerPoint Builder Agent (Rule-based) → Professional .pptx with branding
```

### Skills & Agents Structure
```
agents/
├── smart_presentation_processor_skill.py  # Intent analysis & slide optimization
├── document_content_extractor_skill.py    # Document processing & content extraction
├── presentation_structure_agent.py        # Slide planning & structure
├── slide_content_generator.py             # Detailed content creation
├── powerpoint_builder_agent.py            # File generation with branding
└── core/base_agent.py                      # Base agent functionality
```

## Presentation Configuration

### Slide Count Logic
```python
PRESENTATION_CONFIG = {
    "default_slides": 12,        # Default recommendation
    "max_slides": 15,            # Enforced maximum limit
    "min_slides": 8,             # Minimum for effective presentation
    "use_case": "Standard business presentations for all content types"
}
```

**Slide Count Process:**
1. AI estimates optimal slides based on content volume
2. System enforces 15-slide maximum regardless of estimation
3. Minimum 8 slides maintained for presentation effectiveness

### Standard Structure
```
Slide 1: Title slide with company branding
Slides 2-N: Content slides (organized by document topics)
Final Slide: Summary and key takeaways
```

## API Usage

### Endpoint
```
POST /api/powerpoint_generation
```

### Request Examples

#### PDF Document Processing
```json
{
  "user_message": "create presentation[pdf_extraction]Functional Specification: TechIntel Agent v1.0\n1. Purpose\nThis document outlines...",
  "entra_id": "user-123"
}
```

#### Word Document Processing
```json
{
  "user_message": "[word_document_extraction]Quarterly Sales Report\nExecutive Summary\nQ3 2024 results show strong performance across all regions...",
  "entra_id": "user-123"
}
```

#### Continuation Request
```json
{
  "user_message": "create presentation from the document",
  "session_id": "PPT23072025ABC12345",
  "entra_id": "user-123",
  "conversation_history": [...]
}
```

### Response Structure
```json
{
  "response_data": {
    "status": "completed",
    "session_id": "PPT23072025ABC12345", 
    "conversation_history": [...],
    "processing_info": {
      "intent": {
        "intent": "CREATE_PRESENTATION",
        "confidence": 0.9,
        "estimated_slides": 14,
        "content_highlights": ["Key Topic 1", "Key Topic 2"]
      },
      "max_slides": 15,
      "estimated_slides": 14,
      "file_type": "pdf",
      "response_type": "powerpoint_generation"
    },
    "pipeline_info": [
      "SmartPresentationProcessor",
      "DocumentContentExtractor", 
      "PresentationStructureAgent",
      "SlideContentGenerator",
      "PowerPointBuilderAgent"
    ],
    "powerpoint_output": {
      "ppt_data": "UEsDBBQAAAAIAC1RzVi...",  // Base64 encoded .pptx
      "filename": "presentation_PPT23072025ABC12345.pptx"
    }
  }
}
```

## Frontend Integration

### Base64 to File Conversion
```javascript
function downloadPowerPointFromBase64(base64Data, filename) {
    const binaryString = atob(base64Data);
    const bytes = new Uint8Array(binaryString.length);
    
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    
    const blob = new Blob([bytes], { 
        type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' 
    });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

// Usage
const { ppt_data, filename } = response.response_data.powerpoint_output;
downloadPowerPointFromBase64(ppt_data, filename);
```

## Configuration

### Agent Settings
```python
DEFAULT_AGENT_CONFIGS = {
    "SmartPresentationProcessor": {
        "max_tokens": 4000,
        "temperature": 0.3,    # Structured analysis
        "top_p": 0.8
    },
    "DocumentContentExtractor": {
        "max_tokens": 8000,
        "temperature": 0.4,    # Balanced organization
        "top_p": 0.9
    },
    "PresentationStructureAgent": {
        "max_tokens": 6000,
        "temperature": 0.5,    # Creative structure
        "top_p": 0.9
    },
    "SlideContentGenerator": {
        "max_tokens": 10000,
        "temperature": 0.6,    # Creative content
        "top_p": 0.9
    }
}
```

### Company Branding
```python
COMPANY_DESIGN_STANDARDS = {
    "color_scheme": {
        "primary": "#1F4E79",      # Company blue
        "secondary": "#70AD47",    # Company green  
        "accent": "#C55A11",       # Company orange
        "text_dark": "#2F2F2F",
        "text_light": "#FFFFFF"
    },
    "fonts": {
        "title": ("Calibri", 32, True),
        "subtitle": ("Calibri", 24, False),
        "body": ("Calibri Light", 18, False),
        "footer": ("Calibri", 12, False)
    }
}
```

## Setup

### Installation
```bash
cd azure_function_ppt
pip install -r requirements.txt
```

### Environment Variables
Create `.env` file in parent directory:
```env
ENDPOINT_URL=https://your-ai-foundry-endpoint.openai.azure.com/
DEPLOYMENT_NAME=gpt-4.1-ncsgpt-dev
AZURE_OPENAI_API_KEY=your-api-key
API_VERSION=2025-01-01-preview
```

### Local Development
```bash
# Start Azure Function
func start

# Service available at:
# http://localhost:7071/api/powerpoint_generation
```

### Testing
```bash
# Test with frontend interface
cd ../frontend
npm install && npm start
# Test interface: http://localhost:3000
```

## File Structure
```
azure_function_ppt/
├── agents/
│   ├── core/
│   │   ├── base_agent.py
│   │   └── __init__.py
│   ├── smart_presentation_processor_skill.py
│   ├── document_content_extractor_skill.py
│   ├── presentation_structure_agent.py
│   ├── slide_content_generator.py
│   ├── powerpoint_builder_agent.py
│   └── __init__.py
├── config.py
├── function_app.py
├── ppt_orchestrator.py
├── requirements.txt
├── host.json
├── local.settings.json
└── README.md
```

## Error Handling

### Common Response Statuses
- `completed` - Successful presentation generation
- `waiting_for_file` - No document provided
- `needs_clarification` - Rare, usually auto-resolved
- `error` - Processing failure

### Error Recovery
```python
try:
    response = requests.post(endpoint, json=request_data)
    if response.json()["response_data"]["status"] == "error":
        error_msg = response.json()["response_data"]["error_message"]
        # Handle error appropriately
except Exception as e:
    # Handle request/network errors
    print(f"Request failed: {e}")
```

## Performance

### Generation Metrics
- **Processing Time**: 12-15 seconds average
- **Slide Count**: 8-15 slides (15 max enforced)
- **File Size**: ~50-200KB typical .pptx output
- **Memory Usage**: <500MB per request

### Optimization Features
- **Lazy Loading**: Agents instantiated only when needed
- **Session Management**: Conversation history preserved
- **Content Limits**: AI token limits prevent excessive processing
- **Max Slide Enforcement**: Prevents runaway slide generation

## Dependencies

```txt
azure-functions>=1.0.0
semantic-kernel==1.30.0
openai>=1.0.0
python-dotenv>=1.0.0
python-pptx>=1.0.2
```

## Key Design Decisions

**✅ Simplified Architecture**
- Single presentation format for consistency
- Maximum 15-slide limit for readability
- AI estimates slides, system enforces limits

**✅ Skills vs Agents Naming**
- `_skill.py` for content processing skills
- `_agent.py` for structure/generation agents
- Clear separation of responsibilities

**✅ Base64 Response Format**
- No server file storage required
- Direct frontend download capability
- Scalable for multiple concurrent users

**✅ Company Branding Integration**
- Automatic template application
- Consistent visual standards
- Professional presentation output

---

**PowerPoint Generation Service** - Professional business presentations with intelligent content organization and company branding.
