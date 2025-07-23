"""
PowerPoint Builder Agent - Simplified with 2-color theme
"""
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
import json
import io

class PowerPointBuilderAgent(BaseAgent):
    """Builds PowerPoint files with simple 2-color theme"""

    # Simple color theme
    PRIMARY_COLOR = RGBColor(88, 77, 193)    # #584dc1 (purple)
    ACCENT_COLOR = RGBColor(209, 185, 91)    # #d1b95b (gold)
    TEXT_COLOR = RGBColor(51, 51, 51)        # Dark gray

    agent_description = "Simple PowerPoint file generation with 2-color theme"
    agent_use_cases = [
        "PowerPoint file creation from slide content",
        "Simple theme application",
        "Professional formatting"
    ]

    def __init__(self, **kwargs):
        super().__init__()

    async def process(self, slide_content: str, context_metadata: Optional[Dict[str, Any]] = None) -> bytes:
        """Generate PowerPoint file from slide content"""
        try:
            slides_data = self._parse_slide_content(slide_content)
            prs = Presentation()
            
            for slide_info in slides_data:
                self._create_slide(prs, slide_info)
            
            ppt_buffer = io.BytesIO()
            prs.save(ppt_buffer)
            ppt_buffer.seek(0)
            
            return ppt_buffer.read()
            
        except Exception as e:
            print(f"PowerPoint building error: {str(e)}")
            raise Exception(f"Failed to generate PowerPoint: {str(e)}")

    def _parse_slide_content(self, slide_content: str) -> list:
        """Parse slide content into structured data"""
        try:
            if slide_content.strip().startswith(('[', '{')):
                content_data = json.loads(slide_content)
                return content_data if isinstance(content_data, list) else content_data.get('slides', [])
        except json.JSONDecodeError:
            pass
        
        return self._parse_markdown_content(slide_content)

    def _parse_markdown_content(self, content: str) -> list:
        """Parse markdown-style slide content"""
        slides = []
        current_slide = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith(('# ', '## ')):
                if current_slide:
                    slides.append(current_slide)
                current_slide = {
                    "title": line.lstrip('# '),
                    "content": [],
                    "layout": "TITLE_SLIDE" if not slides else "CONTENT_SLIDE"
                }
            elif line.startswith(('- ', '* ')) and current_slide:
                current_slide["content"].append(line.lstrip('- *'))
            elif line and current_slide:
                current_slide["content"].append(line)
        
        if current_slide:
            slides.append(current_slide)
        
        if not slides:
            slides = [{
                "title": "Generated Presentation",
                "content": ["Content extracted from document"],
                "layout": "TITLE_SLIDE"
            }]
        
        return slides

    def _create_slide(self, prs: Presentation, slide_info: dict):
        """Create individual slide with simple formatting"""
        layout = slide_info.get("layout", "CONTENT_SLIDE")
        title = slide_info.get("title", "Slide Title")
        content = slide_info.get("content", [])
        
        slide_layout = prs.slide_layouts[0] if layout == "TITLE_SLIDE" else prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        # Format title
        if slide.shapes.title:
            slide.shapes.title.text = title
            self._apply_title_format(slide.shapes.title)
        
        # Add content
        if len(slide.placeholders) > 1 and content:
            content_placeholder = slide.placeholders[1]
            if content_placeholder.has_text_frame:
                text_frame = content_placeholder.text_frame
                text_frame.clear()
                
                for i, item in enumerate(content[:6]):  # Max 6 items
                    p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
                    p.text = str(item)
                    self._apply_content_format(p)

    def _apply_title_format(self, title_shape):
        """Apply title formatting with primary color"""
        if title_shape.has_text_frame:
            for paragraph in title_shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    font = run.font
                    font.name = 'Calibri'
                    font.size = Pt(32)
                    font.bold = True
                    font.color.rgb = self.PRIMARY_COLOR

    def _apply_content_format(self, paragraph):
        """Apply content formatting"""
        for run in paragraph.runs:
            font = run.font
            font.name = 'Calibri'
            font.size = Pt(18)
            font.color.rgb = self.TEXT_COLOR