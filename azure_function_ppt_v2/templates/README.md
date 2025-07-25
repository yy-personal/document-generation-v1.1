# PowerPoint Templates for V2 System

This directory contains PowerPoint templates for the V2 Pandoc-based generation system.

## Template Usage

The V2 system uses Pandoc's `--reference-doc` feature to apply your company template to generated presentations.

### Adding Your Company Template

1. Place your company PowerPoint template in this directory
2. Name it `company_template.pptx` (or update the path in `config.py`)
3. Ensure the template has the following slide layouts:
   - **Layout 0**: Title slide
   - **Layout 1**: Content slide (with title and content placeholders)
   - **Layout 2**: Section header or closing slide

### Template Requirements

Your template should include:
- ✅ Company branding (logos, colors, fonts)
- ✅ Master slide designs
- ✅ Standard slide layouts
- ✅ Table formatting styles
- ✅ Proper 16:9 or 4:3 aspect ratio

### How Pandoc Uses Templates

Pandoc will:
- Preserve your template's visual design
- Apply your fonts, colors, and branding
- Use your slide layouts for different content types
- Maintain consistent formatting across all slides

### Template Validation

The system will automatically:
- Check if the template file exists
- Fall back to Pandoc's default template if your template is unavailable
- Log template usage in the processing information

### Supported Template Features

- ✅ **Custom fonts**: Maintained in generated slides
- ✅ **Color schemes**: Applied to all content
- ✅ **Logos and branding**: Preserved from master slides
- ✅ **Table styles**: Applied to markdown tables
- ✅ **Bullet point formatting**: Uses template's bullet styles
- ✅ **Background designs**: Maintained across slides

### Template Best Practices

1. **Keep it simple**: Complex animations or transitions may not transfer
2. **Test layouts**: Ensure title and content placeholders work well
3. **Standard sizes**: Use common slide dimensions (16:9 recommended)
4. **Clear hierarchy**: Define distinct styles for headers, content, tables
5. **Brand consistency**: Include all required company branding elements

### Example Template Structure

A good company template should have:
- Title slide with company logo and branding
- Standard content slide with title and bullet point areas
- Table-friendly layout with appropriate spacing
- Consistent color scheme throughout
- Professional typography choices

Place your `company_template.pptx` file in this directory to enable template-based generation.