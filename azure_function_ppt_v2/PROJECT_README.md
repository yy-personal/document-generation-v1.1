# PowerPoint Generation Service V2 - Project Overview

## 📋 Project Status: **IMPLEMENTATION COMPLETE - READY FOR TESTING**

This document tracks the development progress of the V2 PowerPoint generation system using Pandoc + Markdown approach for improved consistency and template compatibility.

---

## 🎯 Project Goals

### Primary Objectives
- ✅ **Improve Consistency**: Replace unpredictable python-pptx with deterministic Pandoc conversion
- ✅ **Better Templates**: Full compatibility with company PowerPoint templates
- ✅ **Agent-Driven**: Maintain conversational AI agent workflow
- ✅ **Table Support**: Native markdown table conversion to PowerPoint tables
- ✅ **Simplified Architecture**: Reduce from 5 agents to streamlined 2-component system

### Secondary Objectives
- ✅ **Port Isolation**: Use port 7073 (separate from V1's 7071 and PDF's 7072)
- ✅ **Config Alignment**: Reuse existing .env configuration from root directory
- ✅ **Agent Autonomy**: Let agents fully determine slide count (max 15 slides limit only)

---

## 🏗️ Architecture Overview

### V2 System Components

```
azure_function_ppt_v2/
├── agents/
│   ├── base_agent.py                    # ✅ Base agent class
│   └── markdown_presentation_agent.py   # ✅ Generates structured markdown from documents
├── utils/
│   └── pandoc_converter.py             # ✅ Handles Pandoc markdown→PPTX conversion
├── templates/
│   ├── README.md                       # ✅ Template integration guide  
│   └── [company_template.pptx]         # 📋 TO BE ADDED by user
├── ppt_orchestrator_v2.py              # ✅ Main conversation orchestrator
├── function_app.py                     # ✅ Azure Function HTTP entry point
├── config.py                           # ✅ V2 configuration (agent-driven slides)
├── host.json                           # ✅ Azure Functions host config (port 7073)
├── local.settings.json                 # ✅ Local development settings
├── requirements.txt                    # ✅ Python dependencies
└── README.md                          # ✅ User documentation
```

### V2 vs V1 Architectural Comparison

| Component | V1 (python-pptx) | V2 (Pandoc) | Status |
|-----------|------------------|-------------|---------|
| **Agent Count** | 5 agents | 2 components | ✅ Simplified |
| **Content Generation** | Complex JSON → python-pptx | Markdown → Pandoc | ✅ Implemented |
| **Template Support** | Limited/Complex | Native/Full | ✅ Implemented |
| **Table Generation** | Complex detection logic | Native markdown tables | ✅ Implemented |
| **Slide Count** | Multiple agents decide | Single agent decides | ✅ Agent-driven |
| **Consistency** | Variable output | Deterministic output | ✅ Improved |

---

## 🔧 Implementation Details

### Agent Flow (V2)
1. **User Request** → `PPTOrchestratorV2.process_conversation_request()`
2. **Document Parsing** → Extract `[document]base64-content` from conversation
3. **Markdown Generation** → `MarkdownPresentationAgent.process()` creates structured markdown
4. **Pandoc Conversion** → `PandocConverter.markdown_to_pptx()` generates PowerPoint
5. **Response** → Return base64 PPTX with processing metadata

### Key Technical Decisions

#### ✅ **Pandoc Integration**
- **Why**: Native PowerPoint generation with full template support
- **Implementation**: `utils/pandoc_converter.py` handles subprocess calls
- **Benefits**: Consistent output, table support, template compatibility

#### ✅ **Markdown-Driven Content**
- **Why**: More predictable than complex JSON structures  
- **Implementation**: `MarkdownPresentationAgent` generates structured markdown
- **Benefits**: Human-readable, debug-friendly, Pandoc-optimized

#### ✅ **Agent-Driven Slide Count**
- **Why**: Let AI determine optimal slides based on content complexity
- **Implementation**: Only `max_slides: 15` limit, no targets or minimums
- **Benefits**: Content-appropriate presentations, agent autonomy

#### ✅ **Port Segregation**
- **PDF Service**: Port 7072
- **PPT V1**: Port 7071  
- **PPT V2**: Port 7073
- **Benefits**: Can run all services simultaneously for testing

---

## 🚦 Current Status

### ✅ **COMPLETED COMPONENTS**

#### Core Architecture
- [x] **Base Agent Class** (`agents/base_agent.py`)
- [x] **Markdown Presentation Agent** (`agents/markdown_presentation_agent.py`)
  - Content analysis with topic extraction
  - Structured markdown generation with YAML front matter
  - Table detection and markdown table generation
  - Agent-driven slide count determination
- [x] **Pandoc Converter Utility** (`utils/pandoc_converter.py`)
  - Markdown to PowerPoint conversion
  - Template integration with fallback
  - Validation and error handling
  - Base64 encoding support

#### Orchestration Layer
- [x] **PPT Orchestrator V2** (`ppt_orchestrator_v2.py`)
  - Conversation flow management
  - Document extraction from chat history
  - Intent analysis (simplified)
  - Error handling and response building
- [x] **Azure Function Entry Point** (`function_app.py`)
  - HTTP trigger on `/api/powerpoint_generation_v2`
  - Local file saving to `local_output/`
  - Error handling and logging

