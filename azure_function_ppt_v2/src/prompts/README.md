# Centralized Prompt Management System

This directory contains all system prompts used by the PowerPoint Requirements Service v2 agents. The prompts are stored as `.txt` files and loaded dynamically by the `PromptLoader` utility.

## Available Prompts

### conversation_manager_system.txt
System prompt for the ConversationManager agent. Handles:
- User intent analysis
- Conversation flow management
- Automatic clarification workflow triggers
- Content extraction from conversations

### clarification_question_generator_system.txt
System prompt for the ClarificationQuestionGenerator agent. Handles:
- Slide count estimation based on content analysis
- Contextual clarification question generation
- Content complexity assessment

### consolidation_system.txt
System prompt for the consolidation workflow. Handles:
- Combining conversation history and user preferences
- Generating structured summaries for third-party PowerPoint services
- Comprehensive content consolidation

## Variable Replacement

The prompt system supports automatic variable replacement:

### Configuration Variables
- `{MIN_SLIDES}` - Replaced with PRESENTATION_CONFIG.min_slides
- `{MAX_SLIDES}` - Replaced with PRESENTATION_CONFIG.max_slides  
- `{DEFAULT_SLIDES}` - Replaced with PRESENTATION_CONFIG.default_slides

### Custom Variables
Pass custom variables to the `loadPrompt()` method:
```javascript
const prompt = promptLoader.loadPrompt('my_prompt', {
    CUSTOM_VAR: 'value',
    ANOTHER_VAR: 'another value'
});
```

## Usage

### In Agent Classes
```javascript
const { promptLoader } = require('../utils/promptLoader');

// Load a prompt
const systemPrompt = promptLoader.loadPrompt('conversation_manager_system');

// Load with custom variables
const promptWithVars = promptLoader.loadPrompt('my_prompt', {
    USER_NAME: 'John',
    TASK_TYPE: 'analysis'
});
```

### Prompt Management Benefits

1. **Centralized Control**: All prompts in one location for easy management
2. **Version Control**: Track prompt changes through git
3. **Dynamic Loading**: Prompts loaded at runtime, no code redeployment needed
4. **Variable Replacement**: Support for configuration and custom variables
5. **Caching**: Automatic caching for performance
6. **Validation**: Built-in prompt existence validation

## Adding New Prompts

1. Create a new `.txt` file in this directory
2. Write your prompt content with optional variable placeholders
3. Load using `promptLoader.loadPrompt('your_prompt_name')`

## Best Practices

1. **Descriptive Names**: Use clear, descriptive filenames
2. **Variable Naming**: Use `{UPPERCASE}` for variable placeholders
3. **Documentation**: Document prompt purpose and variables in comments
4. **Testing**: Test prompts with various variable combinations
5. **Consistency**: Maintain consistent formatting and structure across prompts