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
            
            # Use template if available (controlled by config.py)
            template_path = get_template_path("default")
            if template_path:
                print(f"Using template: {template_path}")
                prs = Presentation(template_path)
            else:
                print("Using python-pptx default template (no custom design)")
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
        """Get appropriate layout index - SIMPLE 3-LAYOUT SYSTEM"""
        max_layouts = len(prs.slide_layouts)
        print(f"Template has {max_layouts} layouts available")
        
        # SIMPLE 3-LAYOUT SYSTEM:
        # Layout 0: Opening slide (title/intro) - used once
        # Layout 1: Content slide (standard) - used for most slides
        # Layout 2: Ending slide (thank you/NCS) - used once
        
        if slide_type == "TITLE_SLIDE":
            layout_index = 0  # Opening slide
        elif slide_type == "THANK_YOU_SLIDE":
            layout_index = 2  # Ending slide
        else:
            layout_index = 1  # Content slide for everything else
        
        # Fallback if layout doesn't exist
        if layout_index >= max_layouts:
            print(f"Warning: Layout {layout_index} not available, using layout 0")
            layout_index = 0
            
        print(f"Using layout {layout_index} for slide type {slide_type}")
        return layout_index

    def _format_slide_by_type(self, slide, slide_type: str, title: str, content):
        """Apply type-specific formatting to slide"""
        try:
            # Set title - DON'T apply custom formatting, use template's formatting
            if slide.shapes.title:
                print(f"Found title shape, setting to: {title}")
                slide.shapes.title.text = title
                print(f"Successfully set slide title: {title}")
                # Remove custom formatting to preserve template fonts
                # self._apply_title_format_by_type(slide.shapes.title, slide_type)  # REMOVED
            else:
                print(f"No title shape found for slide with title: {title}")
        except Exception as e:
            print(f"Error setting title '{title}': {e}")
        
        try:
            # SIMPLIFIED: Use the same content formatting for all slide types
            # Only the layout (0, 1, or 2) determines the visual design
            self._format_any_slide_content(slide, content, slide_type)
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
        """Format NCS Singapore ending slide - preserve template design"""
        content_placeholder = self._find_content_placeholder(slide)
        if content_placeholder:
            try:
                # NCS Singapore specific content
                ncs_content = content if content else [
                    "Thank you for your attention",
                    "NCS Singapore", 
                    "Leading Digital Transformation",
                    "Questions & Discussion"
                ]
                
                content_list = ncs_content if isinstance(ncs_content, list) else [ncs_content]
                
                # Simple text assignment - preserve template formatting
                ending_text = '\n'.join(content_list[:4])
                content_placeholder.text = ending_text
                print(f"Set NCS ending slide content")
                
            except Exception as e:
                print(f"Error setting NCS ending content: {e}")
        else:
            print("No content placeholder found for NCS ending slide")

    def _format_standout_slide(self, slide, content):
        """Format stand out message slide - preserve template design"""
        content_placeholder = self._find_content_placeholder(slide)
        if content_placeholder:
            try:
                # Format as prominent message
                standout_content = content if content else ["Key Message or Insight"]
                content_list = standout_content if isinstance(standout_content, list) else [standout_content]
                
                # Simple text assignment - let template handle the formatting
                standout_text = '\n'.join(content_list[:2])  # Max 2 items for standout
                content_placeholder.text = standout_text
                print(f"Set standout slide content")
                
            except Exception as e:
                print(f"Error setting standout content: {e}")
        else:
            print("No content placeholder found for standout slide")

    def _format_any_slide_content(self, slide, content, slide_type):
        """SIMPLIFIED: Format any slide content - let template handle design"""
        content_placeholder = self._find_content_placeholder(slide)
        
        if content_placeholder and content:
            try:
                content_list = content if isinstance(content, list) else [content]
                
                # Simple text assignment - preserve ALL template formatting
                if len(content_list) == 1:
                    # Single item - set as plain text
                    content_placeholder.text = str(content_list[0])
                else:
                    # Multiple items - join with bullet points
                    bullet_content = '\n'.join([f"• {item}" for item in content_list[:6]])
                    content_placeholder.text = bullet_content
                    
                print(f"Successfully set content for {slide_type}: {len(content_list)} items")
                
            except Exception as e:
                print(f"Error setting {slide_type} content: {e}")
                # Ultimate fallback
                try:
                    simple_text = str(content[0]) if isinstance(content, list) and content else str(content)
                    content_placeholder.text = simple_text
                    print("Used simple text fallback")
                except Exception as e2:
                    print(f"All methods failed for {slide_type}: {e2}")
        else:
            print(f"No content placeholder or content for {slide_type}. Placeholder: {bool(content_placeholder)}, Content: {bool(content)}")

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
        """Find the content placeholder in a slide (NOT the title placeholder)"""
        print(f"Looking for content placeholder in slide with {len(slide.placeholders)} placeholders")
        
        # First, let's inspect what placeholders we actually have
        for i, placeholder in enumerate(slide.placeholders):
            try:
                has_text_frame = hasattr(placeholder, 'has_text_frame') and placeholder.has_text_frame
                is_title = placeholder == slide.shapes.title
                print(f"Placeholder {i}: has_text_frame={has_text_frame}, is_title={is_title}")
            except Exception as e:
                print(f"Placeholder {i}: Error checking - {e}")
        
        # Try to find a content placeholder (NOT the title)
        for i, placeholder in enumerate(slide.placeholders):
            try:
                # CRITICALLY IMPORTANT: Skip the title placeholder completely
                if slide.shapes.title and placeholder == slide.shapes.title:
                    print(f"Skipping placeholder {i} (it's the title placeholder)")
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
        """Apply minimal content formatting - preserve template fonts"""
        # Only set the bullet level, don't override template fonts/colors
        paragraph.level = 0
        # Remove all font overrides to preserve template formatting
        # Template should handle font, size, and color