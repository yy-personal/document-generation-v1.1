/**
 * Document Parser Utility - Advanced document content processing
 */

class DocumentParser {
    constructor() {
        this.minSectionLength = 50;
        this.maxSectionLength = 500;
    }

    /**
     * Parse document content into structured sections
     */
    parseDocument(documentContent) {
        if (!documentContent || typeof documentContent !== 'string') {
            return this.createEmptyStructure();
        }

        return {
            title: this.extractTitle(documentContent),
            sections: this.extractSections(documentContent),
            keyPoints: this.extractKeyPoints(documentContent),
            summary: this.extractSummary(documentContent),
            metadata: this.extractMetadata(documentContent),
            contentLength: documentContent.length,
            processedAt: new Date().toISOString()
        };
    }

    /**
     * Extract document title
     */
    extractTitle(content) {
        // Look for common title patterns
        const lines = content.split('\n').filter(line => line.trim().length > 0);
        
        // Check first few lines for title-like content
        for (let i = 0; i < Math.min(5, lines.length); i++) {
            const line = lines[i].trim();
            
            // Skip if too short or too long
            if (line.length < 10 || line.length > 100) continue;
            
            // Skip if contains common non-title indicators
            if (this.containsNonTitleIndicators(line)) continue;
            
            // Likely a title if it's short, has title-case, and doesn't end with punctuation
            if (this.looksLikeTitle(line)) {
                return line;
            }
        }
        
        return 'Business Analysis Document';
    }

    /**
     * Extract document sections
     */
    extractSections(content) {
        const sections = [];
        
        // Split by common section delimiters
        const paragraphs = content.split(/\n\s*\n/).filter(p => p.trim().length > this.minSectionLength);
        
        paragraphs.forEach((paragraph, index) => {
            const trimmed = paragraph.trim();
            
            if (trimmed.length >= this.minSectionLength) {
                const section = {
                    id: `section_${index + 1}`,
                    title: this.generateSectionTitle(trimmed, index),
                    content: this.cleanSectionContent(trimmed),
                    type: this.determineSectionType(trimmed),
                    length: trimmed.length,
                    keyPhrases: this.extractKeyPhrases(trimmed)
                };
                
                sections.push(section);
            }
        });
        
        return sections.slice(0, 10); // Limit to 10 sections
    }

