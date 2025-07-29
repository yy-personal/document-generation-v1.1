const { BaseAgent } = require('./core/baseAgent');

/**
 * DocumentProcessor Agent
 * Extracts and organizes content from documents for presentation structure
 */
class DocumentProcessor extends BaseAgent {
    constructor() {
        super('DocumentProcessor');
    }

    async process(input) {
        // Accept either document_content or conversation_content
        const { document_content, conversation_content, user_context, content_source = 'document' } = input;
        
        if (!document_content && !conversation_content) {
            throw new Error('DocumentProcessor requires either document_content or conversation_content');
        }

        // Create system prompt for document processing
        const systemPrompt = this.createDocumentProcessingSystemPrompt();

        // Create user prompt
        const userPrompt = this.createDocumentProcessingUserPrompt({
            document_content,
            conversation_content,
            user_context,
            content_source
        });

        const messages = [
            this.createSystemMessage(systemPrompt),
            this.createUserMessage(userPrompt)
        ];

        // Call AI service
        const aiResponse = await this.callAI(messages);
        const result = this.parseAIResponse(aiResponse.content);

        return result;
    }

    createDocumentProcessingSystemPrompt() {
        return `You are a DocumentProcessor specialized in analyzing content for PowerPoint presentation creation.

## Your Role:
Extract and organize content into structured information suitable for presentation slides from either documents OR conversation content.

## Content Sources:
1. **Document Content**: Traditional documents (reports, proposals, manuals)
2. **Conversation Content**: User-provided topics and details through conversation
3. **Mixed Content**: Combination of documents and conversation details

## Analysis Tasks:
1. **Content Classification**: Identify content type and presentation purpose
2. **Topic Extraction**: Identify main topics and subtopics
3. **Key Information**: Extract important facts, figures, and insights
4. **Structure Analysis**: Understand content flow and hierarchy
5. **Content Complexity**: Assess depth and breadth of information

## Content Organization:
- **Executive Summary**: Key points and presentation purpose
- **Main Topics**: 3-8 primary topics with hierarchical structure
- **Supporting Details**: Important facts, data, examples under each topic
- **Special Content**: Tables, lists, procedures that need special formatting
- **Conclusion Points**: Key takeaways or recommendations

## Conversation Content Processing:
When working with conversation content:
- Extract presentation topics from user messages
- Organize user-provided details into structured format
- Infer content type from user requirements
- Generate logical flow from conversational input
- Fill gaps with standard presentation structure

## Output Format:
Return JSON with:
{
    "content_source": "document|conversation|mixed",
    "document_type": "report|proposal|manual|presentation|educational|business|other",
    "content_complexity": "low|medium|high",
    "executive_summary": "brief overview of content purpose and main points",
    "main_topics": [
        {
            "topic": "topic name",
            "importance": "high|medium|low",
            "content_type": "text|data|procedure|mixed",
            "key_points": ["point1", "point2", ...],
            "supporting_details": ["detail1", "detail2", ...],
            "estimated_slides": number
        }
    ],
    "special_content": {
        "tables": ["description of tables if any"],
        "procedures": ["step-by-step processes if any"],
        "data_points": ["important numbers/metrics if any"]
    },
    "recommendations": "suggested presentation approach based on content"
}

Focus on creating clear, presentation-ready organization regardless of content source.`;
    }

    createDocumentProcessingUserPrompt({ document_content, conversation_content, user_context, content_source }) {
        let prompt = '';

        if (content_source === 'document' && document_content) {
            prompt = `## Document Content:
${document_content}`;
        } else if (content_source === 'conversation' && conversation_content) {
            prompt = `## Conversation Content:
${conversation_content}`;
        } else if (content_source === 'mixed') {
            if (document_content) {
                prompt += `## Document Content:
${document_content}`;
            }
            if (conversation_content) {
                prompt += `${prompt ? '\n\n' : ''}## Additional Conversation Content:
${conversation_content}`;
            }
        }

        if (user_context && user_context.trim()) {
            prompt += `\n\n## User Context:
${user_context}`;
        }

        if (content_source === 'conversation') {
            prompt += `\n\n## Task:
Analyze the conversation content and organize it for PowerPoint presentation creation.

Consider:
- Extract main topics from user's conversational input
- Organize topics into logical presentation flow
- Infer content complexity from user requirements
- Generate supporting details where appropriate
- Determine best presentation approach for this topic

Create a structured format suitable for slide creation from conversational content.`;
        } else {
            prompt += `\n\n## Task:
Analyze this content and organize it for PowerPoint presentation creation. 

Consider:
- What are the main topics that should become slides?
- What type of content formatting is needed (bullets, tables, procedures)?
- How complex is the information (affects slide count estimation)?
- What presentation approach would work best for this content?

Extract and organize the information in a structured format suitable for slide creation.`;
        }

        return prompt;
    }
}

module.exports = { DocumentProcessor };