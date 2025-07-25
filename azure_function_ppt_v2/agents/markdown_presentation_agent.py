"""
Markdown Presentation Agent - Generates structured markdown for Pandoc conversion
"""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from agents.base_agent import BaseAgent
from config import get_ai_service, apply_config_overrides, get_max_slides
from typing import Dict, Any, Optional
from datetime import datetime
import re

class MarkdownPresentationAgent(BaseAgent):
    """Generates presentation content as structured markdown for Pandoc conversion"""

    agent_description = "Creates structured markdown presentations optimized for PowerPoint templates"
    agent_use_cases = [
        "Document content analysis and extraction",
        "Markdown slide generation with table support", 
        "Template-aware content structuring",
        "Pandoc-optimized presentation formatting"
    ]

    def __init__(self, **kwargs):
        super().__init__()
        config = apply_config_overrides(self.__class__.__name__, **kwargs)
        self.service, self.default_execution_settings = get_ai_service(**config)

        instructions = f"""
        You are a Markdown Presentation Specialist that creates structured presentations optimized for PowerPoint templates via Pandoc conversion.

        YOUR CORE RESPONSIBILITY:
        Generate well-structured markdown that will create professional PowerPoint presentations when converted by Pandoc using company templates.

        MARKDOWN STRUCTURE REQUIREMENTS:
        
        1. **YAML Front Matter** (always include):
        ```yaml
        ---
        title: "Specific Presentation Title Based on Content"
        author: "Company Name"
        date: "{datetime.now().strftime('%Y-%m-%d')}"
        ---
        ```

        2. **Slide Structure**:
        - `# Title` → Title slide (use once at start)
        - `## Slide Title` → Content slides
        - `---` → Slide breaks (between slides)

        3. **Content Types**:
        - **Lists**: Use `-` for bullet points (let template handle styling)
        - **Tables**: Use standard markdown tables for structured data
        - **Emphasis**: Use `**bold**` and `*italic*` sparingly
        - **Two-column layouts**: Use Pandoc div syntax when needed

        CONTENT ANALYSIS GUIDELINES:
        - Extract SPECIFIC information from the provided document
        - Create meaningful, descriptive slide titles (not generic ones)
        - Identify when data should be presented as tables vs bullets
        - Maintain professional tone suitable for business presentations
        - Include actual facts, numbers, dates, and details from source
        - DETERMINE optimal slide count based on content density and complexity
        - Maximum {get_max_slides()} slides allowed (hard limit)

        TABLE DETECTION RULES:
        Create tables when content contains:
        - Budget/financial data with amounts
        - Timeline information with dates
        - Comparative data (before/after, metrics)
        - Structured lists with categories and values
        - Team/resource allocation information

        SLIDE SEQUENCE (Standard Business Format):
        1. Title Slide - Main topic and context
        2. Agenda/Overview - What will be covered
        3. Content Slides - Main insights (YOU determine count based on content complexity)
        4. Summary - Key takeaways
        5. Thank You - Closing slide
        
        SLIDE COUNT DETERMINATION:
        - Analyze content complexity and determine optimal slide count
        - Light content (1-2 main topics): 5-7 slides
        - Medium content (3-4 main topics): 8-10 slides  
        - Heavy content (5+ main topics): 11-{get_max_slides()} slides
        - Let content drive the decision, not arbitrary targets

        TABLE FORMATTING EXAMPLE:
        ```markdown
        ## Budget Breakdown

        | Category | Q1 Budget | Q2 Budget | Status |
        |----------|-----------|-----------|---------|
        | Infrastructure | $50,000 | $75,000 | On Track |
        | Personnel | $120,000 | $130,000 | Over Budget |
        ```

        TWO-COLUMN LAYOUT EXAMPLE:
        ```markdown
        ## Strategic Objectives

        ::: {{.columns}}
        :::: {{.column width="50%"}}
        **Technology Modernization**
        - Cloud migration strategy
        - API-first architecture
        ::::
        :::: {{.column width="50%"}}  
        **Process Automation**
        - Workflow digitization
        - AI-powered insights
        ::::
        :::
        ```

        CRITICAL REQUIREMENTS:
        - Base ALL content on the provided document - no generic business content
        - Use specific, descriptive titles that reflect actual document topics
        - Create 6-12 slides based on content density
        - Include actual data, dates, names, and facts from the source
        - Format structured data as tables when appropriate
        - Output ONLY valid markdown - no explanations or meta-commentary

        Your entire response must be properly formatted markdown ready for Pandoc conversion.
        """

        self.agent = ChatCompletionAgent(
            service=self.service,
            name=self.__class__.__name__,
            instructions=instructions
        )

    async def process(self, document_content: str, context_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate structured markdown presentation from document content"""
        try:
            # Analyze the document content first
            content_analysis = self._analyze_document_content(document_content)
            
            generation_prompt = f"""
            DOCUMENT CONTENT ANALYSIS & MARKDOWN GENERATION:
            
            DOCUMENT TO ANALYZE:
            {document_content[:15000]}  # Limit to prevent token overflow
            
            CONTENT ANALYSIS RESULTS:
            - Main Topics: {content_analysis['main_topics']}
            - Has Structured Data: {content_analysis['has_structured_data']}
            - Key Entities: {content_analysis['key_entities']}
            
            TASK: Generate a complete markdown presentation based on this specific document content.
            
            REQUIREMENTS:
            1. Start with YAML front matter using a specific title derived from the content
            2. DETERMINE optimal slide count based on content complexity (max {get_max_slides()} slides)
            3. Use descriptive titles that reflect the actual document topics
            4. Convert structured data to markdown tables where appropriate
            5. Include specific details, numbers, dates, and facts from the document
            6. Follow standard business presentation flow
            7. Output ONLY the markdown - no explanations
            
            SLIDE COUNT DECISION:
            Based on the analysis showing {len(content_analysis['main_topics'])} main topics, 
            YOU decide the optimal number of slides to properly present this content.
            
            Generate the complete markdown presentation now:
            """
            
            self.add_user_message(generation_prompt)
            
            arguments = KernelArguments(settings=self.default_execution_settings)
            
            response = await self.agent.get_response(
                messages=self.get_conversation_history(),
                arguments=arguments
            )

            # Handle semantic kernel response
            if hasattr(response, 'message'):
                response_content = str(response.message.content) if hasattr(response.message, 'content') else str(response.message)
            elif isinstance(response, list) and len(response) > 0:
                last_message = response[-1]
                response_content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
            else:
                response_content = str(response)

            self.add_assistant_message(response_content)
            
            # Clean and validate the markdown
            cleaned_markdown = self._clean_and_validate_markdown(response_content)
            
            return cleaned_markdown

        except Exception as e:
            print(f"Markdown generation error: {str(e)}")
            return self._create_fallback_markdown(document_content)

    def _analyze_document_content(self, content: str) -> dict:
        """Analyze document content to inform markdown generation"""
        analysis = {
            'main_topics': [],
            'has_structured_data': False,
            'key_entities': []
        }
        
        # Split content into sections for topic analysis
        sections = content.split('\n\n')
        sections = [s.strip() for s in sections if s.strip() and len(s.strip()) > 20]
        
        # Extract main topics (first sentence of each significant section)
        for section in sections[:8]:  # Limit to prevent too many topics
            first_sentence = section.split('.')[0].strip()
            if len(first_sentence) > 10 and len(first_sentence) < 100:
                analysis['main_topics'].append(first_sentence)
        
        # Detect structured data patterns
        structured_patterns = [
            r'\$[\d,]+',  # Money amounts
            r'\d+%',      # Percentages  
            r'\d{1,2}/\d{1,2}/\d{4}',  # Dates
            r'Q[1-4]\s+\d{4}',  # Quarters
            r'[A-Z][a-z]+\s*:\s*[A-Z]',  # Key-value pairs
        ]
        
        structured_matches = 0
        for pattern in structured_patterns:
            if re.search(pattern, content):
                structured_matches += 1
        
        analysis['has_structured_data'] = structured_matches >= 2
        
        # Extract key entities (capitalized phrases, numbers, dates)
        entities = re.findall(r'\b[A-Z][A-Za-z\s]{2,30}(?=\s|$|,|\.|:)', content)
        analysis['key_entities'] = list(set(entities[:10]))  # Top 10 unique entities
            
        return analysis

    def _clean_and_validate_markdown(self, markdown_content: str) -> str:
        """Clean and validate generated markdown"""
        # Remove any markdown code block wrapper if present
        if '```markdown' in markdown_content:
            markdown_content = markdown_content.split('```markdown')[1].split('```')[0]
        elif '```' in markdown_content and markdown_content.count('```') >= 2:
            # Remove any code block wrappers
            parts = markdown_content.split('```')
            if len(parts) >= 2:
                markdown_content = parts[1]
        
        # Ensure YAML front matter exists
        if not markdown_content.strip().startswith('---'):
            yaml_header = f"""---
title: "Business Presentation"
author: "Company"
date: "{datetime.now().strftime('%Y-%m-%d')}"
---

"""
            markdown_content = yaml_header + markdown_content
        
        # Ensure proper slide breaks
        lines = markdown_content.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            cleaned_lines.append(line)
            # Add slide break after ## headings (except the last one)
            if line.startswith('## ') and i < len(lines) - 1:
                # Check if next non-empty line is another heading
                next_content_line = None
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        next_content_line = lines[j]
                        break
                
                if next_content_line and next_content_line.startswith('## '):
                    cleaned_lines.append('')
                    cleaned_lines.append('---')
                    cleaned_lines.append('')
        
        return '\n'.join(cleaned_lines)

    def _create_fallback_markdown(self, content: str) -> str:
        """Create basic markdown presentation when AI generation fails"""
        # Extract basic information for fallback
        content_preview = content[:500] + "..." if len(content) > 500 else content
        
        fallback_markdown = f"""---
title: "Document Analysis Presentation"
author: "Company"
date: "{datetime.now().strftime('%Y-%m-%d')}"
---

# Document Analysis Presentation
## Professional Business Review

---

## Overview

Based on the provided document analysis:

- Document contains key business information
- Analysis covers multiple aspects and topics
- Content has been structured for presentation

---

## Key Content Areas

- Primary focus areas identified from document
- Strategic insights and important findings
- Relevant data and supporting information

---

## Document Insights

{content_preview}

---

## Summary

- Document analysis completed successfully
- Key insights extracted and organized
- Ready for detailed business review

---

## Thank You

Questions and discussion welcome
"""
        
        return fallback_markdown