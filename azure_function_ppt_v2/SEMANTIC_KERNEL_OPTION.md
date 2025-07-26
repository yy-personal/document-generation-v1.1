# Semantic Kernel Integration Option

## Overview

If you want to use Semantic Kernel for consistency with your Python services, here's how to integrate it into the Node.js PowerPoint service.

## Package Changes Required

### 1. Update package.json
```json
{
  "dependencies": {
    "@azure/functions": "^4.0.0",
    "@microsoft/semantic-kernel": "^1.0.0",  // Add this
    "pptxgenjs": "^3.12.0",
    "dotenv": "^16.0.0"
    // Remove: "openai": "^4.0.0"  // No longer needed directly
  }
}
```

### 2. Modified BaseAgent with Semantic Kernel

```javascript
const { Kernel, OpenAIChatCompletion, PromptTemplate } = require('@microsoft/semantic-kernel');

class BaseAgent {
    constructor(agentName) {
        this.agentName = agentName;
        this.config = getAgentConfig(agentName);
        
        // Initialize Semantic Kernel
        this.kernel = new Kernel();
        
        // Add OpenAI service
        const openAIService = new OpenAIChatCompletion({
            modelId: process.env.DEPLOYMENT_NAME,
            endpoint: process.env.ENDPOINT_URL,
            apiKey: process.env.AZURE_OPENAI_API_KEY,
            apiVersion: process.env.API_VERSION
        });
        
        this.kernel.addService(openAIService);
    }

    async callAI(messages, overrides = {}) {
        try {
            // Convert messages to SK format
            const prompt = this.convertMessagesToPrompt(messages);
            
            // Create prompt template
            const promptTemplate = new PromptTemplate({
                template: prompt,
                templateFormat: "semantic-kernel"
            });

            // Execute with Semantic Kernel
            const result = await this.kernel.invokePromptAsync(
                promptTemplate,
                {
                    max_tokens: overrides.max_tokens || this.config.max_tokens,
                    temperature: overrides.temperature || this.config.temperature
                }
            );

            return {
                content: result.value,
                usage: result.metadata?.usage,
                model: result.metadata?.model
            };

        } catch (error) {
            console.error(`[${this.agentName}] SK call failed:`, error);
            throw new Error(`Semantic Kernel call failed for ${this.agentName}: ${error.message}`);
        }
    }

    convertMessagesToPrompt(messages) {
        // Convert OpenAI message format to SK prompt format
        return messages.map(msg => `${msg.role}: ${msg.content}`).join('\n\n');
    }
}
```

## Pros of Using Semantic Kernel

### 1. Consistency
- Same patterns as your Python services
- Familiar agent architecture
- Consistent configuration approaches

### 2. Advanced Features
- Built-in prompt management
- Function calling capabilities
- Planning and orchestration
- Memory and context management

### 3. Microsoft Ecosystem
- Better Azure integration
- Enterprise features
- Future-proofing with Microsoft roadmap

## Cons of Using Semantic Kernel

### 1. Complexity
- Additional abstraction layer
- More complex error handling
- Steeper learning curve

### 2. Performance
- Additional overhead
- More dependencies
- Potentially slower cold starts

### 3. Maturity
- Semantic Kernel JS is newer than Python version
- Fewer examples and community resources
- Potential breaking changes in updates

## Migration Path (If Desired)

If you want to migrate to Semantic Kernel:

### Phase 1: Update Dependencies
```bash
npm uninstall openai
npm install @microsoft/semantic-kernel
```

### Phase 2: Update BaseAgent
- Replace direct OpenAI calls with SK calls
- Update error handling
- Test all agents work correctly

### Phase 3: Enhance with SK Features
- Add prompt templates
- Implement function calling if needed
- Add memory/context features

### Phase 4: Validate
- Run full test suite
- Compare performance
- Ensure feature parity

## Current Recommendation

**For this project, stick with direct OpenAI calls** because:

1. **Our use case is simple** - Just chat completions
2. **Better performance** - Fewer layers
3. **Easier to debug** - Direct API control
4. **Lighter deployment** - Smaller package size
5. **Focus on PptxGenJS integration** - Don't add complexity now

## When to Consider Semantic Kernel

Consider migrating to Semantic Kernel if you need:
- **Complex multi-agent orchestration**
- **Advanced prompt management**
- **Function calling capabilities**
- **Memory across conversations**
- **Planning and reasoning**

For simple AI agent pipelines like ours, direct OpenAI is often the better choice.

## Decision Framework

Ask yourself:
1. Do we need advanced SK features? **No - simple chat completions**
2. Is consistency more important than simplicity? **Simplicity wins for now**
3. Will this complicate PptxGenJS integration? **Yes - additional layer**
4. Is the team familiar with SK JavaScript? **Python SK is different**

**Conclusion: Continue with direct OpenAI for this service.**