const fs = require('fs');
const path = require('path');
const AdmZip = require('adm-zip');
const xml2js = require('xml2js');

/**
 * PowerPoint Template Analyzer
 * Extracts master slide layouts, colors, fonts, and positioning from existing .pptx templates
 */
class TemplateAnalyzer {
    constructor(templatePath) {
        this.templatePath = templatePath;
        this.masterSlides = [];
        this.themeData = {};
    }

    async analyze() {
        try {
            console.log(`[TemplateAnalyzer] Analyzing template: ${this.templatePath}`);
            
            // Extract .pptx contents
            const zip = new AdmZip(this.templatePath);
            const entries = zip.getEntries();
            
            // Parse presentation.xml for structure
            await this.parsePresentationStructure(zip);
            
            // Parse theme.xml for colors and fonts
            await this.parseTheme(zip);
            
            // Parse master slides
            await this.parseMasterSlides(zip);
            
            // Generate PptxGenJS code
            this.generateMasterSlideCode();
            
        } catch (error) {
            console.error('[TemplateAnalyzer] Analysis failed:', error);
        }
    }

    async parsePresentationStructure(zip) {
        const presentationEntry = zip.getEntry('ppt/presentation.xml');
        if (!presentationEntry) return;
        
        const xml = presentationEntry.getData().toString('utf8');
        const parser = new xml2js.Parser();
        const result = await parser.parseStringPromise(xml);
        
        console.log('[TemplateAnalyzer] Found presentation structure');
        // Extract master slide references
    }

    async parseTheme(zip) {
        const themeEntry = zip.getEntry('ppt/theme/theme1.xml');
        if (!themeEntry) return;
        
        const xml = themeEntry.getData().toString('utf8');
        const parser = new xml2js.Parser();
        const result = await parser.parseStringPromise(xml);
        
        console.log('[TemplateAnalyzer] Extracted theme colors and fonts');
        this.extractThemeData(result);
    }

    extractThemeData(themeXml) {
        // Extract color scheme
        const colorScheme = themeXml?.['a:theme']?.['a:themeElements']?.[0]?.['a:clrScheme']?.[0];
        if (colorScheme) {
            this.themeData.colors = {
                primary: this.extractColor(colorScheme['a:accent1']),
                secondary: this.extractColor(colorScheme['a:accent2']),
                background: this.extractColor(colorScheme['a:lt1']),
                text: this.extractColor(colorScheme['a:dk1'])
            };
        }

        // Extract font scheme
        const fontScheme = themeXml?.['a:theme']?.['a:themeElements']?.[0]?.['a:fontScheme']?.[0];
        if (fontScheme) {
            this.themeData.fonts = {
                major: this.extractFont(fontScheme['a:majorFont']),
                minor: this.extractFont(fontScheme['a:minorFont'])
            };
        }
    }

    extractColor(colorElement) {
        // Extract RGB or system color values
        if (colorElement?.[0]?.['a:srgbClr']) {
            return colorElement[0]['a:srgbClr'][0]['$'].val;
        }
        return 'FFFFFF'; // Default white
    }

    extractFont(fontElement) {
        // Extract font family name
        if (fontElement?.[0]?.['a:latin']) {
            return fontElement[0]['a:latin'][0]['$'].typeface;
        }
        return 'Calibri'; // Default font
    }

    async parseMasterSlides(zip) {
        // Find all master slide files
        const masterSlideFiles = zip.getEntries().filter(entry => 
            entry.entryName.startsWith('ppt/slideMasters/') && entry.entryName.endsWith('.xml')
        );

        for (const masterFile of masterSlideFiles) {
            await this.parseMasterSlide(masterFile);
        }
    }

