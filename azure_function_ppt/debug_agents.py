#!/usr/bin/env python3
"""
Debug script to test individual agents and see where they're failing
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.smart_presentation_processor_skill import SmartPresentationProcessor
from agents.document_content_extractor_skill import DocumentContentExtractor  
from agents.presentation_structure_agent import PresentationStructureAgent
from agents.slide_content_generator import SlideContentGenerator

# Test document content
test_document = """Project Phoenix: A Strategic Overview

1. Executive Summary

Project Phoenix is a company-wide initiative to modernize our legacy customer relationship management (CRM) platform. The primary goal is to improve operational efficiency, enhance data security, and provide a superior user experience for our sales and support teams.

2. Key Objectives

Our mission is to achieve three core objectives:
- Modernize Technology Stack: Migrate from the outdated on-premise system to a cloud-native, scalable architecture.
- Enhance User Experience: Design an intuitive and responsive user interface that minimizes training time and reduces user error.
- Improve Data Analytics: Implement a centralized data warehouse with real-time reporting dashboards.

3. Project Timeline

The project is divided into three distinct phases:
- Phase 1 (Q3 2024): Discovery & Planning
- Phase 2 (Q4 2024 - Q1 2025): Development & Implementation  
- Phase 3 (Q2 2025): Testing & Deployment"""

async def test_agent(agent_name, agent_class, input_data, context=None):
    """Test individual agent"""
    print(f"\n=== Testing {agent_name} ===")
    try:
        agent = agent_class()
        result = await agent.process(input_data, context)
        print(f"SUCCESS: {len(str(result))} characters returned")
        print(f"First 200 chars: {str(result)[:200]}...")
        return result
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

async def debug_pipeline():
    """Test the entire pipeline step by step"""
    
    # Step 1: Smart Intent Processor
    intent_result = await test_agent(
        "SmartPresentationProcessor", 
        SmartPresentationProcessor,
        "Create a presentation from this document",
        {"has_previous_document": True}
    )
    
    # Step 2: Document Content Extractor
    extracted_content = await test_agent(
        "DocumentContentExtractor",
        DocumentContentExtractor, 
        test_document
    )
    
    # Step 3: Presentation Structure Agent
    if extracted_content:
        structure_result = await test_agent(
            "PresentationStructureAgent",
            PresentationStructureAgent,
            extracted_content
        )
        
        # Step 4: Slide Content Generator
        if structure_result:
            content_result = await test_agent(
                "SlideContentGenerator", 
                SlideContentGenerator,
                structure_result
            )
            
            print(f"\n=== FINAL PIPELINE RESULTS ===")
            print(f"Intent: {'OK' if intent_result else 'FAIL'}")
            print(f"Content Extraction: {'OK' if extracted_content else 'FAIL'}")
            print(f"Structure: {'OK' if structure_result else 'FAIL'}")
            print(f"Content Generation: {'OK' if content_result else 'FAIL'}")

if __name__ == "__main__":
    asyncio.run(debug_pipeline())