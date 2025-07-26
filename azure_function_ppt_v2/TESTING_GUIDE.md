# Local Testing Guide for PowerPoint Service v2

## Prerequisites

1. **Azure Functions Core Tools** installed globally:
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Node.js 18+** installed

3. **Azure OpenAI credentials** - You'll need the same credentials used in your other services

## Setup Steps

### 1. Install Dependencies
```bash
cd azure_function_ppt_v2
npm install
```

### 2. Configure Environment Variables
Edit the `.env` file with your Azure OpenAI credentials:
```
ENDPOINT_URL=https://your-ai-foundry-endpoint.openai.azure.com/
DEPLOYMENT_NAME=gpt-4.1-ncsgpt-dev
AZURE_OPENAI_API_KEY=your-actual-api-key
API_VERSION=2025-01-01-preview
```

### 3. Start the Local Service
```bash
npm start
```

You should see output like:
```
Azure Functions Core Tools
Core Tools Version:       4.x.x
Function Runtime Version: 4.x.x

Functions:
  powerpointGeneration: [GET,POST] http://localhost:7071/api/powerpointGeneration
```

### 4. Test the Service

#### Option A: Run Automated Tests
```bash
# In another terminal (keep the service running)
npm test
```

#### Option B: Manual API Testing
Use curl or Postman to test:

**Health Check (GET):**
```bash
curl http://localhost:7071/api/powerpointGeneration
```

**Conversation Test (POST):**
```bash
curl -X POST http://localhost:7071/api/powerpointGeneration \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "What kind of presentation would work best for this? [document]Sample business proposal content here...",
    "entra_id": "test-user"
  }'
```

#### Option C: Frontend Testing
If you have a frontend, point it to `http://localhost:7071/api/powerpointGeneration`

## Expected Test Results

### 1. Conversational Flow Test
- ✅ Document upload with questions
- ✅ Context building through follow-up messages
- ✅ Slide count estimation
- ✅ Session management
- ⏳ PowerPoint generation (returns placeholder until PptxGenJS is integrated)

### 2. Agent Pipeline Validation
The service should execute this pipeline:
```
ConversationManager → DocumentProcessor → SlideEstimator → ContentStructurer → PptxGenerator
```

Each agent should return structured JSON data for the next agent in the pipeline.

### 3. Current Limitations
- **PowerPoint generation is placeholder** - Returns mock base64 data
- **No actual .pptx file** - Until PptxGenJS integration is complete
- **Testing phase only** - Service processes conversations and estimates slides correctly

## Troubleshooting

### Common Issues

**1. "Missing required environment variable" error:**
- Check that your `.env` file has all required variables
- Ensure environment variable names match exactly

**2. "OpenAI API call failed" error:**
- Verify your Azure OpenAI credentials are correct
- Check that your deployment name matches your Azure OpenAI model deployment

**3. "Port 7071 already in use" error:**
- Stop any other Azure Functions services running
- Only one service can run on port 7071 at a time

**4. Module not found errors:**
- Run `npm install` to ensure all dependencies are installed
- Check that you're in the correct directory (`azure_function_ppt_v2`)

### Service Logs
The service provides detailed console logging:
- Agent execution steps
- Token usage per AI call
- Processing time measurements
- Error details

## Next Steps

Once local testing is working:
1. Validate the conversational flow works as expected
2. Test with various document types and sizes
3. Confirm slide estimation is reasonable
4. Prepare for PptxGenJS integration in next session

## Development Notes

- The service is designed for deployment to Azure Functions as a **Node.js app**
- All agents follow the same pattern as your Python services but in JavaScript
- Configuration is centralized in `src/config/config.js`
- Test scenarios cover the full conversational workflow