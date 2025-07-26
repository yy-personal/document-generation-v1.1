
const PptxGenJS = require('pptxgenjs');
const path = require('path');

async function createVisualAnalysis() {
    console.log('Creating visual analysis of corporate template...');
    
    const pres = new PptxGenJS();
    
    // Configure 16:9 presentation
    pres.defineLayout({ name: 'LAYOUT_16x9', width: 10, height: 5.625 });
    pres.layout = 'LAYOUT_16x9';
    
    // Title slide showing what we're analyzing
    const titleSlide = pres.addSlide();
    titleSlide.addText('NCS Corporate Template Analysis', {
        x: 1, y: 2, w: 8, h: 1,
        fontSize: 32, bold: true, align: 'center', color: '00A7E1'
    });
    titleSlide.addText('Visual Layout Analysis for PptxGenJS Integration', {
        x: 1, y: 3, w: 8, h: 0.8,
        fontSize: 18, align: 'center', color: '333333'
    });
    
    // Create test slides for each potential master slide type
    const slideTypes = [
        { name: 'Title Slide', desc: 'Main presentation title with subtitle and date' },
        { name: 'Agenda Slide', desc: 'Agenda or overview with bullet points' },
        { name: 'Content Slide', desc: 'Standard content with title and bullet points' },
        { name: 'Two Column Slide', desc: 'Side-by-side content layout' },
        { name: 'Table Slide', desc: 'Data table or comparison layout' },
        { name: 'Quote/Highlight Slide', desc: 'Featured quote or key message' },
        { name: 'Image Slide', desc: 'Image-focused layout with caption' },
        { name: 'Thank You Slide', desc: 'Closing slide with contact info' }
    ];
    
    slideTypes.forEach((slideType, index) => {
        const slide = pres.addSlide();
        
        // Mock the layout we expect for each type
        slide.addText(slideType.name, {
            x: 1, y: 0.7, w: 8, h: 0.8,
            fontSize: 24, bold: true, color: '00A7E1'
        });
        
        slide.addText(slideType.desc, {
            x: 1, y: 1.5, w: 8, h: 0.5,
            fontSize: 14, color: '666666'
        });
        
        // Add sample content based on slide type
        if (slideType.name.includes('Title')) {
            slide.addText('Sample Presentation Title', {
                x: 1, y: 2.5, w: 8, h: 1,
                fontSize: 28, bold: true, align: 'center'
            });
            slide.addText('Subtitle or Department Name', {
                x: 1, y: 3.5, w: 8, h: 0.5,
                fontSize: 16, align: 'center', color: '666666'
            });
        } else if (slideType.name.includes('Two Column')) {
            slide.addText('Left Column Content:\n• Point 1\n• Point 2\n• Point 3', {
                x: 1, y: 2.5, w: 3.8, h: 2,
                fontSize: 14
            });
            slide.addText('Right Column Content:\n• Point A\n• Point B\n• Point C', {
                x: 5.2, y: 2.5, w: 3.8, h: 2,
                fontSize: 14
            });
        } else if (slideType.name.includes('Table')) {
            const tableData = [
                ['Header 1', 'Header 2', 'Header 3'],
                ['Data 1', 'Data 2', 'Data 3'],
                ['Data 4', 'Data 5', 'Data 6']
            ];
            slide.addTable(tableData, {
                x: 1, y: 2.5, w: 8, h: 2,
                fontSize: 12,
                border: { type: 'solid', color: '00A7E1', pt: 1 }
            });
        } else {
            slide.addText('• Sample bullet point 1\n• Sample bullet point 2\n• Sample bullet point 3\n• Sample bullet point 4', {
                x: 1.5, y: 2.5, w: 7, h: 2,
                fontSize: 14
            });
        }
        
        // Add slide number
        slide.addText(String(index + 2), {
            x: 9.2, y: 5.2, w: 0.5, h: 0.3,
            fontSize: 10, color: '666666', align: 'right'
        });
    });
    
    // Save the analysis file
    const outputPath = path.join(__dirname, '../local_output/template_analysis.pptx');
    await pres.writeFile({ fileName: outputPath });
    
    console.log('Visual analysis saved to:', outputPath);
    console.log('');
    console.log('NEXT STEPS:');
    console.log('1. Open template_analysis.pptx');
    console.log('2. Compare with your corporate template (ncs_ppt_template_2023.pptx)');
    console.log('3. Note the differences in:');
    console.log('   - Logo placement and size');
    console.log('   - Brand colors and lines');
    console.log('   - Text positioning and fonts');
    console.log('   - Background elements');
    console.log('   - Footer/header elements');
    console.log('4. Provide feedback on what needs to match your template');
}

createVisualAnalysis().catch(console.error);
