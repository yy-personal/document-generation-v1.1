# Azure Function Deployment Guide
## PowerPoint Generation Service v2

Simple deployment guide for `fnncsgptpptagent-v2` Azure Function App.

## Quick Deployment

### 1. Deploy Command
```bash
cd azure_function_ppt_v2
func azure functionapp publish fnncsgptpptagent-v2 --build remote
```

### 2. Why `--build remote` Works
- Your local `node_modules` (1.2GB) is excluded by `.funcignore`
- Azure rebuilds dependencies from `package.json` on their servers
- Faster upload (~50MB source code only)
- No dependency conflicts

## Required Azure Settings

Configure in Azure Portal → Function App → Configuration:
```
ENDPOINT_URL=https://your-ai-foundry-endpoint.openai.azure.com/
DEPLOYMENT_NAME=gpt-4.1-ncsgpt-dev
AZURE_OPENAI_API_KEY=your-api-key
API_VERSION=2025-01-01-preview
```

## Test Deployment

**GET Test:**
```bash
curl https://fnncsgptpptagent-v2.azurewebsites.net/api/powerpointGeneration
```

**Expected Response:**
```json
{
  "service": "PowerPoint Generation v2",
  "status": "running",
  "version": "1.0.0"
}
```

**Stage 1 Test (Clarification Questions):**
```bash
curl -X POST https://fnncsgptpptagent-v2.azurewebsites.net/api/powerpointGeneration \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "[create_presentation]",
    "entra_id": "test-user",
    "session_id": "test-session-123",
    "conversation_history": [
      {
        "session_id": "test-session-123",
        "conversation": [
          {
            "question": "Tell me about AI in business",
            "response": "AI transforms business operations through automation, data analysis, and decision support systems."
          }
        ]
      }
    ]
  }'
```

**Expected Stage 1 Response:**
```json
{
  "response_data": {
    "show_clarification_popup": true,
    "clarification_questions": [
      {
        "id": "slide_count",
        "question": "How many slides would you like? (Recommended: 12 slides based on AI analysis)",
        "field_type": "number",
        "default_value": 12
      }
    ]
  }
}
```

**Stage 2 Test (Generate Presentation):**
```bash
curl -X POST https://fnncsgptpptagent-v2.azurewebsites.net/api/powerpointGeneration \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "[clarification_answers]{\"slide_count\": 10, \"audience_level\": \"Intermediate\", \"include_examples\": true}",
    "entra_id": "test-user",
    "session_id": "test-session-123",
    "conversation_history": [same_as_stage_1]
  }'
```

**Expected Stage 2 Response:**
```json
{
  "response_data": {
    "powerpoint_output": {
      "filename": "presentation_PPTV2...pptx",
      "file_data": "base64_encoded_pptx_file",
      "file_size_kb": 1234
    }
  }
}
```

## File Exclusions (.funcignore)

These files are NOT uploaded:
- `node_modules/` (1.2GB saved!)
- `local_output/`
- `local.settings.json`
- `.env` files

## Troubleshooting

**Build fails:** Check Node.js version in Azure
```bash
func azure functionapp config appsettings set --name fnncsgptpptagent-v2 --settings WEBSITE_NODE_DEFAULT_VERSION=~18
```

**View logs:**
```bash
func azure functionapp logstream fnncsgptpptagent-v2
```

## Deployment Checklist

- [ ] Run deployment command
- [ ] Check Azure Portal shows "Running" 
- [ ] Test GET endpoint
- [ ] Test Stage 1: Clarification questions
- [ ] Test Stage 2: Presentation generation
- [ ] Monitor Application Insights for errors
- [ ] Verify conversation history processing
- [ ] Test bracket notation triggers

## New Features in v2

### 2-Stage Clarification Workflow
- **Stage 1**: AI analyzes conversation → generates contextual questions
- **Stage 2**: User answers → customized PowerPoint generation
- **Processing Time**: 2-3s Stage 1, 6-9s Stage 2
- **AI Efficiency**: Single SlideEstimator call, user choice respected

### Bracket Notation Triggers
- `[create_presentation]` → Triggers clarification questions
- `[clarification_answers]{JSON}` → Triggers presentation generation
- Exact matching prevents AI misinterpretation

### Smart Question Generation
- Up to 5 contextual questions based on conversation content
- Field types: number, select, boolean with validation
- Business vs technical content detection
- AI-powered slide count recommendations

That's it! The `--build remote` handles the heavy lifting.