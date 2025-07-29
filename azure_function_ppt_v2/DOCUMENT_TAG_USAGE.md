# Document Tag Usage Guide

This guide explains how to use document tags with the PowerPoint Generation Service v2.

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