    async parseMasterSlide(masterFile) {
        const xml = masterFile.getData().toString('utf8');
        const parser = new xml2js.Parser();
        const result = await parser.parseStringPromise(xml);

        const masterSlide = {
            name: path.basename(masterFile.entryName, '.xml'),
            placeholders: [],
            shapes: [],
            background: null
        };

        // Extract placeholders and shapes
        const spTree = result?.['p:sldMaster']?.['p:cSld']?.[0]?.['p:spTree']?.[0];
        if (spTree && spTree['p:sp']) {
            for (const shape of spTree['p:sp']) {
                this.extractShapeData(shape, masterSlide);
            }
        }

        this.masterSlides.push(masterSlide);
        console.log(`[TemplateAnalyzer] Parsed master slide: ${masterSlide.name}`);
    }

    extractShapeData(shape, masterSlide) {
        // Extract shape positioning and type
        const spPr = shape['p:spPr']?.[0];
        const txBody = shape['p:txBody']?.[0];
        const nvSpPr = shape['p:nvSpPr']?.[0];
        
        if (spPr && spPr['a:xfrm']) {
            const transform = spPr['a:xfrm'][0];
            const position = {
                x: this.emuToInches(transform['a:off']?.[0]?.['$']?.x || 0),
                y: this.emuToInches(transform['a:off']?.[0]?.['$']?.y || 0),
                w: this.emuToInches(transform['a:ext']?.[0]?.['$']?.cx || 0),
                h: this.emuToInches(transform['a:ext']?.[0]?.['$']?.cy || 0)
            };

            // Get shape name for identification
            const shapeName = nvSpPr?.['p:cNvPr']?.[0]?.['$']?.name || 'Unknown';
            
            // Extract text content if available
            let textContent = '';
            if (txBody && txBody['a:p']) {
                textContent = this.extractTextContent(txBody['a:p']);
            }

            // Determine if it's a placeholder or shape
            const placeholder = nvSpPr?.['p:nvPr']?.[0]?.['p:ph'];
            if (placeholder) {
                const placeholderType = placeholder[0]['$']?.type || 'body';
                const placeholderIdx = placeholder[0]['$']?.idx || '';
                masterSlide.placeholders.push({
                    name: shapeName,
                    type: placeholderType,
                    idx: placeholderIdx,
                    text: textContent,
                    ...position
                });
            } else {
                // Determine shape type
                const shapeType = this.determineShapeType(spPr, txBody, shapeName);
                masterSlide.shapes.push({
                    name: shapeName,
                    type: shapeType,
                    text: textContent,
                    fillColor: this.extractFillColor(spPr),
                    lineColor: this.extractLineColor(spPr),
                    fontSize: this.extractFontSize(txBody),
                    fontColor: this.extractFontColor(txBody),
                    ...position
                });
            }
        }
    }

    extractTextContent(paragraphs) {
        let content = '';
        for (const para of paragraphs) {
            if (para['a:r']) {
                for (const run of para['a:r']) {
                    if (run['a:t'] && run['a:t'][0]) {
                        content += run['a:t'][0];
                    }
                }
            }
            content += ' ';
        }
        return content.trim();
    }

    determineShapeType(spPr, txBody, shapeName) {
        // Check for specific shape types
        if (spPr['a:custGeom'] || spPr['a:prstGeom']) {
            const geom = spPr['a:prstGeom']?.[0]?.['$']?.prst;
            if (geom) {
                if (geom === 'rect') return 'rectangle';
                if (geom === 'ellipse') return 'circle';
                if (geom === 'line') return 'line';
                return geom;
            }
        }
        
        // Check if it's a text box
        if (txBody) return 'textbox';
        
        // Check shape name for clues
        const name = shapeName.toLowerCase();
        if (name.includes('logo')) return 'logo';
        if (name.includes('line')) return 'line';
        if (name.includes('image') || name.includes('picture')) return 'image';
        
        return 'shape';
    }

    extractFillColor(spPr) {
        const solidFill = spPr?.['a:solidFill']?.[0];
        if (solidFill) {
            return this.extractColorFromFill(solidFill);
        }
        return null;
    }

    extractLineColor(spPr) {
        const ln = spPr?.['a:ln']?.[0];
        if (ln && ln['a:solidFill']) {
            return this.extractColorFromFill(ln['a:solidFill'][0]);
        }
        return null;
    }

