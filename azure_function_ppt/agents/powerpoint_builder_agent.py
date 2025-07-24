"""
PowerPoint Builder Agent - With template support
"""
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
from config import get_template_path
import json
import io
import os

class PowerPointBuilderAgent(BaseAgent):
    """Builds PowerPoint files with simple 2-color theme"""

    # Simple color theme
    PRIMARY_COLOR = RGBColor(88, 77, 193)    # #584dc1 (purple)
    ACCENT_COLOR = RGBColor(209, 185, 91)    # #d1b95b (gold)
    TEXT_COLOR = RGBColor(51, 51, 51)        # Dark gray

    agent_description = "PowerPoint file generation with template support"
    agent_use_cases = [
        "PowerPoint file creation from slide content",
        "Template-based presentation generation",
        "Custom branding and layouts", 
        "Professional formatting"
    ]

    def __init__(self, **kwargs):
        super().__init__()

    async def process(self, slide_content: str, context_metadata: Optional[Dict[str, Any]] = None) -> bytes:
        """Generate PowerPoint file from slide content with template support"""
        try:
            slides_data = self._parse_slide_content(slide_content)
            
            # Use template if available
            template_path = get_template_path("default")
            if template_path:
                print(f"Using template: {template_path}")
                prs = Presentation(template_path)
            else:
                print("Using python-pptx default template")
                prs = Presentation()
            
            for slide_info in slides_data:
                self._create_slide(prs, slide_info)
            
            ppt_buffer = io.BytesIO()
            prs.save(ppt_buffer)
            ppt_buffer.seek(0)
            
            return ppt_buffer.read()
            
        except Exception as e:
            print(f"PowerPoint building error: {str(e)}")
            # If template failed, try without template
            if "template" in str(e).lower():
                print("Template failed, falling back to default")
                try:
                    slides_data = self._parse_slide_content(slide_content)
                    prs = Presentation()  # Use default
                    
                    for slide_info in slides_data:
                        self._create_slide(prs, slide_info)
                    
                    ppt_buffer = io.BytesIO()
                    prs.save(ppt_buffer)
                    ppt_buffer.seek(0)
                    
                    return ppt_buffer.read()
                except Exception as fallback_error:
                    raise Exception(f"Failed to generate PowerPoint even with fallback: {str(fallback_error)}")
            
            raise Exception(f"Failed to generate PowerPoint: {str(e)}")

    def _parse_slide_content(self, slide_content: str) -> list:
        """Parse slide content into structured data"""
        try:
            # Clean up potential markdown formatting around JSON
            if '```json' in slide_content:
                slide_content = slide_content.split('```json')[1].split('```')[0]

            if slide_content.strip().startswith(('[', '{')):
                content_data = json.loads(slide_content)
                # Handle cases where the JSON is a dict with a 'slides' key
                if isinstance(content_data, dict):
                    return content_data.get('slides') or content_data.get('presentation_structure', [])
                return content_data
        except (json.JSONDecodeError, IndexError):
            # Fallback to markdown if JSON parsing fails
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
        """Create individual slide with formatting based on slide type"""
        # Get slide type and determine layout
        slide_type = slide_info.get("slide_type") or slide_info.get("layout", "CONTENT_SLIDE")
        title = slide_info.get("title", "Slide Title")
        
        # Content can come from either "content" (detailed) or "content_outline" (structure)
        content = slide_info.get("content") or slide_info.get("content_outline", [])
        
        try:
            # Determine the appropriate PowerPoint layout based on slide type
            slide_layout_index = self._get_layout_index(slide_type, prs)
            slide_layout = prs.slide_layouts[slide_layout_index]
            slide = prs.slides.add_slide(slide_layout)
            
            print(f"Creating slide: {title} (type: {slide_type}, layout: {slide_layout_index})")
            print(f"Available placeholders: {len(slide.placeholders)}")
            
            # Apply type-specific formatting
            self._format_slide_by_type(slide, slide_type, title, content)
            
        except Exception as e:
            print(f"Error creating slide '{title}' of type '{slide_type}': {str(e)}")
            # Try with a simpler approach - just set title if possible
            slide_layout = prs.slide_layouts[0]  # Use title layout as fallback
            slide = prs.slides.add_slide(slide_layout)
            if slide.shapes.title:
                slide.shapes.title.text = title
            raise e

    def _get_layout_index(self, slide_type: str, prs: Presentation) -> int:
        """Get appropriate layout index based on slide type and template structure"""
        # Template structure mapping (default_template.pptx):
        # Layout 0: Presentation title, date time (slide 1)
        # Layout 1: Presentation title, date time duplicate (slide 2) 
        # Layout 2: Agenda, divider title (slide 3)
        # Layout 3: Stand out message (slide 4)
        # Layout 4: Content slide - side by side, 2-4 rows (slide 5)
        # Layout 5: Content slide - side by side, 2-4 rows (slide 6)
        # Layout 6: Content slide - side by side, 2-4 rows (slide 7)
        # Layout 7: NCS Singapore ending slide (slide 8)
        
        layout_mapping = {
            "TITLE_SLIDE": 0,           # Use template's title layout
            "AGENDA_SLIDE": 2,          # Use template's agenda layout
            "INTRODUCTION_SLIDE": 3,    # Use template's stand out message layout
            "KEY_INSIGHT_SLIDE": 4,     # Use template's content layouts (4-6)
            "RECOMMENDATIONS_SLIDE": 5, # Use template's content layouts
            "CONCLUSION_SLIDE": 6,      # Use template's content layouts
            "THANK_YOU_SLIDE": 7,       # Use template's NCS ending layout
            "CONTENT_SLIDE": 4,         # Default to first content layout
            "TWO_COLUMN_SLIDE": 4,      # Use content layout (side-by-side design)
            "SUMMARY_SLIDE": 5,         # Use content layout
            "STANDOUT_SLIDE": 3         # Use stand out message layout
        }
        
        layout_index = layout_mapping.get(slide_type, 4)  # Default to content layout
        
        # Fallback if layout doesn't exist in template
        max_layouts = len(prs.slide_layouts)
        if layout_index >= max_layouts:
            # Cycle through available content layouts (4-6) or fallback to layout 1
            if max_layouts > 4:
                layout_index = 4 + (layout_index % 3)  # Rotate between layouts 4,5,6
            else:
                layout_index = min(1, max_layouts - 1)
            
        return layout_index

    def _format_slide_by_type(self, slide, slide_type: str, title: str, content):
        """Apply type-specific formatting to slide"""
        try:
            # Set title
            if slide.shapes.title:
                slide.shapes.title.text = title
                self._apply_title_format_by_type(slide.shapes.title, slide_type)
        except Exception as e:
            print(f"Error setting title: {e}")
        
        try:
            # Add content based on slide type
            if slide_type == "TITLE_SLIDE":
                self._format_title_slide(slide, content)
            elif slide_type == "THANK_YOU_SLIDE":
                self._format_ncs_ending_slide(slide, content)
            elif slide_type == "STANDOUT_SLIDE":
                self._format_standout_slide(slide, content)
            else:
                self._format_content_slide(slide, content)
        except Exception as e:
            print(f"Error formatting slide content for type {slide_type}: {e}")
            # Just leave the slide as-is if formatting fails

    def _format_title_slide(self, slide, content):
        """Format title slide with subtitle"""
        subtitle_placeholder = self._find_content_placeholder(slide)
        if subtitle_placeholder:
            try:
                subtitle_text = content[0] if content else "Professional Business Presentation"
                subtitle_placeholder.text = str(subtitle_text)
                print(f"Set title slide subtitle: {subtitle_text}")
            except Exception as e:
                print(f"Error setting title slide content: {e}")
        else:
            print("No subtitle placeholder found for title slide")

    def _format_ncs_ending_slide(self, slide, content):
        """Format NCS Singapore ending slide with company branding"""
        content_placeholder = self._find_content_placeholder(slide)
        if content_placeholder and content_placeholder.has_text_frame:
            text_frame = content_placeholder.text_frame
            text_frame.clear()
            
            # NCS Singapore specific content
            ncs_content = content if content else [
                "Thank you for your attention",
                "NCS Singapore",
                "Leading Digital Transformation",
                "Questions & Discussion"
            ]
            
            content_list = ncs_content if isinstance(ncs_content, list) else [ncs_content]
            
            for i, item in enumerate(content_list[:4]):
                p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
                p.text = str(item)
                self._apply_content_format(p)

    def _format_standout_slide(self, slide, content):
        """Format stand out message slide"""
        content_placeholder = self._find_content_placeholder(slide)
        if content_placeholder and content_placeholder.has_text_frame:
            text_frame = content_placeholder.text_frame
            text_frame.clear()
            
            # Format as prominent message
            standout_content = content if content else ["Key Message or Insight"]
            content_list = standout_content if isinstance(standout_content, list) else [standout_content]
            
            for i, item in enumerate(content_list[:2]):  # Max 2 items for standout
                p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
                p.text = str(item)
                # Apply larger formatting for standout messages
                for run in p.runs:
                    font = run.font
                    font.name = 'Calibri'
                    font.size = Pt(24)  # Larger than regular content
                    font.bold = True
                    font.color.rgb = self.PRIMARY_COLOR

    def _format_content_slide(self, slide, content):
        """Format regular content slide with bullets"""
        content_placeholder = self._find_content_placeholder(slide)
        if content_placeholder and content:
            try:
                text_frame = content_placeholder.text_frame
                text_frame.clear()
                
                content_list = content if isinstance(content, list) else [content]
                
                for i, item in enumerate(content_list[:6]):  # Max 6 items
                    p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
                    p.text = str(item)
                    self._apply_content_format(p)
                    
                print(f"Successfully added {len(content_list)} content items to slide")
                
            except Exception as e:
                print(f"Error formatting content slide: {e}")
                # Fallback: try to add content as simple text
                try:
                    content_text = '\n'.join(content_list) if isinstance(content, list) else str(content)
                    content_placeholder.text = content_text
                    print("Used fallback text setting")
                except Exception as e2:
                    print(f"Fallback also failed: {e2}")
        else:
            print(f"No content placeholder found or no content provided. Placeholder: {content_placeholder}, Content: {bool(content)}")

    def _apply_title_format_by_type(self, title_shape, slide_type: str):
        """Apply title formatting based on slide type"""
        if title_shape.has_text_frame:
            for paragraph in title_shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    font = run.font
                    font.name = 'Calibri'
                    
                    # Different sizes for different slide types
                    if slide_type in ["TITLE_SLIDE", "THANK_YOU_SLIDE"]:
                        font.size = Pt(36)
                    else:
                        font.size = Pt(32)
                    
                    font.bold = True
                    font.color.rgb = self.PRIMARY_COLOR


    def _find_content_placeholder(self, slide):
        """Find the content placeholder in a slide (handles varying template structures)"""
        print(f"Looking for content placeholder in slide with {len(slide.placeholders)} placeholders")
        
        # First, let's inspect what placeholders we actually have
        for i, placeholder in enumerate(slide.placeholders):
            try:
                has_text_frame = hasattr(placeholder, 'has_text_frame') and placeholder.has_text_frame
                print(f"Placeholder {i}: has_text_frame={has_text_frame}")
            except Exception as e:
                print(f"Placeholder {i}: Error checking - {e}")
        
        # Try to find a working content placeholder
        for i, placeholder in enumerate(slide.placeholders):
            try:
                # Skip title placeholder (usually index 0)
                if i == 0 and slide.shapes.title and placeholder == slide.shapes.title:
                    continue
                    
                # Check if this placeholder can hold text
                if hasattr(placeholder, 'has_text_frame') and placeholder.has_text_frame:
                    # Additional check - try to access the text_frame
                    _ = placeholder.text_frame
                    print(f"Found working content placeholder at index {i}")
                    return placeholder
                    
            except Exception as e:
                print(f"Placeholder {i}: Error accessing - {e}")
                continue
        
        print("No working content placeholder found!")
        return None

    def _apply_content_format(self, paragraph):
        """Apply content formatting"""
        paragraph.level = 0
        for run in paragraph.runs:
            font = run.font
            font.name = 'Calibri'
            font.size = Pt(18)
            font.color.rgb = self.TEXT_COLOR