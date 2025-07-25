# PowerPoint Templates

This folder contains PowerPoint template files that can be used as the base for generating presentations with custom branding and layouts.

## How Templates Work in python-pptx

Python-pptx doesn't use traditional PowerPoint template files (.potx). Instead, it uses regular PowerPoint files (.pptx) with slides removed as "templates."

### Template Structure

A python-pptx template is a regular .pptx file that contains:
- ✅ **Slide Master** - Defines overall design theme
- ✅ **Slide Layouts** - Different layout types (title, content, etc.)
- ✅ **Theme Colors** - Company color palette
- ✅ **Fonts** - Typography settings
- ✅ **Background** - Master slide background
- ❌ **Slides** - All slides removed (that's what makes it a template)

## Creating a Custom Template

### Method 1: PowerPoint Design
1. Open PowerPoint
2. Design your presentation (colors, fonts, layouts, logo placement)
3. Delete all content slides (keep only the master/layouts)
4. Save as `template_name.pptx` in this folder

### Method 2: Start from Existing
1. Take any well-designed PowerPoint presentation
2. Delete all slides
3. Customize the slide master and layouts
4. Save in this folder

## Using Templates in Code

### Basic Template Usage
```python
from pptx import Presentation

# Load your custom template
prs = Presentation('templates/company_template.pptx')

# Now add slides using the template's layouts
slide_layout = prs.slide_layouts[0]  # Title slide layout
slide = prs.slides.add_slide(slide_layout)

# The slide will inherit the template's design
slide.shapes.title.text = "My Presentation"
```

### Available Slide Layouts
Most templates include these standard layouts:
- `slide_layouts[0]` - Title Slide
- `slide_layouts[1]` - Title and Content
- `slide_layouts[2]` - Section Header
- `slide_layouts[3]` - Two Content
- `slide_layouts[4]` - Comparison
- `slide_layouts[5]` - Title Only
- `slide_layouts[6]` - Blank
- `slide_layouts[7]` - Content with Caption
- `slide_layouts[8]` - Picture with Caption

### Accessing Layouts by Name
```python
# You can also find layouts by name
for layout in prs.slide_layouts:
    print(f"Layout {layout.name}: Index {prs.slide_layouts.index(layout)}")
```

## Template Files

### Default Template
- **File**: `default_template.pptx` (when available)
- **Description**: Clean, professional template with minimal branding
- **Use Case**: General business presentations

### Company Template  
- **File**: `company_template.pptx` (to be added)
- **Description**: Official company template with branding
- **Use Case**: Client presentations, reports, proposals

### Custom Templates
Add your own .pptx template files here and document them:

```
templates/
├── README.md                    # This file
├── default_template.pptx        # Clean professional template
├── company_template.pptx        # Official company branding
├── technical_template.pptx      # For technical documentation
└── executive_template.pptx      # For executive summaries
```

## Integration with PowerPoint Builder

### Current Integration (TODO)
The `PowerPointBuilderAgent` currently creates presentations from scratch. To use templates:

1. **Update agent to load template**:
   ```python
   # Instead of: prs = Presentation()
   template_path = "templates/company_template.pptx"
   prs = Presentation(template_path)
   ```

2. **Configure template selection**:
   - Add template selection to config.py
   - Allow different templates for different presentation types
   - Fall back to default template if custom template fails

### Template Configuration Example
```python
# In config.py
TEMPLATE_CONFIG = {
    "default_template": "templates/default_template.pptx",
    "company_template": "templates/company_template.pptx",
    "fallback_template": None  # Use python-pptx default
}
```

## Best Practices

### Template Design
- ✅ Use consistent colors throughout
- ✅ Set up proper font hierarchy
- ✅ Include logo placement in master
- ✅ Design layouts for different content types
- ✅ Test layouts with varying content lengths

### File Management
- ✅ Use descriptive filenames
- ✅ Keep file sizes reasonable (<5MB)
- ✅ Test templates with python-pptx before deploying
- ✅ Version control important templates
- ✅ Document any special layout requirements

### Code Integration
- ✅ Handle missing template files gracefully
- ✅ Validate template has required layouts
- ✅ Fall back to default if template fails
- ✅ Log template usage for debugging

## Troubleshooting

### Common Issues

**Template not found**:
```python
import os
template_path = "templates/my_template.pptx"
if not os.path.exists(template_path):
    print(f"Template not found: {template_path}")
    # Fall back to default
    prs = Presentation()
```

**Layout not available**:
```python
try:
    layout = prs.slide_layouts[1]  # Title and Content
except IndexError:
    # Fall back to first available layout
    layout = prs.slide_layouts[0]
```

**Corrupted template**:
```python
try:
    prs = Presentation(template_path)
except Exception as e:
    print(f"Failed to load template: {e}")
    # Use default template
    prs = Presentation()
```

## Advanced Features

### Custom Colors
Templates can define custom color schemes that python-pptx will use:
```python
# Access theme colors
theme = prs.slide_master.theme
color_scheme = theme.color_scheme
```

### Custom Fonts
Templates can specify font themes:
```python
# Access font scheme
font_scheme = prs.slide_master.theme.font_scheme
```

### Master Slide Customization
For advanced template customization, you can modify the slide master:
```python
slide_master = prs.slide_master
# Modify master properties
```

## Resources

- [python-pptx Documentation](https://python-pptx.readthedocs.io/)
- [PowerPoint Slide Master Guide](https://support.microsoft.com/en-us/office/what-is-a-slide-master-b9abb2a0-7aef-4257-a6e1-329c634b8a8c)
- [Corporate Template Best Practices](https://support.microsoft.com/en-us/office/create-and-save-a-powerpoint-template-ee4429ad-2a74-4100-82f7-50f8169c8aca)

---

**Note**: Place your .pptx template files in this folder and update the PowerPointBuilderAgent to use them for consistent, branded presentations.