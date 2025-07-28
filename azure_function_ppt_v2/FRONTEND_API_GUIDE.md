# Frontend API Integration Guide
## PowerPoint Generation Service v2

Guide for integrating the conversational PowerPoint generation API into frontend applications.

## API Endpoint

**Production URL:** `https://fnncsgptpptagent-v2.azurewebsites.net/api/powerpointGeneration`
**Method:** `POST`
**Content-Type:** `application/json`

## Request Format

```javascript
{
  "user_message": "Create a presentation [document]base64_content",
  "entra_id": "user-123",
  "session_id": "optional-session-id", // Auto-generated if not provided
  "conversation_history": [] // Array of previous messages
}
```

## Response Structure

```javascript
{
  "response_data": {
    "status": "completed", // "processing", "completed", "error"
    "session_id": "generated-session-id",
    "conversation_history": [], // Updated conversation array
    "pipeline_info": ["ConversationManager", "SlideEstimator"], // Which agents ran
    "processing_info": {
      "conversation": {
        "should_generate_presentation": false,
        "has_document_content": true,
        "response_text": "What kind of presentation would work best?",
        "user_context": "..."
      },
      "slide_estimate": {
        "estimated_slides": 8,
        "reasoning": "Based on content complexity..."
      }
    },
    "response_text": "Based on your document, I estimate...",
    "powerpoint_output": null // Only present when presentation is generated
  }
}
```

## Conversation Flow

### 1. Document Upload + Question
```javascript
const response1 = await fetch(API_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_message: "What kind of presentation works best? [document]" + base64Content,
    entra_id: userId
  })
});

// Response: Conversational response with slide estimate
// should_generate_presentation: false
// powerpoint_output: null
```

### 2. Follow-up Conversation
```javascript
const response2 = await fetch(API_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_message: "Focus on implementation timeline and metrics",
    session_id: response1.response_data.session_id,
    conversation_history: response1.response_data.conversation_history,
    entra_id: userId
  })
});

// Response: Updated context and refined slide estimate
// should_generate_presentation: false
// powerpoint_output: null
```

### 3. Generate Presentation
```javascript
const response3 = await fetch(API_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_message: "Create the presentation now",
    session_id: response2.response_data.session_id,
    conversation_history: response2.response_data.conversation_history,
    entra_id: userId
  })
});

// Response: Full pipeline execution with PowerPoint file
// should_generate_presentation: true
// powerpoint_output: { base64_content, filename, file_size_kb, slide_count }
```

## PowerPoint Output Structure

When `should_generate_presentation: true`, the response includes:

```javascript
{
  "powerpoint_output": {
    "base64_content": "UEsDBBQAAAAIA...", // Base64 encoded .pptx file
    "filename": "presentation_ABC123_20250128.pptx",
    "file_size_kb": 1247,
    "slide_count": 8,
    "generation_info": {
      "template_used": "ncs_ppt_template_2023",
      "total_processing_time": "12.3s",
      "agent_pipeline": ["ConversationManager", "DocumentProcessor", "SlideEstimator", "ContentStructurer", "PptxGenerator"]
    }
  }
}
```

## Frontend Implementation Examples

### React Hook for Conversation
```javascript
const usePowerPointConversation = () => {
  const [sessionId, setSessionId] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (message, userId) => {
    setIsLoading(true);
    
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_message: message,
          session_id: sessionId,
          conversation_history: history,
          entra_id: userId
        })
      });

      const data = await response.json();
      
      setSessionId(data.response_data.session_id);
      setHistory(data.response_data.conversation_history);
      
      return data.response_data;
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return { sendMessage, sessionId, history, isLoading };
};
```

### File Download Handler
```javascript
const downloadPowerPoint = (powerpoint_output) => {
  if (!powerpoint_output?.base64_content) {
    console.error('No PowerPoint data to download');
    return;
  }

  // Convert base64 to blob
  const binaryString = atob(powerpoint_output.base64_content);
  const bytes = new Uint8Array(binaryString.length);
  
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  const blob = new Blob([bytes], { 
    type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' 
  });

  // Create download link
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = powerpoint_output.filename;
  link.click();
  
  // Cleanup
  URL.revokeObjectURL(url);
};
```

### Complete Chat Interface
```javascript
const PowerPointChat = ({ userId, documentBase64 }) => {
  const { sendMessage, history, isLoading } = usePowerPointConversation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message to UI
    const userMessage = { role: 'user', content: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);

    try {
      // Send to API (include document on first message)
      const isFirstMessage = messages.length === 0;
      const messageWithDoc = isFirstMessage && documentBase64 
        ? `${input} [document]${documentBase64}`
        : input;

      const response = await sendMessage(messageWithDoc, userId);
      
      // Add assistant response to UI
      const assistantMessage = { 
        role: 'assistant', 
        content: response.response_text,
        timestamp: new Date(),
        powerpoint_output: response.powerpoint_output 
      };
      setMessages(prev => [...prev, assistantMessage]);

      setInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  return (
    <div className="powerpoint-chat">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.powerpoint_output && (
              <button onClick={() => downloadPowerPoint(msg.powerpoint_output)}>
                Download {msg.powerpoint_output.filename}
              </button>
            )}
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about your presentation..."
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading}>
          {isLoading ? 'Processing...' : 'Send'}
        </button>
      </div>
    </div>
  );
};
```

## Document Processing

### File to Base64 Conversion
```javascript
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(',')[1]; // Remove data:mime;base64, prefix
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

// Usage
const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (file && (file.type === 'application/pdf' || file.type.includes('word'))) {
    const base64Content = await fileToBase64(file);
    setDocumentBase64(base64Content);
  }
};
```

## Error Handling

```javascript
const handleApiResponse = (response) => {
  if (response.response_data.status === 'error') {
    throw new Error(response.response_data.error_message);
  }
  
  if (response.response_data.status === 'processing') {
    // Handle processing state if needed
    console.log('Request is still processing...');
  }
  
  return response.response_data;
};
```

## Response State Management

Track conversation state based on API responses:

```javascript
const getConversationState = (responseData) => {
  const hasDocument = responseData.processing_info?.conversation?.has_document_content;
  const shouldGenerate = responseData.processing_info?.conversation?.should_generate_presentation;
  const hasOutput = !!responseData.powerpoint_output;

  if (hasOutput) return 'completed';
  if (shouldGenerate) return 'generating';
  if (hasDocument) return 'discussing';
  return 'initial';
};

// Use state to show appropriate UI
const state = getConversationState(response);
switch (state) {
  case 'initial': 
    return <DocumentUpload />;
  case 'discussing': 
    return <ConversationInterface />;
  case 'generating': 
    return <GeneratingSpinner />;
  case 'completed': 
    return <DownloadInterface />;
}
```

## Key Integration Points

1. **Session Management**: Always pass `session_id` and `conversation_history` for context
2. **Document Handling**: Include `[document]base64_content` in first message only
3. **State Detection**: Use `should_generate_presentation` to determine when PowerPoint is ready
4. **File Download**: Convert `base64_content` to blob for browser download
5. **Error Handling**: Check `status` field for error states
6. **Loading States**: API calls typically take 2-15 seconds depending on complexity

The API supports full conversational flow - upload document, discuss requirements, refine context, then generate presentation when ready.