# PowerPoint Generation Service V2

An improved PowerPoint generation system using **Pandoc + Markdown** approach for better consistency and template compatibility.

## 🚀 Key Improvements in V2

- **Pandoc Integration**: Uses Pandoc for native PowerPoint generation
- **Markdown-Driven**: Agents generate structured markdown instead of complex JSON
- **Better Templates**: Full compatibility with company PowerPoint templates
- **Table Support**: Native markdown table conversion
- **Consistent Output**: Deterministic slide generation
- **Simplified Architecture**: Streamlined 2-agent approach

## 📋 Architecture Overview

### V2 Agent Flow
1. **MarkdownPresentationAgent**: Generates structured markdown from documents
2. **PandocConverter**: Converts markdown to PowerPoint using company templates

### V2 vs V1 Comparison
| Feature | V1 (python-pptx) | V2 (Pandoc) |
|---------|------------------|-------------|
| Template Support | Limited | Full |
| Table Generation | Complex detection | Native markdown |
| Consistency | Variable | Deterministic |
| Agent Count | 5 agents | 2 components |
| Output Quality | Inconsistent | Reliable |

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
cd azure_function_ppt_v2
pip install -r requirements.txt
```

### 2. Install Pandoc
**Windows:**
```bash
# Download from: https://pandoc.org/installing.html
# Or use Chocolatey:
choco install pandoc
```

**Linux/Azure:**
```bash
apt-get update
apt-get install pandoc
```

### 3. Add Your Company Template
1. Place your PowerPoint template in `templates/company_template.pptx`
2. Ensure template has standard layouts (title, content, closing)
3. Template will be automatically detected and used

### 4. Configure Environment
The V2 system uses the same `.env` file as your PDF service in the root directory.
Ensure your root `.env` file contains:
```env
ENDPOINT_URL=https://your-endpoint.openai.azure.com/
DEPLOYMENT_NAME=your-gpt-model
AZURE_OPENAI_API_KEY=your-api-key
API_VERSION=2025-01-01-preview
```

The V2 system automatically loads these from the parent directory.

## 🔧 Usage

### Local Development
```bash
func start
```
The service will be available at: `http://localhost:7073/api/powerpoint_generation_v2`

### API Request Format
```json
{
  "session_id": "optional-session-id",
  "user_message": "Create presentation from [document]base64-content",
  "conversation_history": []
}
```

### API Response Format
```json
{
  "response_data": {
    "status": "completed",
    "session_id": "PPT_V2_25012025ABC123",
    "system_version": "V2_Pandoc_Markdown",
    "powerpoint_output": {
      "ppt_data": "base64-encoded-pptx",
      "filename": "presentation_v2_session.pptx"
    },
    "processing_info": {
      "slide_count": 8,
      "template_used": true,
      "processing_method": "pandoc_markdown"
    }
  }
}
```

## 📝 Markdown Generation

### Agent Output Example
```markdown
---
title: "Digital Transformation Strategy"
author: "Your Company"
date: "2025-01-25"
---

# Digital Transformation Strategy
## Strategic Roadmap 2024-2025

---

## Current State Analysis

- Legacy systems across 47 applications
- Data silos preventing comprehensive BI
- Manual processes consuming 60% capacity

---

## Budget Breakdown

| Category | Q1 Budget | Q2 Budget | Status |
|----------|-----------|-----------|---------|
| Infrastructure | $50,000 | $75,000 | On Track |
| Personnel | $120,000 | $130,000 | Over Budget |

---

## Thank You

Questions and discussion welcome
```

### Pandoc Conversion
The markdown is automatically converted to PowerPoint using your company template with:
- Native table formatting
- Proper slide layouts
- Company branding
- Professional styling

## 🎯 Features

### Template Integration
- **Full Template Support**: Uses your existing PowerPoint templates
- **Brand Consistency**: Maintains logos, colors, fonts
- **Layout Preservation**: Respects slide layouts and designs

### Content Generation
- **Smart Analysis**: Extracts specific content from documents
- **Table Detection**: Converts structured data to native tables
- **Professional Flow**: Standard business presentation structure

### Quality Improvements
- **Consistent Output**: Same input always produces same result
- **Error Handling**: Graceful fallbacks and detailed error reporting
- **Debug Support**: Optional file saving for troubleshooting

## 📊 Configuration

### Presentation Settings (`config.py`)
```python
PRESENTATION_CONFIG = {
    "max_slides": 15,        # Maximum slides (hard limit only)
    # Agents determine optimal slide count based on content
}
```

### Pandoc Settings
```python
PANDOC_CONFIG = {
    "timeout_seconds": 60,
    "slide_level": 2,        # ## headers create slides
    "wrap": "preserve",
    "template_path": "templates/company_template.pptx"
}
```

## 🔍 Testing

### Manual Testing
1. Start the function: `func start`
2. Use your existing frontend or API client
3. Send document with `[document]base64-content` format
4. Check `local_output/` for generated presentations

### Validation
The system includes built-in validation for:
- Markdown structure quality
- Slide count limits
- Template availability
- Content completeness

## 📈 Monitoring

### Processing Information
Each response includes detailed processing info:
- Slide count generated
- Template usage status
- Processing method used
- File size and debug info

### Error Handling
- Graceful degradation if template unavailable
- Fallback to Pandoc defaults
- Detailed error messages for troubleshooting

## 🔄 Migration from V1

To migrate from the original system:
1. Keep V1 running alongside V2
2. Test V2 with your documents and templates
3. Compare output quality and consistency
4. Gradually transition traffic to V2
5. Retire V1 when satisfied with V2 performance

## 📞 Support

For issues or questions:
1. Check template compatibility
2. Verify Pandoc installation
3. Review markdown validation output
4. Check processing_info in API responses