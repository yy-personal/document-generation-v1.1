# Azure Function PowerPoint Generation v2 - Deployment Guide

## Prerequisites

### Local Development
- **Node.js**: v18.0.0 or higher
- **Python**: 3.9 or higher (for content analysis agent)
- **Azure Functions Core Tools**: v4.0.0 or higher
- **Azure CLI**: Latest version

### Azure Resources
- Azure Functions App (Node.js 18 runtime)
- Azure OpenAI Service
- Application Insights (optional, for monitoring)

## Local Development Setup

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies for content analysis
cd python_agents
pip install -r requirements.txt
cd ..
```

### 2. Configure Environment Variables

Copy `local.settings.json.template` to `local.settings.json` and configure:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "node",
    "ENDPOINT_URL": "https://your-ai-foundry-endpoint.openai.azure.com/",
    "DEPLOYMENT_NAME": "gpt-4.1-ncsgpt-dev",
    "AZURE_OPENAI_API_KEY": "your-api-key",
    "API_VERSION": "2025-01-01-preview"
  }
}
```

### 3. Start Local Development

```bash
# Start the Azure Function locally
func start

# The function will be available at:
# - Main API: http://localhost:7071/api/powerpoint_generation_v2
# - Health Check: http://localhost:7071/api/health_v2
```

### 4. Run Tests

```bash
# Run integration tests
node test/test_integration.js

# Run with npm (if configured)
npm test
```

## Azure Deployment

### 1. Create Azure Resources

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="rg-powerpoint-service"
FUNCTION_APP="func-powerpoint-v2"
LOCATION="Southeast Asia"
STORAGE_ACCOUNT="stpowerpointv2"

# Create resource group
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION" \
  --sku Standard_LRS

# Create function app
az functionapp create \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --storage-account $STORAGE_ACCOUNT \
  --runtime node \
  --runtime-version 18 \
  --functions-version 4 \
  --os-type Linux
```

### 2. Configure Application Settings

```bash
# Set Azure OpenAI configuration
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
  ENDPOINT_URL="https://your-ai-foundry-endpoint.openai.azure.com/" \
  DEPLOYMENT_NAME="gpt-4.1-ncsgpt-dev" \
  AZURE_OPENAI_API_KEY="your-api-key" \
  API_VERSION="2025-01-01-preview"
```

### 3. Deploy Function Code

```bash
# Deploy using Azure Functions Core Tools
func azure functionapp publish $FUNCTION_APP

# Or deploy using Azure CLI
az functionapp deployment source config-zip \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --src deployment.zip
```

### 4. Verify Deployment

```bash
# Test health endpoint
curl https://$FUNCTION_APP.azurewebsites.net/api/health_v2

# Expected response:
# {
#   "status": "healthy",
#   "service": "PowerPoint Generation v2",
#   "version": "2.0.0",
#   "architecture": "hybrid"
# }
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ENDPOINT_URL` | Azure OpenAI endpoint URL | Yes |
| `DEPLOYMENT_NAME` | Azure OpenAI deployment name | Yes |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes |
| `API_VERSION` | Azure OpenAI API version | Yes |
| `PYTHON_AGENT_URL` | Python content analysis service URL | No |

### Function App Settings

- **Runtime**: Node.js 18
- **OS**: Linux (recommended)
- **Plan**: Consumption or Premium
- **Timeout**: 10 minutes (for large document processing)

## Monitoring and Troubleshooting

### Application Insights

Enable Application Insights for monitoring:

```bash
# Create Application Insights resource
az monitor app-insights component create \
  --app $FUNCTION_APP \
  --location "$LOCATION" \
  --resource-group $RESOURCE_GROUP

# Link to Function App
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"
```

### Common Issues

1. **Module not found errors**
   - Ensure all dependencies are listed in `package.json`
   - Run `npm install` before deployment

2. **Azure OpenAI connection fails**
   - Verify endpoint URL and API key
   - Check network security groups and firewall rules

3. **Timeout errors**
   - Increase function timeout in `host.json`
   - Consider using Premium plan for better performance

4. **Memory issues**
   - Monitor memory usage in Application Insights
   - Optimize slide generation for large documents

### Logs and Debugging

```bash
# Stream logs in real-time
func azure functionapp logstream $FUNCTION_APP

# View logs in Azure portal
# Navigate to Function App > Functions > powerpoint_generation_v2 > Monitor
```

## Performance Optimization

### Scaling Configuration

```json
// host.json
{
  "version": "2.0",
  "functionTimeout": "00:10:00",
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxConcurrentRequests": 100,
      "maxOutstandingRequests": 200
    }
  }
}
```

### Memory and CPU

- **Recommended Plan**: Premium P1V2 or higher
- **Memory**: 3.5GB minimum for large document processing
- **CPU**: 1 vCPU minimum

## Security

### API Security

```bash
# Enable function-level authentication
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings AzureWebJobsDisableHomepage=true

# Configure CORS if needed
az functionapp cors add \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins "https://yourdomain.com"
```

### Key Management

- Store sensitive keys in Azure Key Vault
- Use Managed Identity for Azure resource access
- Rotate API keys regularly

## Backup and Disaster Recovery

### Function App Backup

```bash
# Export function app configuration
az functionapp config backup create \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --storage-account $STORAGE_ACCOUNT \
  --container backups
```

### Source Code

- Maintain code in version control (Git)
- Use Azure DevOps or GitHub Actions for CI/CD
- Tag releases for easy rollback

## Support and Maintenance

### Health Monitoring

- Set up alerts for function failures
- Monitor execution duration and memory usage
- Track API response times

### Regular Maintenance

- Update dependencies monthly
- Review and rotate API keys quarterly
- Monitor Azure OpenAI usage and limits
- Test disaster recovery procedures

For additional support, contact the development team or refer to the troubleshooting section in the main README.