    extractColorFromFill(fillElement) {
        if (fillElement['a:srgbClr']) {
            return fillElement['a:srgbClr'][0]['$'].val;
        }
        if (fillElement['a:schemeClr']) {
            return 'THEME_' + fillElement['a:schemeClr'][0]['$'].val;
        }
        return null;
    }

    extractFontSize(txBody) {
        if (txBody?.['a:p']?.[0]?.['a:r']?.[0]?.['a:rPr']?.[0]?.['$']?.sz) {
            return Math.round(parseInt(txBody['a:p'][0]['a:r'][0]['a:rPr'][0]['$'].sz) / 100);
        }
        return null;
    }

    extractFontColor(txBody) {
        const rPr = txBody?.['a:p']?.[0]?.['a:r']?.[0]?.['a:rPr']?.[0];
        if (rPr?.['a:solidFill']) {
            return this.extractColorFromFill(rPr['a:solidFill'][0]);
        }
        return null;
    }

    emuToInches(emu) {
        // Convert EMU (English Metric Units) to inches
        return Math.round((parseInt(emu) / 914400) * 100) / 100;
    }

    generateMasterSlideCode() {
        console.log('\n[TemplateAnalyzer] Detailed Template Analysis:');
        console.log('==============================================\n');

        // First, print detailed analysis
        for (const masterSlide of this.masterSlides) {
            console.log(`\n--- ${masterSlide.name.toUpperCase()} ANALYSIS ---`);
            
            console.log(`Placeholders (${masterSlide.placeholders.length}):`);
            for (const placeholder of masterSlide.placeholders) {
                console.log(`  • ${placeholder.name}: ${placeholder.type} (${placeholder.x}", ${placeholder.y}", ${placeholder.w}"×${placeholder.h}")`);
                if (placeholder.text) console.log(`    Text: "${placeholder.text}"`);
            }
            
            console.log(`Shapes (${masterSlide.shapes.length}):`);
            for (const shape of masterSlide.shapes) {
                console.log(`  • ${shape.name}: ${shape.type} (${shape.x}", ${shape.y}", ${shape.w}"×${shape.h}")`);
                if (shape.text) console.log(`    Text: "${shape.text}"`);
                if (shape.fillColor) console.log(`    Fill: #${shape.fillColor}`);
                if (shape.lineColor) console.log(`    Line: #${shape.lineColor}`);
                if (shape.fontSize) console.log(`    Font: ${shape.fontSize}pt`);
            }
        }

        console.log('\n\n[TemplateAnalyzer] Generated PptxGenJS Master Slide Code:');
        console.log('=========================================================\n');

        for (const masterSlide of this.masterSlides) {
            console.log(`// ${masterSlide.name.toUpperCase()}_MASTER`);
            console.log(`// Placeholders: ${masterSlide.placeholders.length}, Shapes: ${masterSlide.shapes.length}`);
            console.log('pres.defineSlideMaster({');
            console.log(`    title: "${masterSlide.name.toUpperCase()}_MASTER",`);
            console.log('    background: { color: "FFFFFF" },');
            console.log('    margin: [0.75, 0.5, 0.75, 0.5],');
            console.log('    objects: [');

            // Generate shapes with enhanced details
            for (const shape of masterSlide.shapes) {
                if (shape.type === 'textbox' || shape.text) {
                    console.log('        {');
                    console.log('            text: {');
                    console.log(`                text: "${shape.text || shape.name}",`);
                    console.log('                options: {');
                    console.log(`                    x: ${shape.x}, y: ${shape.y}, w: ${shape.w}, h: ${shape.h},`);
                    if (shape.fontSize) console.log(`                    fontSize: ${shape.fontSize},`);
                    if (shape.fontColor) console.log(`                    color: "${shape.fontColor.replace('THEME_', '')}",`);
                    console.log('                }');
                    console.log('            }');
                    console.log('        },');
                } else if (shape.type === 'rectangle' || shape.type === 'line') {
                    console.log('        {');
                    console.log(`            ${shape.type === 'line' ? 'line' : 'rect'}: {`);
                    console.log(`                x: ${shape.x}, y: ${shape.y}, w: ${shape.w}, h: ${shape.h},`);
                    if (shape.fillColor) console.log(`                fill: { color: "${shape.fillColor}" },`);
                    if (shape.lineColor) console.log(`                line: { color: "${shape.lineColor}", width: 1 }`);
                    console.log('            }');
                    console.log('        },');
                } else {
                    console.log(`        // ${shape.name}: ${shape.type} at (${shape.x}", ${shape.y}", ${shape.w}"×${shape.h}")`);
                }
            }

            // Generate placeholders with enhanced details
            for (const placeholder of masterSlide.placeholders) {
                console.log('        {');
                console.log('            placeholder: {');
                console.log('                options: {');
                console.log(`                    name: "${placeholder.type}",`);
                console.log(`                    type: "${placeholder.type}",`);
                console.log(`                    x: ${placeholder.x}, y: ${placeholder.y}, w: ${placeholder.w}, h: ${placeholder.h}`);
                console.log('                }');
                console.log('            }');
                console.log('        },');
            }

            console.log('    ],');
            console.log('    slideNumber: { x: 9.2, y: 5.2, color: "666666", fontSize: 10 }');
            console.log('});\n');
        }

        // Generate theme colors with actual extracted values
        console.log('// ============ EXTRACTED THEME DATA ============');
        console.log(`// Primary Color: #${this.themeData.colors?.primary || 'UNKNOWN'}`);
        console.log(`// Secondary Color: #${this.themeData.colors?.secondary || 'UNKNOWN'}`);
        console.log(`// Background Color: #${this.themeData.colors?.background || 'UNKNOWN'}`);
        console.log(`// Text Color: #${this.themeData.colors?.text || 'UNKNOWN'}`);
        console.log(`// Major Font (Headings): ${this.themeData.fonts?.major || 'UNKNOWN'}`);
        console.log(`// Minor Font (Body): ${this.themeData.fonts?.minor || 'UNKNOWN'}`);
        console.log('// =============================================\n');

        // Generate usage recommendations
        this.generateUsageRecommendations();
    }

