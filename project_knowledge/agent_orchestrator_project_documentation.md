# Agent Orchestrator Project Documentation
## Phase 1 (Current) & Phase 2 (Upcoming) Implementation Guide

---

## 🎯 **Project Overview**

This project implements an advanced AI Agent Orchestrator using Microsoft Semantic Kernel, designed to create intelligent agents through dynamic pipeline processing. The system currently supports markdown generation and will expand to support specialized CV processing and document creation.

### **Core Architecture**
- **Platform**: Azure Functions with Python
- **AI Framework**: Microsoft Semantic Kernel
- **AI Model**: Azure OpenAI GPT-4
- **Integration**: Power Automate + Dataverse for data persistence
- **Deployment**: Azure Cloud with CI/CD pipeline

---

## 📋 **Phase 1: Current Implementation (Markdown Agent Generator)**

### **System Overview**
The current system transforms user input (text/Word documents) into comprehensive markdown agent specifications through a sophisticated 5-step pipeline.

### **Technical Architecture**

#### **Core Components**
```
web_orchestrator.py          # Main orchestration logic
config.py                    # Configuration and agent settings
function_app.py              # Azure Functions entry point
agents/                      # Specialized agent implementations
├── dynamic_orchestrator_agent.py
├── sk_input_validator_skill.py
├── sk_research_skill.py
├── sk_gap_analysis_skill.py
├── sk_evaluator_skill.py
├── sk_solution_consultant_skill.py
├── sk_formatter_agent.py
└── sk_post_completion_refinement_agent.py
```

#### **Pipeline Flow (5-Step Process)**
```
1. Input Validation (SKInputValidatorSkill)
   ↓
2. Dynamic Agent Orchestration (DynamicOrchestratorAgent)
   ↓
3. Content Creation (Selected: SKResearchSkill | SKGapAnalysisSkill)
   ↓
4. Quality Evaluation (SKEvaluatorSkill + SKSolutionConsultantSkill)
   ↓
5. Markdown Formatting (SKFormatterAgent)
```

### **Key Features**

#### **1. Intelligent Input Processing**
- **Word Document Extraction**: Automatic content extraction from `.docx` files
- **Input Validation**: Ensures request clarity before processing
- **Clarification Loop**: Up to 2 rounds of user clarification if needed

#### **2. Dynamic Agent Selection**
- **Content Agents**: `SKResearchSkill`, `SKGapAnalysisSkill`
- **Mandatory Agents**: Input validator, evaluator, formatter
- **Selection Logic**: Based on request complexity and type

#### **3. Quality Assurance**
- **Quality Threshold**: 80/100 minimum score
- **Improvement Iterations**: Up to 3 rounds of refinement
- **Evaluation Metrics**: Comprehensive scoring with feedback loop

#### **4. Session Management**
- **Session IDs**: Format `PCSH{DDMMYYYY}{UNIQUE10}`
- **Conversation Tracking**: Complete history preservation
- **Post-Completion Refinement**: Discussion and update support

#### **5. Power Automate Integration**
- **Real-time Sync**: Automatic Dataverse updates
- **Data Structure**: Complete conversation and metadata storage
- **Error Handling**: Robust error recovery and reporting

### **Configuration Settings**
```python
# Quality Control
QUALITY_THRESHOLD = 80
MAX_IMPROVEMENT_ITERATIONS = 3
MAX_CLARIFICATION_ROUNDS = 2

# Pipeline Components
MANDATORY_START_AGENTS = ["SKInputValidatorSkill"]
CONTENT_AGENTS = ["SKGapAnalysisSkill", "SKResearchSkill"]
MANDATORY_END_AGENTS = ["SKEvaluatorSkill", "SKSolutionConsultantSkill", "SKFormatterAgent"]

# File Format Support
SUPPORTED_INPUT_FORMATS = ["PDF", "Word (.docx)", "Excel (.xlsx)", "Images", "PowerPoint (.pptx)", "Text"]
SUPPORTED_OUTPUT_FORMATS = ["Text string", "Word documents (.docx)"]
```

### **API Endpoints**

#### **Primary Endpoint: `/api/pc_conversation`**
```json
{
  "request": {
    "user_message": "string",
    "entra_id": "string",
    "session_id": "string (optional)",
    "conversation_history": []
  },
  "response": {
    "conversation_data": {
      "status": "needs_clarification|completed|error",
      "session_id": "string",
      "entra_id": "string",
      "conversation_history": [],
      "pipeline_info": [],
      "quality_summary": "string",
      "usable_outputs": {
        "generated_agent_name": "string",
        "generated_summary": "string",
        "generated_markdown": "string"
      }
    },
    "power_automate_response": {}
  }
}
```

