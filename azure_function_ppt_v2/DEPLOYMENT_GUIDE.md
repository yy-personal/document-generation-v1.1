# Azure Function Deployment Guide - Node.js

## Deployment Overview

This PowerPoint Generation Service v2 is designed to be deployed as a **Node.js Azure Function**, not Python.

## Why Node.js for Azure Deployment?

### ✅ Advantages
- **Native PptxGenJS support** - Direct JavaScript library usage
- **No runtime bridging** - Avoids Python → JavaScript subprocess complexity
- **Better performance** - Single runtime environment
- **Azure Functions Node.js support** - Full feature parity with Python
- **Smaller deployment package** - No dual-runtime overhead

### ❌ Python Alternative Issues
- Requires Python → Node.js bridging for PptxGenJS
- Subprocess management complexity
- Larger deployment size
- Potential performance bottlenecks
- More complex error handling

## Deployment Configuration

### 1. Azure Function Settings
```json
{
  "FUNCTIONS_WORKER_RUNTIME": "node",
  "WEBSITE_NODE_DEFAULT_VERSION": "~18",
  "FUNCTIONS_EXTENSION_VERSION": "~4"
}
```

### 2. Application Settings (Environment Variables)
```
ENDPOINT_URL=https://your-ai-foundry-endpoint.openai.azure.com/
DEPLOYMENT_NAME=gpt-4.1-ncsgpt-dev
AZURE_OPENAI_API_KEY=your-api-key
API_VERSION=2025-01-01-preview
```

### 3. Deployment Commands

#### Using Azure CLI:
```bash
# Login to Azure
az login

# Create resource group (if needed)
az group create --name rg-powerpoint-v2 --location eastus

# Create function app
az functionapp create \
  --resource-group rg-powerpoint-v2 \
  --consumption-plan-location eastus \
  --runtime node \
  --runtime-version 18 \
  --functions-version 4 \
  --name powerpoint-gen-v2 \
  --storage-account yourstorageaccount

# Deploy the function
cd azure_function_ppt_v2
func azure functionapp publish powerpoint-gen-v2
```

#### Using VS Code Azure Functions Extension:
1. Install "Azure Functions" extension
2. Sign in to Azure
3. Right-click the `azure_function_ppt_v2` folder
4. Select "Deploy to Function App"
5. Choose "Create new Function App"
6. Select Node.js 18 runtime

### 4. Post-Deployment Configuration

Set environment variables in Azure Portal:
1. Go to your Function App → Configuration
2. Add Application Settings:
   - `ENDPOINT_URL`
   - `DEPLOYMENT_NAME` 
   - `AZURE_OPENAI_API_KEY`
   - `API_VERSION`
3. Save and restart the function app

## Service Architecture in Azure

### Current Deployment Strategy
You'll have **3 separate Azure Function Apps**:

1. **PDF Processing** (Python) - `azure_function_pdf`
2. **PowerPoint v1** (Python) - `azure_function_ppt` 
3. **PowerPoint v2** (Node.js) - `azure_function_ppt_v2` ← This one

### Benefits of Separate Deployments
- **Independent scaling** - Each service scales based on its usage
- **Technology flexibility** - Python for some, Node.js for others
- **Deployment isolation** - Updates to one service don't affect others
- **Resource optimization** - Right-sized compute for each workload

## Performance Considerations

### Cold Start Optimization
- **Consumption Plan**: 2-5 second cold starts (acceptable for conversation flows)
- **Premium Plan**: Always warm instances (better for high-frequency usage)
- **Dedicated Plan**: Predictable performance (if needed)

### Memory and Timeout
- **Default**: 1.5GB memory, 5-minute timeout
- **Recommended**: Monitor actual usage and adjust if needed
- **PptxGenJS generation**: Usually completes in 10-30 seconds

## Testing Deployed Service

### Health Check
```bash
curl https://powerpoint-gen-v2.azurewebsites.net/api/powerpointGeneration
```

### API Test
```bash
curl -X POST https://powerpoint-gen-v2.azurewebsites.net/api/powerpointGeneration \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Test document [document]Sample content...",
    "entra_id": "test-user"
  }'
```

## Monitoring and Logs

### Application Insights
- Automatically enabled with Function App creation
- View logs, performance metrics, and errors
- Set up alerts for failures or performance issues

### Function App Logs
- View real-time logs in Azure Portal
- Monitor agent execution and token usage
- Track conversation flows and session management

## Cost Optimization

### Consumption Plan (Recommended)
- **Pay per execution** - Only charged when function runs
- **Automatic scaling** - Scales up/down based on demand
- **Cost effective** - Good for conversational workloads with variable usage

### Estimated Costs
- **Per conversation**: ~$0.01-0.05 (depending on document complexity)
- **Monthly estimate**: Based on conversation volume
- **OpenAI costs separate**: Main cost factor (token usage)

## Next Steps After Deployment

1. **Test the deployed service** with your frontend
2. **Monitor performance** through Application Insights
3. **Implement PptxGenJS integration** (next development session)
4. **Add company template support** (future enhancement)

The Node.js deployment approach will give you the best performance and simplest architecture for the PptxGenJS-based PowerPoint generation.