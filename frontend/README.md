# PowerPoint Generation Frontend Test Interface

React test interface for the PowerPoint generation service with integrated document processing.

## Overview

Simple, clean test interface that allows you to upload documents and generate professional PowerPoint presentations. All document processing is handled internally by the PowerPoint service - no external APIs required.

### Key Features
- **Direct File Upload** - PDF and Word document support
- **Presentation Type Selection** - Executive Summary, Document Analysis, or General
- **Auto-Detection** - Service intelligently determines optimal presentation type
- **One-Click Download** - Generated PowerPoint files download immediately
- **Real-time Progress** - Visual feedback during generation process
- **Session Continuity** - Support for conversation-based requests

## Architecture

### Simplified Workflow
```
File Upload → Base64 Conversion → PowerPoint Service → Download
     ↓              ↓                      ↓              ↓
 PDF/Word     Convert to Base64    AI Processing    .pptx File
```

**No External Dependencies**: The frontend only communicates with the PowerPoint generation service. All document extraction and processing happens internally.

## Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configuration
The frontend is pre-configured to work with the local PowerPoint service. No API keys or external services required.

```javascript
// Default configuration in src/App.js
const API_CONFIG = {
  PPT_GENERATION_API: 'http://localhost:7071/api/powerpoint_generation'
};
```

### 3. Start Development Server
```bash
npm start
```

Frontend runs on `http://localhost:3000`

## Usage

### Basic Workflow
1. **Upload Document** - Click to select PDF or Word file
2. **Add Request (Optional)** - Specify presentation type or leave blank for auto-detection
3. **Select Type** - Choose from Executive Summary, Document Analysis, General, or Auto
4. **Generate** - Click "Generate PowerPoint" button
5. **Download** - Click download button when generation completes

### Request Examples

**Auto-Detection:**
- Upload file, leave request blank
- Service analyzes content and selects optimal presentation type

**Specific Type:**
- Request: "Create an executive summary"
- Type: Executive Summary
- Result: 8-slide executive presentation

**Custom Instructions:**
- Request: "Focus on technical details and implementation"
- Type: Document Analysis  
- Result: 10-slide technical analysis

## Features

### File Support
- **PDF Documents** - Any PDF file with extractable text
- **Word Documents** - .docx files (Word 2007+)
- **File Size** - Handles documents up to reasonable business sizes

### Presentation Types
- **Executive Summary** (8 slides) - High-level overviews for leadership
- **Document Analysis** (10 slides) - Detailed technical analysis
- **General Presentation** (12 slides) - Standard business presentations
- **Auto-Detect** - Service chooses optimal type based on content

### User Experience
- **Drag & Drop Upload** - Easy file selection
- **Progress Indicators** - Real-time generation status
- **Error Handling** - Clear error messages and recovery
- **Download Management** - Automatic file download with proper naming
- **Session Reset** - Start new tests easily

## Technical Details

### File Processing
```javascript
// Files converted to base64 for service
const base64Data = await fileToBase64(file);
const fileTypeTag = file.type.includes('pdf') ? 'pdf_extraction' : 'word_document_extraction';
const fullMessage = `${request}[${fileTypeTag}]${base64Data}`;
```

### PowerPoint Download
```javascript
// Base64 PowerPoint converted to downloadable file
const { ppt_data, filename } = response.powerpoint_output;
downloadPowerPointFromBase64(ppt_data, filename);
```

## Dependencies

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "lucide-react": "^0.263.1",
  "react-scripts": "5.0.1"
}
```

### External Dependencies
- **Tailwind CSS** - Loaded via CDN for styling
- **None** - No authentication tokens or external APIs required

## Requirements

- PowerPoint generation service running on `localhost:7071`
- Node.js 16+ for React development
- Modern web browser with JavaScript enabled

---

**Frontend Test Interface** - Simple, effective testing for the PowerPoint generation service with integrated document processing.