#### **System Info Endpoint: `/api/get_system_info`**
Returns current configuration and system status.

### **Data Storage (Dataverse)**

#### **SessionHistories Table**
- `SessionId` (Primary Key)
- `EntraId` (User identifier)
- `Status` (needs_clarification, completed, error)
- `SessionHistoryContent` (JSON conversation array)
- `PipelineInfo` (Agent pipeline used)
- `QualitySummary` (Quality metrics)
- `Markdown` (Generated markdown content)
- `ModifiedOn` (Last update timestamp)

### **Current Use Cases**
1. **Agent Specification Creation**: Generate detailed AI agent specifications
2. **Document Processing**: Extract and process Word document content
3. **Quality Assurance**: Iterative improvement until quality standards met
4. **Collaborative Refinement**: Post-completion discussion and updates

---

## 🚀 **Phase 2: Document Processing Services**

### **Service Overview**
Three dedicated Azure Functions for generic document processing with extraction, enhancement, and output generation capabilities.

#### **Architecture**
```
External Orchestrator
         ↓
    Route Decision
         ↓
┌─────────────────────────────────────────┐
│  Azure Function 1: PDF Processing      │
│  Azure Function 2: Word Processing     │
│  Azure Function 3: PPT Generation      │
└─────────────────────────────────────────┘
```

#### **Individual Function Responsibilities**

##### **Function 1: PDF Processing Service**
- **Input**: Documents in PDF format
- **Processing**: Extract, analyze, and enhance PDF content
- **Output**: Processed PDF document
- **Use Cases**: Reports, contracts, CVs, manuals

##### **Function 2: Word Processing Service**
- **Input**: Documents in Word (.docx) format
- **Processing**: Extract, analyze, and enhance Word content
- **Output**: Processed Word document
- **Use Cases**: Letters, proposals, CVs, documentation

##### **Function 3: PPT Generation Service**
- **Input**: Document content (from orchestrator)
- **Processing**: Create presentations from document data
- **Output**: PowerPoint presentation
- **Use Cases**: Executive summaries, CV highlights, report presentations

### **Generic Processing Capabilities**
- **Document Analysis**: Content extraction and structure analysis
- **Content Enhancement**: AI-powered content improvement
- **Format Conversion**: Cross-format document processing
- **Template Application**: Standardized output formatting
- **Quality Assurance**: Automated validation and improvement

### **Example Use Cases**
- **CV Processing**: Extract and enhance CV information
- **Report Summarization**: Create executive summaries
- **Document Standardization**: Apply corporate templates
- **Content Restructuring**: Reorganize document sections
- **Multi-format Output**: Generate presentations from documents

### **Deployment Structure**
- **3 Independent Azure Functions**: Separate deployments per format
- **External Orchestrator**: Handles routing logic and use case determination
- **Frontend**: Simple testing interface for team validation
- **Purpose**: Generic document processing with CV as initial use case

### **Technical Considerations**
- **File Processing**: Support for Word (.docx) and PDF extraction
- **Document Generation**: PPT, Word, and PDF output capabilities
- **Independent Deployment**: Separate from Phase 1 infrastructure
- **Simple Testing**: Frontend for team validation without codebase integration

---

## 🎯 **Success Metrics**

### **Phase 1 (Current)**
- **Quality Score**: Minimum 80/100 for all generated specifications
- **Processing Time**: <30 seconds average per request
- **System Reliability**: 99% uptime for Azure Functions

### **Phase 2 (Target)**
- **File Processing**: Successful extraction from Word/PDF formats
- **Document Quality**: Professional-grade output documents
- **Team Adoption**: Smooth testing and validation workflow

---

## 💡 **Key Success Factors**

### **Technical Excellence**
- **Modular Design**: Reuse Phase 1 components effectively
- **Quality Standards**: Maintain high accuracy and performance
- **Scalability**: Design for concurrent users and large files

### **User Experience**
- **Seamless Integration**: Consistent interface across all use cases
- **Fast Processing**: Maintain performance despite increased complexity
- **Professional Outputs**: Ensure all generated documents meet professional standards

### **Business Value**
- **HR Efficiency**: Streamline CV processing workflows
- **Future Readiness**: Help users identify and develop future skills
- **Data Insights**: Provide analytics on skills trends and gaps

---

*This documentation provides the foundation for implementing Phase 2 while leveraging the robust Phase 1 infrastructure. The modular approach ensures scalability and maintainability across all use cases.*