# ✅ PowerPoint V2 Setup Complete!

Your Pandoc + Markdown PowerPoint generation system is ready!

## 🚀 Quick Start

1. **Install Pandoc** (required for conversion):
   ```bash
   # Windows (Chocolatey)
   choco install pandoc
   
   # Windows (Download)
   # Visit: https://pandoc.org/installing.html
   
   # Linux/Azure
   apt-get install pandoc
   ```

2. **Add Your Company Template**:
   - Place your PowerPoint template at: `templates/company_template.pptx`
   - The system will automatically detect and use it

3. **Start the Service**:
   ```bash
   cd azure_function_ppt_v2
   func start
   ```
   
4. **Access the API**:
   - **URL**: `http://localhost:7073/api/powerpoint_generation_v2`
   - **Port**: 7073 (different from V1's 7071)

## 🔧 Configuration

### Environment Variables
The V2 system uses your existing `.env` file from the root directory:
```
document-generation-v1.1/
├── .env                    # ← Your existing environment file
├── azure_function_pdf/     # Port 7072
├── azure_function_ppt/     # Port 7071  
└── azure_function_ppt_v2/  # Port 7073
```

### Port Assignment
- **PDF Service**: Port 7072
- **PPT V1 Service**: Port 7071  
- **PPT V2 Service**: Port 7073

## 📝 API Usage

### Request Format
```json
{
  "user_message": "Create presentation from [document]base64-content",
  "conversation_history": []
}
```

### Response Format
```json
{
  "response_data": {
    "status": "completed",
    "system_version": "V2_Pandoc_Markdown",
    "powerpoint_output": {
      "ppt_data": "base64-pptx-content",
      "filename": "presentation_v2_session.pptx"
    },
    "processing_info": {
      "slide_count": 8,
      "template_used": true,
      "processing_method": "pandoc_markdown"
    }
  }
}
```

## 🎯 Key Features

- **Template Compatible**: Uses your existing company PowerPoint templates
- **Table Support**: Native markdown tables convert to PowerPoint tables
- **Consistent Output**: Same input always produces same result
- **Agent Conversations**: Maintains your existing chat workflow
- **Error Handling**: Graceful fallbacks with detailed logging

## 🔍 Testing

1. Use your existing frontend pointing to port 7073
2. Upload a document with `[document]base64-content`
3. Check `local_output/` folder for generated presentations
4. Compare consistency with V1 system

## 📊 Monitoring

Generated files are saved locally in:
```
azure_function_ppt_v2/local_output/presentation_v2_*.pptx
```

Check the `processing_info` in API responses for:
- Slide count
- Template usage status  
- Processing method
- Error details (if any)

Your V2 system is ready to create more consistent PowerPoint presentations! 🎉