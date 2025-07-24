"""
PowerPoint Builder Agent - With template support
"""
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent
from config import get_template_path
import json
import io
import os
import re

class PowerPointBuilderAgent(BaseAgent):
    """Builds PowerPoint files with 16:9 aspect ratio and simple 2-color theme"""

    # Simple color theme
    PRIMARY_COLOR = RGBColor(88, 77, 193)    # #584dc1 (purple)
    ACCENT_COLOR = RGBColor(209, 185, 91)    # #d1b95b (gold)
    TEXT_COLOR = RGBColor(51, 51, 51)        # Dark gray

    agent_description = "PowerPoint file generation with 16:9 aspect ratio and template support"
    agent_use_cases = [
        "PowerPoint file creation from slide content",
        "16:9 widescreen presentation generation", 
        "Template-based presentation generation",
        "Custom branding and layouts", 
        "Professional formatting"
    ]

    def __init__(self, **kwargs):
        super().__init__()
    
    def _set_16_9_aspect_ratio(self, prs: Presentation):
        """Set presentation to 16:9 aspect ratio"""
        prs.slide_width = Inches(16)
        prs.slide_height = Inches(9)

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
            
            # Always set to 16:9 aspect ratio
            self._set_16_9_aspect_ratio(prs)
            
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
                    
                    # Always set to 16:9 aspect ratio
                    self._set_16_9_aspect_ratio(prs)
                    
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
                self._apply_smart_text_formatting(subtitle_placeholder, str(subtitle_text))
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
                self._apply_smart_text_formatting(content_placeholder, ending_text)
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
                self._apply_smart_text_formatting(content_placeholder, standout_text)
                print(f"Set standout slide content")
                
            except Exception as e:
                print(f"Error setting standout content: {e}")
        else:
            print("No content placeholder found for standout slide")

    def _format_any_slide_content(self, slide, content, slide_type):
        """SIMPLIFIED: Format any slide content with table detection and smart formatting"""
        content_placeholder = self._find_content_placeholder(slide)
        
        if content_placeholder and content:
            try:
                content_list = content if isinstance(content, list) else [content]
                
                # Check if content should be a table
                table_info = self._detect_table_content(content_list)
                
                if table_info["is_table"]:
                    # Remove the content placeholder and create a table instead
                    try:
                        slide.shapes._spTree.remove(content_placeholder._element)
                        print(f"Removed text placeholder to create table")
                    except:
                        print("Could not remove placeholder, creating table anyway")
                    
                    # Create table
                    if self._create_table_slide(slide, table_info):
                        print(f"Successfully created table for {slide_type}")
                        return
                    else:
                        print(f"Table creation failed, falling back to text for {slide_type}")
                
                # Standard text formatting (not a table)
                if len(content_list) == 1:
                    # Single item - could be paragraph or single point
                    content_placeholder.text = str(content_list[0])
                else:
                    # Multiple items - DON'T add manual bullets, let PowerPoint's template handle it
                    content_text = '\n'.join([str(item) for item in content_list[:6]])
                    content_placeholder.text = content_text
                
                # Apply smart text formatting with auto-fit
                self._apply_smart_text_formatting(content_placeholder, content_text if len(content_list) > 1 else str(content_list[0]))
                    
                print(f"Successfully set content for {slide_type}: {len(content_list)} items")
                
            except Exception as e:
                print(f"Error setting {slide_type} content: {e}")
                # Ultimate fallback
                try:
                    simple_text = str(content[0]) if isinstance(content, list) and content else str(content)
                    content_placeholder.text = simple_text
                    self._apply_smart_text_formatting(content_placeholder, simple_text)
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

    def _apply_smart_text_formatting(self, content_placeholder, content_text: str):
        """
        Apply smart text formatting with auto-fit and word wrap
        
        HOW TO ADJUST TEXT POSITIONING IN THE FUTURE:
        
        1. MARGINS (text_frame.margin_*):
           - margin_left/right: Controls horizontal spacing from slide edges
           - margin_top/bottom: Controls vertical spacing from slide edges
           - Use Inches(value) - typical range: 0.1 to 0.8 inches
        
        2. VERTICAL ALIGNMENT (text_frame.vertical_anchor):
           - MSO_ANCHOR.TOP: Text starts at top of text box
           - MSO_ANCHOR.MIDDLE: Text centered vertically in text box  
           - MSO_ANCHOR.BOTTOM: Text aligned to bottom of text box
        
        3. HORIZONTAL ALIGNMENT (paragraph.alignment):
           - PP_ALIGN.LEFT: Left-aligned (best for bullets)
           - PP_ALIGN.CENTER: Center-aligned
           - PP_ALIGN.RIGHT: Right-aligned
           - PP_ALIGN.JUSTIFY: Justified text
        
        4. FONT SIZE: Adjust base_font_size values below for different text lengths
        
        5. AUTO-FIT BEHAVIOR (text_frame.auto_size):
           - MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE: Shrinks text to fit
           - MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT: Expands text box
           - MSO_AUTO_SIZE.NONE: No auto-sizing
        """
        if not content_placeholder.has_text_frame:
            return
            
        try:
            text_frame = content_placeholder.text_frame
            
            # Enable word wrap for better text flow
            text_frame.word_wrap = True
            
            # Configure auto-sizing behavior
            from pptx.enum.text import MSO_AUTO_SIZE, MSO_ANCHOR
            text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
            
            # Set vertical text alignment - center vertically within the text box
            text_frame.vertical_anchor = MSO_ANCHOR.TOP  # Options: TOP, MIDDLE, BOTTOM
            
            # Set better margins for professional layout - move content away from edges
            text_frame.margin_left = Inches(0.3)    # More space from left edge
            text_frame.margin_right = Inches(0.3)   # More space from right edge  
            text_frame.margin_top = Inches(0.4)     # Move content down from top
            text_frame.margin_bottom = Inches(0.3)  # Space at bottom
            
            # Set a good starting font size - let auto-fit adjust as needed
            char_count = len(content_text.strip())
            if char_count <= 200:
                base_font_size = 24  # Start larger for short content
            elif char_count <= 400:
                base_font_size = 22  # Medium starting size
            else:
                base_font_size = 20  # Smaller starting size for long content
            
            # Apply base font size and alignment to all content
            from pptx.enum.text import PP_ALIGN
            for paragraph in text_frame.paragraphs:
                # Set paragraph alignment (left is usually best for bullet points)
                paragraph.alignment = PP_ALIGN.LEFT
                
                for run in paragraph.runs:
                    run.font.size = Pt(base_font_size)
                    run.font.name = 'Calibri'
                        
            print(f"Applied auto-fit formatting with {base_font_size}pt base size for {char_count} characters")
            
        except Exception as e:
            print(f"Error applying smart text formatting: {e}")

    def _detect_table_content(self, content_list: list) -> dict:
        """Detect if content should be presented as a table"""
        if not content_list or len(content_list) < 2:
            return {"is_table": False}
        
        # Look for patterns that suggest tabular data
        table_patterns = [
            r'\w+\s*:\s*\$[\d,]+',      # Item: $amount
            r'\w+\s*:\s*\d+\.?\d*%',    # Item: percentage  
            r'\w+\s*:\s*\d+',           # Item: number
            r'[A-Z][^:]*:\s*.+',        # Category: description
        ]
        
        matches = 0
        for item in content_list[:6]:  # Check first 6 items
            item_str = str(item)
            for pattern in table_patterns:
                if re.search(pattern, item_str):
                    matches += 1
                    break
        
        # If 50%+ of items match table patterns, create a table
        if matches >= len(content_list) * 0.5 and matches >= 2:
            table_data = self._parse_table_data(content_list)
            return {
                "is_table": True,
                "rows": len(table_data),
                "cols": 2,  # Most common: label/value pairs
                "data": table_data
            }
        
        return {"is_table": False}

    def _parse_table_data(self, content_list: list) -> list:
        """Parse content into table rows"""
        table_data = []
        
        for item in content_list:
            item_str = str(item).strip()
            
            # Split on colon for key:value pairs
            if ':' in item_str:
                parts = item_str.split(':', 1)
                if len(parts) == 2:
                    table_data.append([parts[0].strip(), parts[1].strip()])
                else:
                    table_data.append([item_str, ""])
            else:
                # If no colon, put entire text in first column
                table_data.append([item_str, ""])
        
        return table_data[:8]  # Limit to 8 rows for readability

    def _create_table_slide(self, slide, table_info: dict):
        """Create a table on the slide"""
        try:
            rows = table_info["rows"]
            cols = table_info["cols"] 
            data = table_info["data"]
            
            # Position table in the content area
            left = Inches(1)
            top = Inches(2) 
            width = Inches(14)  # 16:9 slide width minus margins
            height = Inches(5)
            
            # Add table shape
            table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
            table = table_shape.table
            
            # Set column widths for better layout
            table.columns[0].width = Inches(6)   # First column (labels)
            table.columns[1].width = Inches(8)   # Second column (values)
            
            # Fill table with data
            for row_idx, row_data in enumerate(data):
                if row_idx >= rows:
                    break
                    
                for col_idx, cell_value in enumerate(row_data):
                    if col_idx >= cols:
                        break
                        
                    cell = table.cell(row_idx, col_idx)
                    cell.text = str(cell_value)
                    
                    # Format cell text
                    paragraph = cell.text_frame.paragraphs[0]
                    paragraph.alignment = PP_ALIGN.LEFT
                    
                    for run in paragraph.runs:
                        run.font.name = 'Calibri'
                        run.font.size = Pt(18)
                        
                        # Make first column bold (labels)
                        if col_idx == 0:
                            run.font.bold = True
            
            print(f"Created table with {rows} rows and {cols} columns")
            return True
            
        except Exception as e:
            print(f"Error creating table: {e}")
            return False

    def _apply_content_format(self, paragraph):
        """Apply minimal content formatting - preserve template fonts"""
        # Only set the bullet level, don't override template fonts/colors
        paragraph.level = 0
        # Remove all font overrides to preserve template formatting
        # Template should handle font, size, and color