/**
 * Slide Builder Utility - Advanced PptxGenJS slide creation
 */
const { BRAND_COLORS, TEMPLATE_CONFIG, getSlideLayoutByType } = require('../config');

class SlideBuilder {
    constructor() {
        this.template = TEMPLATE_CONFIG.corporateTemplate;
    }

    /**
     * Apply corporate template to presentation
     */
    applyCorperateTemplate(pres) {
        // Set presentation properties
        pres.author = 'NCS Singapore';
        pres.company = 'NCS Singapore';
        pres.subject = 'Business Presentation';
        pres.title = 'Professional Business Presentation';
        
        // Define slide masters for consistent branding
        this.defineSlideMasters(pres);
    }

    /**
     * Define slide masters for corporate branding
     */
    defineSlideMasters(pres) {
        // Title Slide Master
        pres.defineSlideMaster({
            title: 'TITLE_MASTER',
            background: { color: BRAND_COLORS.background },
            objects: [
                {
                    placeholder: {
                        options: { name: 'title', type: 'title', x: 1, y: 2, w: 14, h: 2 },
                        text: { 
                            color: BRAND_COLORS.primary, 
                            fontSize: 36, 
                            fontFace: 'Calibri',
                            bold: true,
                            align: 'center'
                        }
                    }
                },
                {
                    placeholder: {
                        options: { name: 'subtitle', type: 'body', x: 1, y: 4.5, w: 14, h: 1.5 },
                        text: { 
                            color: BRAND_COLORS.text, 
                            fontSize: 18, 
                            fontFace: 'Calibri',
                            align: 'center'
                        }
                    }
                }
            ]
        });

        // Content Slide Master
        pres.defineSlideMaster({
            title: 'CONTENT_MASTER',
            background: { color: BRAND_COLORS.background },
            objects: [
                {
                    placeholder: {
                        options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 15, h: 1.2 },
                        text: { 
                            color: BRAND_COLORS.primary, 
                            fontSize: 28, 
                            fontFace: 'Calibri',
                            bold: true
                        }
                    }
                },
                {
                    placeholder: {
                        options: { name: 'content', type: 'body', x: 0.8, y: 1.8, w: 14.4, h: 6.5 },
                        text: { 
                            color: BRAND_COLORS.text, 
                            fontSize: 18, 
                            fontFace: 'Calibri',
                            bullet: { type: 'bullet' }
                        }
                    }
                }
            ]
        });
    }

    /**
     * Create a slide based on type and content
     */
    async createSlide(pres, slideData, isFirst = false, isLast = false) {
        const slideType = slideData.type || 'CONTENT_SLIDE';
        
        switch (slideType) {
            case 'TITLE_SLIDE':
                return this.createTitleSlide(pres, slideData);
            case 'AGENDA_SLIDE':
                return this.createAgendaSlide(pres, slideData);
            case 'CONTENT_SLIDE':
                return this.createContentSlide(pres, slideData);
            case 'TABLE_SLIDE':
                return this.createTableSlide(pres, slideData);
            case 'CHART_SLIDE':
                return this.createChartSlide(pres, slideData);
            case 'TWO_COLUMN':
                return this.createTwoColumnSlide(pres, slideData);
            case 'SUMMARY_SLIDE':
                return this.createSummarySlide(pres, slideData);
            case 'THANK_YOU_SLIDE':
                return this.createThankYouSlide(pres, slideData);
            default:
                return this.createContentSlide(pres, slideData);
        }
    }

    /**
     * Create title slide with corporate branding
     */
    createTitleSlide(pres, slideData) {
        const slide = pres.addSlide({ masterName: 'TITLE_MASTER' });
        
        // Add title
        slide.addText(slideData.title || 'Business Presentation', {
            placeholder: 'title'
        });
        
        // Add subtitle
        slide.addText(slideData.subtitle || slideData.content?.[0] || 'Professional Analysis and Insights', {
            placeholder: 'subtitle'
        });
        
        // Add corporate logo area (placeholder for now)
        slide.addText('NCS', {
            x: 13.5, y: 7.5, w: 2, h: 1,
            fontSize: 14,
            color: BRAND_COLORS.primary,
            bold: true,
            align: 'right'
        });
        
        return slide;
    }

    /**
     * Create agenda slide
     */
    createAgendaSlide(pres, slideData) {
        const slide = pres.addSlide({ masterName: 'CONTENT_MASTER' });
        
        slide.addText(slideData.title || 'Agenda', {
            placeholder: 'title'
        });
        
        const agendaItems = slideData.content || [
            'Overview and Context',
            'Key Analysis Points', 
            'Findings and Insights',
            'Recommendations',
            'Next Steps'
        ];
        
        slide.addText(agendaItems, {
            placeholder: 'content',
            bullet: { type: 'bullet', style: 'circle' }
        });
        
        return slide;
    }

    /**
     * Create standard content slide
     */
    createContentSlide(pres, slideData) {
        const slide = pres.addSlide({ masterName: 'CONTENT_MASTER' });
        
        slide.addText(slideData.title || 'Content', {
            placeholder: 'title'
        });
        
        const content = slideData.content || ['Content point extracted from document'];
        
        // Check if content should be a table
        if (this.shouldCreateTable(content)) {
            return this.createTableFromContent(slide, content);
        }
        
        // Standard bullet points
        slide.addText(content, {
            placeholder: 'content',
            bullet: { type: 'bullet', style: 'circle' }
        });
        
        return slide;
    }

    /**
     * Create table slide with structured data
     */
    createTableSlide(pres, slideData) {
        const slide = pres.addSlide({ masterName: 'CONTENT_MASTER' });
        
        slide.addText(slideData.title || 'Data Analysis', {
            placeholder: 'title'
        });
        
        const tableData = slideData.tableData || this.convertContentToTableData(slideData.content);
        
        slide.addTable(tableData, {
            x: 0.8, y: 2.2, w: 14.4, h: 5.5,
            fill: { color: BRAND_COLORS.lightGray },
            border: { pt: 1, color: BRAND_COLORS.primary },
            fontSize: 14,
            fontFace: 'Calibri'
        });
        
        return slide;
    }

    /**
     * Create chart slide
     */
    createChartSlide(pres, slideData) {
        const slide = pres.addSlide({ masterName: 'CONTENT_MASTER' });
        
        slide.addText(slideData.title || 'Analysis Chart', {
            placeholder: 'title'
        });
        
        // Example chart data - in real implementation, this would come from slideData
        const chartData = slideData.chartData || [
            { name: 'Category A', values: [25] },
            { name: 'Category B', values: [35] },
            { name: 'Category C', values: [40] }
        ];
        
        slide.addChart(pres.ChartType.pie, chartData, {
            x: 2, y: 2.5, w: 12, h: 5,
            showTitle: false,
            showLegend: true,
            legendPos: 'r',
            chartColors: [BRAND_COLORS.primary, BRAND_COLORS.secondary, BRAND_COLORS.accent]
        });
        
        return slide;
    }

    /**
     * Create two-column layout slide
     */
    createTwoColumnSlide(pres, slideData) {
        const slide = pres.addSlide({ masterName: 'CONTENT_MASTER' });
        
        slide.addText(slideData.title || 'Comparison Analysis', {
            placeholder: 'title'
        });
        
        const leftContent = slideData.leftContent || slideData.content?.slice(0, Math.ceil(slideData.content.length / 2)) || ['Left column content'];
        const rightContent = slideData.rightContent || slideData.content?.slice(Math.ceil(slideData.content.length / 2)) || ['Right column content'];
        
        // Left column
        slide.addText(leftContent, {
            x: 0.8, y: 2.2, w: 7, h: 5.5,
            fontSize: 16,
            color: BRAND_COLORS.text,
            bullet: { type: 'bullet', style: 'circle' }
        });
        
        // Right column
        slide.addText(rightContent, {
            x: 8.2, y: 2.2, w: 7, h: 5.5,
            fontSize: 16,
            color: BRAND_COLORS.text,
            bullet: { type: 'bullet', style: 'circle' }
        });
        
        return slide;
    }

    /**
     * Create summary slide
     */
    createSummarySlide(pres, slideData) {
        const slide = pres.addSlide({ masterName: 'CONTENT_MASTER' });
        
        slide.addText('Key Takeaways', {
            placeholder: 'title'
        });
        
        const summaryPoints = slideData.content || [
            'Key insights from analysis',
            'Important findings and observations', 
            'Strategic recommendations',
            'Proposed next steps'
        ];
        
        slide.addText(summaryPoints, {
            placeholder: 'content',
            bullet: { type: 'bullet', style: 'circle' },
            fontSize: 20,
            bold: true
        });
        
        return slide;
    }

    /**
     * Create thank you slide with NCS branding
     */
    createThankYouSlide(pres, slideData) {
        const slide = pres.addSlide({ masterName: 'TITLE_MASTER' });
        
        slide.addText('Thank You', {
            placeholder: 'title'
        });
        
        slide.addText('Questions & Discussion', {
            placeholder: 'subtitle'
        });
        
        // Add NCS branding
        slide.addText('NCS Singapore', {
            x: 1, y: 7.5, w: 14, h: 1,
            fontSize: 16,
            color: BRAND_COLORS.primary,
            bold: true,
            align: 'center'
        });
        
        return slide;
    }

    /**
     * Check if content should be converted to a table
     */
    shouldCreateTable(content) {
        if (!Array.isArray(content) || content.length < 3) return false;
        
        // Look for structured data patterns
        const structuredCount = content.filter(item => {
            const str = String(item);
            return str.includes(':') || 
                   str.match(/\$[\d,]+/) || 
                   str.match(/\d+\.?\d*%/) ||
                   str.match(/\d{4}-\d{2}-\d{2}/);
        }).length;
        
        return structuredCount >= content.length * 0.6;
    }

    /**
     * Convert content to table data
     */
    convertContentToTableData(content) {
        if (!content || !Array.isArray(content)) return [['Item', 'Value']];
        
        const tableData = [['Category', 'Details']];
        
        content.forEach(item => {
            const str = String(item);
            if (str.includes(':')) {
                const parts = str.split(':', 2);
                tableData.push([parts[0].trim(), parts[1].trim()]);
            } else {
                tableData.push([str, '']);
            }
        });
        
        return tableData;
    }

    /**
     * Create table from content within a slide
     */
    createTableFromContent(slide, content) {
        const tableData = this.convertContentToTableData(content);
        
        slide.addTable(tableData, {
            x: 0.8, y: 2.2, w: 14.4, h: 5.5,
            fill: { color: BRAND_COLORS.lightGray },
            border: { pt: 1, color: BRAND_COLORS.primary },
            fontSize: 14,
            fontFace: 'Calibri',
            rowBackgroudColor: [BRAND_COLORS.primary, null] // Header row colored
        });
        
        return slide;
    }
}

module.exports = SlideBuilder;