#### Configuration & Setup
- [x] **Configuration System** (`config.py`)
  - Environment loading from parent `.env`
  - Agent-driven slide count (max 15 only)
  - Azure OpenAI service integration
- [x] **Dependencies** (`requirements.txt`)
  - Semantic Kernel 1.30.0
  - Azure Functions support
  - All required utilities
- [x] **Azure Functions Config**
  - `host.json` - Extension bundle [4.*, 5.0.0)
  - `local.settings.json` - Port 7073, Python isolation
- [x] **Documentation**
  - User setup guide (`README.md`)
  - Template integration guide (`templates/README.md`)

### 📋 **PENDING TASKS**

#### Testing & Validation
- [ ] **Install Pandoc** on development/deployment environment
- [ ] **Add Company Template** to `templates/company_template.pptx`
- [ ] **Integration Testing** with existing frontend
- [ ] **Performance Testing** vs V1 system
- [ ] **Template Compatibility Testing** with various PowerPoint templates

#### Optional Enhancements
- [ ] **Debug Mode** - Save intermediate markdown files
- [ ] **Template Validation** - Check template layout compatibility
- [ ] **Batch Processing** - Multiple documents in single request
- [ ] **Custom Slide Layouts** - Support for specialized slide types

---

## 🔬 Testing Strategy

### Phase 1: Local Development Testing
```bash
# 1. Start V2 service
cd azure_function_ppt_v2
func start  # Runs on port 7073

# 2. Test API endpoint
POST http://localhost:7073/api/powerpoint_generation_v2
{
  "user_message": "Create presentation from [document]base64-content",
  "conversation_history": []
}

# 3. Check output
ls local_output/  # Should contain presentation_v2_*.pptx files
```

### Phase 2: Template Integration Testing
- [ ] Test with company PowerPoint template
- [ ] Verify branding, fonts, colors are preserved  
- [ ] Test table formatting with template styles
- [ ] Compare output consistency across multiple runs

### Phase 3: Comparative Testing (V1 vs V2)
- [ ] Same document input to both systems
- [ ] Compare slide count decisions
- [ ] Compare content organization and flow
- [ ] Compare template application quality
- [ ] Compare processing time and reliability

---

## 🐛 Known Issues & Considerations

### Dependencies
- **Pandoc Installation Required**: Must be available in system PATH
- **Template Dependency**: System works without template but better with company template
- **Azure Environment**: Pandoc needs to be installed in Azure deployment

### Limitations
- **Slide Count**: Hard limit of 15 slides (configurable in `config.py`)
- **Content Length**: Markdown generation limited by token limits (~15,000 chars input)
- **Template Features**: Complex PowerPoint animations/transitions may not transfer

### Future Improvements
- **Custom Layout Support**: More sophisticated slide layout detection
- **Multi-language Support**: Non-English document processing
- **Advanced Tables**: Complex table layouts beyond basic markdown
- **Chart Generation**: Integration with chart libraries

---

## 🔄 Migration Strategy

### Parallel Operation Approach
1. **Keep V1 Running**: Maintain existing service on port 7071
2. **Deploy V2**: Run V2 service on port 7073
3. **A/B Testing**: Compare outputs side-by-side
4. **Gradual Migration**: Move traffic percentage from V1 to V2
5. **Full Migration**: Switch to V2 when confidence is high

### Rollback Plan
- V1 system remains untouched and can be reactivated
- Configuration allows instant switching between systems
- All conversation history remains compatible

---

## 📞 Next Steps for Development

### Immediate (Next Session)
1. **Install Pandoc** in development environment
2. **Add Company Template** to `templates/company_template.pptx`
3. **Test Basic Functionality** with sample documents
4. **Verify Port Configuration** works correctly

### Short Term
1. **Integration Testing** with existing frontend
2. **Performance Benchmarking** against V1
3. **Template Compatibility** validation
4. **Error Handling** refinement

### Long Term  
1. **Production Deployment** configuration
2. **Monitoring and Logging** setup
3. **Performance Optimization** if needed
4. **Feature Enhancements** based on user feedback

---

## 📝 Development Notes

### Key Files to Modify for Customization
- `config.py` - Adjust max slides, agent settings, template paths
- `agents/markdown_presentation_agent.py` - Modify content analysis logic
- `utils/pandoc_converter.py` - Adjust Pandoc conversion parameters
- `templates/company_template.pptx` - Replace with actual company template

### Environment Setup Checklist
- [x] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Pandoc installed and accessible via command line
- [x] Azure OpenAI credentials in root `.env` file
- [ ] Company PowerPoint template added
- [x] Azure Functions Core Tools available for local testing

---

## 📊 Success Metrics

### Technical Metrics
- **Consistency**: Same input → Same output every time
- **Template Compatibility**: Company branding preserved in 100% of outputs
- **Table Support**: Structured data correctly formatted as native PowerPoint tables
- **Performance**: Processing time competitive with or better than V1

### Business Metrics  
- **User Satisfaction**: Improved presentation quality feedback
- **Reliability**: Reduced error rates compared to V1
- **Maintenance**: Less code complexity, easier debugging and updates

---

**Last Updated**: January 25, 2025  
**Status**: Ready for testing phase  
**Next Review**: After initial testing and Pandoc installation