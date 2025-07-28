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
- [ ] Test POST with document upload
- [ ] Monitor Application Insights for errors

That's it! The `--build remote` handles the heavy lifting.