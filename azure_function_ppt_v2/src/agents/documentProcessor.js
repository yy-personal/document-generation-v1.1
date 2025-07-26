const { BaseAgent } = require('./baseAgent');

/**
 * DocumentProcessor Agent
 * Extracts and organizes content from documents for presentation structure
 */
class DocumentProcessor extends BaseAgent {
    constructor() {
        super('DocumentProcessor');
    }

    async process(input) {
        this.validateInput(input, ['document_content']);

        const { document_content, user_context } = input;

        // Create system prompt for document processing
        const systemPrompt = this.createDocumentProcessingSystemPrompt();

        // Create user prompt
        const userPrompt = this.createDocumentProcessingUserPrompt({
            document_content,
            user_context
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
        return `You are a DocumentProcessor specialized in analyzing documents for PowerPoint presentation creation.

## Your Role:
Extract and organize document content into structured information suitable for presentation slides.

## Analysis Tasks:
1. **Content Classification**: Identify document type (report, proposal, manual, etc.)
2. **Topic Extraction**: Identify main topics and subtopics
3. **Key Information**: Extract important facts, figures, and insights
4. **Structure Analysis**: Understand document flow and hierarchy
5. **Content Complexity**: Assess depth and breadth of information

## Content Organization:
- **Executive Summary**: Key points if document has summary
- **Main Topics**: 3-8 primary topics with hierarchical structure
- **Supporting Details**: Important facts, data, examples under each topic
- **Special Content**: Tables, lists, procedures that need special formatting
- **Conclusion Points**: Key takeaways or recommendations

## Output Format:
Return JSON with:
{
    "document_type": "report|proposal|manual|presentation|other",
    "content_complexity": "low|medium|high",
    "executive_summary": "brief overview of document purpose and main points",
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

Focus on creating clear, presentation-ready organization of the content.`;
    }

    createDocumentProcessingUserPrompt({ document_content, user_context }) {
        let prompt = `## Document Content:
${document_content}`;

        if (user_context && user_context.trim()) {
            prompt += `\n\n## User Context:
${user_context}`;
        }

        prompt += `\n\n## Task:
Analyze this document and organize its content for PowerPoint presentation creation. 

Consider:
- What are the main topics that should become slides?
- What type of content formatting is needed (bullets, tables, procedures)?
- How complex is the information (affects slide count estimation)?
- What presentation approach would work best for this content?

Extract and organize the information in a structured format suitable for slide creation.`;

        return prompt;
    }
}

module.exports = { DocumentProcessor };