    /**
     * Extract key points from document
     */
    extractKeyPoints(content) {
        const points = [];
        
        // Look for bullet points
        const bulletMatches = content.match(/^[\s]*[•\-\*]\s+.+$/gm);
        if (bulletMatches) {
            bulletMatches.forEach(match => {
                const cleaned = match.replace(/^[\s]*[•\-\*]\s+/, '').trim();
                if (cleaned.length > 20 && cleaned.length < 200) {
                    points.push(cleaned);
                }
            });
        }
        
        // Look for numbered points
        const numberedMatches = content.match(/^\s*\d+[\.\)]\s+.+$/gm);
        if (numberedMatches) {
            numberedMatches.forEach(match => {
                const cleaned = match.replace(/^\s*\d+[\.\)]\s+/, '').trim();
                if (cleaned.length > 20 && cleaned.length < 200) {
                    points.push(cleaned);
                }
            });
        }
        
        // Extract sentences that look like key points
        if (points.length < 5) {
            const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 30);
            sentences.forEach(sentence => {
                const trimmed = sentence.trim();
                if (this.looksLikeKeyPoint(trimmed)) {
                    points.push(trimmed);
                }
            });
        }
        
        return points.slice(0, 15); // Limit to 15 key points
    }

    /**
     * Extract document summary
     */
    extractSummary(content) {
        const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 20);
        
        // Take first 3 meaningful sentences as summary
        const summarySentences = sentences
            .slice(0, 10)
            .filter(s => this.isMeaningfulSentence(s))
            .slice(0, 3);
        
        return summarySentences.join('. ') + '.';
    }

    /**
     * Extract metadata from document
     */
    extractMetadata(content) {
        return {
            wordCount: content.split(/\s+/).length,
            characterCount: content.length,
            paragraphCount: content.split(/\n\s*\n/).length,
            sentenceCount: content.split(/[.!?]+/).length,
            hasNumbers: /\d/.test(content),
            hasPercentages: /%/.test(content),
            hasCurrency: /\$/.test(content),
            hasDates: /\d{4}[-\/]\d{2}[-\/]\d{2}|\d{2}[-\/]\d{2}[-\/]\d{4}/.test(content),
            estimatedReadingTime: Math.ceil(content.split(/\s+/).length / 200) // Words per minute
        };
    }

    /**
     * Helper: Check if line contains non-title indicators
     */
    containsNonTitleIndicators(line) {
        const nonTitlePatterns = [
            /^(the|this|that|these|those|a|an)\s/i,
            /\d{4}[-\/]\d{2}[-\/]\d{2}/, // Dates
            /\$\d+/, // Currency
            /\d+%/, // Percentages
            /(inc|ltd|llc|corp)/i, // Company suffixes
            /^page\s+\d+/i,
            /^chapter\s+\d+/i
        ];
        
        return nonTitlePatterns.some(pattern => pattern.test(line));
    }

    /**
     * Helper: Check if line looks like a title
     */
    looksLikeTitle(line) {
        // Title characteristics
        const hasCapitalWords = /[A-Z][a-z]+\s+[A-Z][a-z]+/.test(line);
        const isReasonableLength = line.length >= 10 && line.length <= 80;
        const doesntEndWithPeriod = !line.endsWith('.');
        const hasMinimalPunctuation = (line.match(/[,;:]/g) || []).length <= 2;
        
        return hasCapitalWords && isReasonableLength && doesntEndWithPeriod && hasMinimalPunctuation;
    }

    /**
     * Helper: Generate section title
     */
    generateSectionTitle(content, index) {
        // Try to extract first sentence as title
        const firstSentence = content.split(/[.!?]/)[0].trim();
        
        if (firstSentence.length > 10 && firstSentence.length < 80) {
            return firstSentence;
        }
        
        // Fallback to generic title
        const sectionTypes = [
            'Overview', 'Analysis', 'Key Points', 'Findings', 
            'Recommendations', 'Details', 'Summary', 'Insights'
        ];
        
        return sectionTypes[index % sectionTypes.length];
    }

    /**
     * Helper: Clean section content
     */
    cleanSectionContent(content) {
        return content
            .replace(/\s+/g, ' ') // Normalize whitespace
            .replace(/^\s*\d+[\.\)]\s*/, '') // Remove leading numbers
            .trim()
            .substring(0, this.maxSectionLength);
    }

    /**
     * Helper: Determine section type
     */
    determineSectionType(content) {
        const lowerContent = content.toLowerCase();
        
        if (lowerContent.includes('recommend') || lowerContent.includes('suggest')) {
            return 'recommendations';
        } else if (lowerContent.includes('summary') || lowerContent.includes('conclusion')) {
            return 'summary';
        } else if (lowerContent.includes('analysis') || lowerContent.includes('finding')) {
            return 'analysis';
        } else if (lowerContent.includes('overview') || lowerContent.includes('introduction')) {
            return 'overview';
        } else {
            return 'content';
        }
    }

    /**
     * Helper: Extract key phrases from text
     */
    extractKeyPhrases(text) {
        // Simple key phrase extraction - look for capitalized phrases
        const phrases = text.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}/g) || [];
        return phrases.slice(0, 5); // Limit to 5 phrases per section
    }

    /**
     * Helper: Check if text looks like a key point
     */
    looksLikeKeyPoint(text) {
        const indicators = [
            'important', 'key', 'significant', 'critical', 'essential',
            'recommend', 'suggest', 'should', 'must', 'need to',
            'increase', 'decrease', 'improve', 'enhance', 'reduce'
        ];
        
        const lowerText = text.toLowerCase();
        return indicators.some(indicator => lowerText.includes(indicator)) && 
               text.length >= 30 && 
               text.length <= 150;
    }

    /**
     * Helper: Check if sentence is meaningful
     */
    isMeaningfulSentence(sentence) {
        const trimmed = sentence.trim();
        return trimmed.length > 20 && 
               trimmed.length < 200 && 
               /[a-zA-Z]/.test(trimmed) && 
               !trimmed.startsWith('Page ') &&
               !trimmed.startsWith('Chapter ');
    }

    /**
     * Helper: Create empty structure
     */
    createEmptyStructure() {
        return {
            title: 'Document Analysis',
            sections: [],
            keyPoints: ['No content available for analysis'],
            summary: 'Document content could not be processed.',
            metadata: {
                wordCount: 0,
                characterCount: 0,
                paragraphCount: 0,
                sentenceCount: 0,
                hasNumbers: false,
                hasPercentages: false,
                hasCurrency: false,
                hasDates: false,
                estimatedReadingTime: 0
            },
            contentLength: 0,
            processedAt: new Date().toISOString()
        };
    }
}

module.exports = DocumentParser;