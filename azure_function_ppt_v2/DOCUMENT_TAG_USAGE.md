# Document Tag and Bracket Notation Guide

This guide explains how to use document tags and bracket notation with the PowerPoint Generation Service v2.

## New Document Tag Format

The service now supports `[document_start]` and `[document_end]` tags to clearly define where document content begins and ends.

### Basic Usage

```
Create a presentation from this document:
[document_start]
Executive Summary
Our company achieved remarkable growth in Q3 2024, with revenue increasing by 25% compared to the previous quarter.

Key Achievements
- Revenue: $2.3M (up from $1.8M)
- New customers: 150
- Customer retention: 89%
- Product launches: 2 major releases

Future Outlook
We expect continued growth in Q4 with the launch of our new product line and expanded market presence.
[document_end]

Please focus on the key metrics and make it suitable for executive presentation.
```

### Benefits of New Format

1. **Clear Boundaries**: Explicitly defines where document content starts and ends
2. **Mixed Content Support**: Allows user text before and after document content
3. **Multiline Documents**: Handles complex documents with multiple sections
4. **Better Parsing**: More reliable extraction of document content

### Examples

#### Example 1: Document with Instructions

```
User: I need help creating slides from this report. Please focus on the financial highlights.
[document_start]
Annual Financial Report 2024
Total Revenue: $12.5M
Operating Expenses: $8.2M
Net Profit: $4.3M
Growth Rate: 18% YoY
[document_end]
Make it suitable for board presentation.
```

#### Example 2: Complex Document Structure

```
User: Transform this into a training presentation:
[document_start]
Training Manual: Customer Service Excellence

Module 1: Communication Skills
- Active listening techniques
- Empathy in customer interactions
- Clear and concise messaging

Module 2: Problem Resolution
- Identifying root causes
- Escalation procedures
- Follow-up protocols

Module 3: Product Knowledge
- Features and benefits
- Common use cases
- Troubleshooting basics
[document_end]
Target audience: New customer service representatives.
```

#### Example 3: Conversation-Only (No Document)

```
User: Create a presentation about artificial intelligence basics for business executives.
```

The service can now create presentations entirely from conversation content without requiring any documents.

## Backward Compatibility

The service still supports the legacy `[document]` format for backward compatibility:

```
User: Create presentation [document]Legacy content here
```

However, we recommend using the new `[document_start]` and `[document_end]` format for better content parsing and user experience.

## Response Examples

### With Document Tags
- The service extracts the document content separately from user instructions
- Provides slide count estimates based on document complexity
- Creates presentations that combine document content with user requirements

### Without Document Tags (Conversation-Only)
- The service builds presentations from conversational topic requests
- Asks clarifying questions to gather sufficient detail
- Estimates slide counts based on topic breadth and complexity
- Generates complete presentations from conversation content alone

## Testing the New Format

Use the test script to verify the new document tag functionality:

```bash
cd azure_function_ppt_v2
node test/test-document-tags.js
```

This will verify that document extraction works correctly with both new and legacy formats.

## Bracket Notation for Frontend Integration

The service uses special bracket notation for exact frontend trigger matching:

### Action Triggers

#### 1. Create Presentation Trigger
```json
{
  "user_message": "[create_presentation]",
  "conversation_history": [conversation_data],
  "session_id": "session-123",
  "entra_id": "user-id"
}
```

**Response**: Clarification questions popup with AI slide recommendations

#### 2. Clarification Answers Trigger
```json
{
  "user_message": "[clarification_answers]{\"slide_count\": 12, \"audience_level\": \"Intermediate\", \"include_examples\": true}",
  "conversation_history": [same_conversation_data],
  "session_id": "session-123", 
  "entra_id": "user-id"
}
```

**Response**: Customized PowerPoint generation based on user answers

### Bracket Notation Rules

1. **Exact Matching**: Brackets must match exactly `[create_presentation]`
2. **No Spaces**: No extra spaces inside brackets
3. **Case Sensitive**: Use exact case as specified
4. **JSON Format**: Answers must be valid JSON after `[clarification_answers]`

### Conversation History Format

The service expects conversation history in this format:

```json
{
  "conversation_history": [
    {
      "session_id": "session-123",
      "total_questions": 3,
      "conversation": [
        {
          "question_id": "uuid-1",
          "question": "Tell me about robotics in workplace",
          "response_id": "uuid-2", 
          "response": "Robotics in workplace involves automation...",
          "response_timestamp": "2025-07-29T06:02:15.905Z"
        },
        {
          "question_id": "uuid-3",
          "question": "What about the history of robotics?",
          "response_id": "uuid-4",
          "response": "The history of robotics spans from ancient myths...",
          "response_timestamp": "2025-07-29T06:02:41.329Z"
        }
      ]
    }
  ]
}
```

### Combined Usage: Documents + Bracket Notation

You can combine document tags with bracket notation:

```json
{
  "user_message": "[create_presentation] Based on this quarterly report: [document_start]Q3 2024 Results...[document_end]",
  "conversation_history": [conversation_data],
  "session_id": "session-123",
  "entra_id": "user-id"
}
```

The service will:
1. Detect the `[create_presentation]` trigger
2. Extract document content from `[document_start]...[document_end]`
3. Generate clarification questions based on both conversation and document content

### Testing Bracket Notation

Use the updated test scripts:

```bash
cd azure_function_ppt_v2

# Test 2-stage clarification workflow with brackets
node test/test-clarification-workflow.js

# Test document tags with brackets
node test/test-document-tags.js
```

Both document tags and bracket notation work together to provide a complete frontend integration solution.