    generateUsageRecommendations() {
        console.log('// ============ USAGE RECOMMENDATIONS ============');
        console.log('// Based on your template analysis:');
        
        const titleSlides = this.masterSlides.filter(slide => 
            slide.placeholders.some(p => p.type === 'title' || p.type === 'ctrTitle')
        );
        const contentSlides = this.masterSlides.filter(slide => 
            slide.placeholders.some(p => p.type === 'body' || p.type === 'obj')
        );
        
        console.log(`// - ${titleSlides.length} slide(s) appear to be title layouts`);
        console.log(`// - ${contentSlides.length} slide(s) appear to be content layouts`);
        console.log(`// - ${this.masterSlides.length - titleSlides.length - contentSlides.length} slide(s) appear to be specialty layouts`);
        
        console.log('//');
        console.log('// Recommended mapping:');
        console.log('// const masterSlideMap = {');
        
        if (titleSlides.length > 0) {
            console.log(`//     "TITLE_SLIDE": "${titleSlides[0].name.toUpperCase()}_MASTER",`);
        }
        if (contentSlides.length > 0) {
            console.log(`//     "CONTENT_SLIDE": "${contentSlides[0].name.toUpperCase()}_MASTER",`);
            console.log(`//     "AGENDA_SLIDE": "${contentSlides[0].name.toUpperCase()}_MASTER",`);
        }
        
        console.log('// };');
        console.log('// ===============================================\n');
    }
}

module.exports = { TemplateAnalyzer };

// Usage example:
if (require.main === module) {
    const templatePath = path.join(__dirname, '../template/ncs_ppt_template_2023.pptx');
    const analyzer = new TemplateAnalyzer(templatePath);
    analyzer.analyze();
}