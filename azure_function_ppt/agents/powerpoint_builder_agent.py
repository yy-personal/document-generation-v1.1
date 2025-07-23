"""
PowerPoint Builder Agent - Rule-based PowerPoint file generation
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
import json
import re
import io
import base64

class PowerPointBuilderAgent(BaseAgent):
    """Builds actual PowerPoint files with company branding"""

    agent_description = "Rule-based PowerPoint file generation with company branding"
    agent_use_cases = [
        "PowerPoint file creation from slide content",
        "Company branding application",
        "Template-based slide generation",
        "Professional formatting"
    ]

    def __init__(self, **kwargs):
        super().__init__()

    async def process(self, slide_content: str, context_metadata: Optional[Dict[str, Any]] = None) -> bytes:
        """Generate PowerPoint file from slide content"""
        try:
            presentation_type = context_metadata.get("presentation_type", "GENERAL_PRESENTATION") if context_metadata else "GENERAL_PRESENTATION"
            session_id = context_metadata.get("session_id", "DEFAULT") if context_metadata else "DEFAULT"
            
            # Parse slide content
            slides_data = self._parse_slide_content(slide_content)
            
            # Create presentation
            prs = Presentation()
            
            # Apply company branding
            self._apply_company_branding(prs)
            
            # Generate slides
            for slide_info in slides_data:
                self._create_slide(prs, slide_info)
            
            # Save to bytes
            ppt_buffer = io.BytesIO()
            prs.save(ppt_buffer)
            ppt_buffer.seek(0)
            
            return ppt_buffer.read()
            
        except Exception as e:
            print(f"PowerPoint building error: {str(e)}")
            raise Exception(f"Failed to generate PowerPoint: {str(e)}")

    def _parse_slide_content(self, slide_content: str) -> list:
        """Parse slide content into structured data"""
        slides = []
        
        try:
            # Try to parse as JSON first
            if slide_content.strip().startswith('{') or slide_content.strip().startswith('['):
                content_data = json.loads(slide_content)
                if isinstance(content_data, list):
                    return content_data
                elif isinstance(content_data, dict) and 'slides' in content_data:
                    return content_data['slides']
            
            # Fallback: Parse markdown-style content
            return self._parse_markdown_content(slide_content)
            
        except json.JSONDecodeError:
            return self._parse_markdown_content(slide_content)

    def _parse_markdown_content(self, content: str) -> list:
        """Parse markdown-style slide content"""
        slides = []
        lines = content.split('\n')
        current_slide = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Slide title (# or ##)
            if line.startswith('# ') or line.startswith('## '):
                if current_slide:
                    slides.append(current_slide)
                current_slide = {
                    "title": line.lstrip('# '),
                    "content": [],
                    "layout": "CONTENT_SLIDE"
                }
            # Bullet points
            elif line.startswith('- ') or line.startswith('* '):
                if current_slide:
                    current_slide["content"].append(line.lstrip('- *'))
            # Regular text
            elif line and current_slide:
                current_slide["content"].append(line)
        
        if current_slide:
            slides.append(current_slide)
        
        # Ensure we have at least a title slide
        if not slides:
            slides = [{
                "title": "Generated Presentation",
                "content": ["Content extracted from document"],
                "layout": "TITLE_SLIDE"
            }]
        
        # Set first slide as title slide if not specified
        if slides[0]["layout"] != "TITLE_SLIDE":
            slides[0]["layout"] = "TITLE_SLIDE"
        
        return slides

    def _apply_company_branding(self, prs: Presentation):
        """Apply company branding to presentation master"""
        from config import COMPANY_DESIGN_STANDARDS
        
        # This would typically involve modifying the slide master
        # For now, we'll apply branding per slide
        pass

    def _create_slide(self, prs: Presentation, slide_info: dict):
        """Create individual slide with content"""
        from config import COMPANY_DESIGN_STANDARDS
        
        layout = slide_info.get("layout", "CONTENT_SLIDE")
        title = slide_info.get("title", "Slide Title")
        content = slide_info.get("content", [])
        
        if layout == "TITLE_SLIDE":
            slide_layout = prs.slide_layouts[0]  # Title slide layout
        else:
            slide_layout = prs.slide_layouts[1]  # Content slide layout
        
        slide = prs.slides.add_slide(slide_layout)
        
        # Set title
        if slide.shapes.title:
            slide.shapes.title.text = title
            self._format_title(slide.shapes.title)
        
        # Add content
        if hasattr(slide, 'placeholders') and len(slide.placeholders) > 1:
            content_placeholder = slide.placeholders[1]
            if content_placeholder.has_text_frame:
                text_frame = content_placeholder.text_frame
                text_frame.clear()
                
                # Add content paragraphs
                for i, item in enumerate(content[:6]):  # Max 6 items per slide
                    if i == 0:
                        p = text_frame.paragraphs[0]
                    else:
                        p = text_frame.add_paragraph()
                    
                    p.text = str(item)
                    p.level = 0
                    self._format_content_paragraph(p)

    def _format_title(self, title_shape):
        """Apply title formatting"""
        from config import COMPANY_DESIGN_STANDARDS
        
        if title_shape.has_text_frame:
            text_frame = title_shape.text_frame
            for paragraph in text_frame.paragraphs:
                for run in paragraph.runs:
                    font = run.font
                    font.name = 'Calibri'
                    font.size = Pt(32)
                    font.bold = True
                    font.color.rgb = RGBColor(47, 47, 47)  # text_dark

    def _format_content_paragraph(self, paragraph):
        """Apply content paragraph formatting"""
        from config import COMPANY_DESIGN_STANDARDS
        
        for run in paragraph.runs:
            font = run.font
            font.name = 'Calibri Light'
            font.size = Pt(18)
            font.color.rgb = RGBColor(47, 47, 47)  # text_dark

    def _add_company_footer(self, slide):
        """Add company footer to slide"""
        from config import COMPANY_DESIGN_STANDARDS
        
        # Add footer text box
        left = Inches(0.5)
        top = Inches(7)
        width = Inches(9)
        height = Inches(0.5)
        
        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.text = COMPANY_DESIGN_STANDARDS["branding"]["footer_template"]
        
        # Format footer
        for paragraph in text_frame.paragraphs:
            paragraph.alignment = PP_ALIGN.CENTER
            for run in paragraph.runs:
                font = run.font
                font.name = 'Calibri'
                font.size = Pt(12)
                font.color.rgb = RGBColor(47, 47, 47)
