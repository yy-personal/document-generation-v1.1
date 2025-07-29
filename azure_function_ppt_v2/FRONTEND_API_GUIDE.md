# Frontend API Integration Guide
## PowerPoint Generation Service v2 - 2-Stage Clarification Workflow

Guide for integrating the new 2-stage clarification PowerPoint generation API into frontend applications.

## API Endpoint

**Production URL:** `https://fnncsgptpptagent-v2.azurewebsites.net/api/powerpointGeneration`
**Method:** `POST`
**Content-Type:** `application/json`

## New 2-Stage Workflow Overview

The API now uses a 2-stage workflow for better user experience:

1. **Stage 1**: User clicks "Create Presentation" → AI analyzes conversation → Shows clarification questions popup
2. **Stage 2**: User answers questions → Generates customized PowerPoint presentation

## Stage 1: Get Clarification Questions

### Request Format
```javascript
{
  "user_message": "[create_presentation]",
  "entra_id": "user-123",
  "session_id": "session-abc-123",
  "conversation_history": [
    {
      "session_id": "session-abc-123",
      "total_questions": 3,
      "conversation": [
        {
          "question_id": "uuid-1",
          "question": "Tell me about AI in business",
          "response_id": "uuid-2",
          "response": "AI transforms business operations through automation...",
          "response_timestamp": "2025-07-29T06:02:15.905Z"
        }
      ]
    }
  ]
}
```

### Stage 1 Response Structure
```javascript
{
  "response_data": {
    "status": "completed",
    "session_id": "session-abc-123",
    "show_clarification_popup": true,
    "clarification_questions": [
      {
        "id": "slide_count",
        "question": "How many slides would you like in your presentation? (Recommended: 12 slides based on AI analysis of your content)",
        "field_type": "number",
        "placeholder": "12",
        "required": true,
        "default_value": 12,
        "validation": {"min": 5, "max": 50},
        "recommendation": 12,
        "recommendation_source": "AI analysis of your content",
        "ai_generated": true
      },
      {
        "id": "audience_level",
        "question": "What is the technical level of your audience?",
        "field_type": "select",
        "options": ["Beginner", "Intermediate", "Advanced", "Mixed audience"],
        "required": true,
        "default_value": "Intermediate"
      },
      {
        "id": "include_examples",
        "question": "Would you like detailed examples and case studies included?",
        "field_type": "boolean",
        "required": true,
        "default_value": true
      },
      {
        "id": "business_style",
        "question": "What type of business presentation format do you prefer?",
        "field_type": "select",
        "options": ["Executive Summary", "Detailed Analysis", "Strategic Overview", "Training Material"],
        "required": true,
        "default_value": "Strategic Overview"
      }
    ],
    "pipeline_info": ["ConversationManager", "SlideEstimator"],
    "processing_info": {
      "slide_estimate": {
        "estimated_slides": 12,
        "content_complexity": "medium",
        "reasoning": "Based on conversation content length and business context"
      }
    }
  }
}
```

## Stage 2: Generate Presentation with Answers

### Request Format
```javascript
{
  "user_message": "[clarification_answers]{\"slide_count\": 15, \"audience_level\": \"Advanced\", \"include_examples\": true, \"business_style\": \"Strategic Overview\"}",
  "entra_id": "user-123", 
  "session_id": "session-abc-123",
  "conversation_history": [same_as_stage_1]
}
```

### Stage 2 Response Structure
```javascript
{
  "response_data": {
    "status": "completed",
    "session_id": "session-abc-123",
    "pipeline_info": ["ConversationManager", "DocumentProcessor", "SlideEstimator (user choice)", "ContentStructurer", "PptxGenerator"],
    "processing_info": {
      "slide_estimate": {
        "estimated_slides": 15,
        "content_complexity": "user_specified",
        "reasoning": "User chose 15 slides from clarification popup",
        "user_specified": true
      }
    },
    "powerpoint_output": {
      "base64_content": "UEsDBBQAAAAIA...",
      "filename": "presentation_PPTV220250729ABC123_20250729.pptx",
      "file_size_kb": 1247,
      "slide_count": 15,
      "generation_info": {
        "template_used": "ncs_ppt_template_2023",
        "total_processing_time": "8.7s",
        "customization_applied": {
          "audience_level": "Advanced",
          "include_examples": true,
          "business_style": "Strategic Overview"
        }
      }
    },
    "response_text": "PowerPoint presentation generated successfully!\n\nPresentation Details:\n- Slides: 15\n- File: presentation_PPTV220250729ABC123_20250729.pptx\n- Size: 1247KB\n\nYour presentation is ready for download."
  }
}
```

## Frontend Implementation

### React Hook for 2-Stage Workflow
```javascript
const usePowerPointClarificationWorkflow = () => {
  const [stage, setStage] = useState('ready'); // 'ready', 'questions', 'generating', 'completed'
  const [sessionId, setSessionId] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [clarificationQuestions, setClarificationQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const API_URL = 'https://fnncsgptpptagent-v2.azurewebsites.net/api/powerpointGeneration';

  // Stage 1: Get clarification questions
  const requestClarificationQuestions = async (conversationData, userId) => {
    setIsLoading(true);
    setStage('questions');

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_message: '[create_presentation]',
          conversation_history: [conversationData],
          session_id: conversationData.session_id,
          entra_id: userId
        })
      });

      const data = await response.json();
      
      if (data.response_data.show_clarification_popup) {
        setSessionId(data.response_data.session_id);
        setConversationHistory([conversationData]);
        setClarificationQuestions(data.response_data.clarification_questions);
        return data.response_data.clarification_questions;
      }
      
      throw new Error('Unexpected response format');
    } catch (error) {
      console.error('Stage 1 failed:', error);
      setStage('ready');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Stage 2: Generate presentation with answers
  const generatePresentationWithAnswers = async (answers, userId) => {
    setIsLoading(true);
    setStage('generating');

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_message: `[clarification_answers]${JSON.stringify(answers)}`,
          conversation_history: conversationHistory,
          session_id: sessionId,
          entra_id: userId
        })
      });

      const data = await response.json();
      
      if (data.response_data.powerpoint_output) {
        setStage('completed');
        return data.response_data;
      }
      
      throw new Error('PowerPoint generation failed');
    } catch (error) {
      console.error('Stage 2 failed:', error);
      setStage('questions');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const resetWorkflow = () => {
    setStage('ready');
    setSessionId(null);
    setConversationHistory([]);
    setClarificationQuestions([]);
  };

  return {
    stage,
    clarificationQuestions,
    requestClarificationQuestions,
    generatePresentationWithAnswers,
    resetWorkflow,
    isLoading
  };
};
```

### Clarification Questions Modal Component
```javascript
const ClarificationQuestionsModal = ({ questions, onSubmit, onCancel, isLoading }) => {
  const [answers, setAnswers] = useState({});

  useEffect(() => {
    // Initialize with default values
    const defaultAnswers = {};
    questions.forEach(q => {
      defaultAnswers[q.id] = q.default_value;
    });
    setAnswers(defaultAnswers);
  }, [questions]);

  const handleSubmit = () => {
    // Validate required fields
    const missingRequired = questions.filter(q => 
      q.required && (answers[q.id] === undefined || answers[q.id] === '')
    );
    
    if (missingRequired.length > 0) {
      alert(`Please answer: ${missingRequired.map(q => q.question).join(', ')}`);
      return;
    }

    onSubmit(answers);
  };

  const renderField = (question) => {
    switch (question.field_type) {
      case 'number':
        return (
          <input
            type="number"
            value={answers[question.id] || ''}
            onChange={(e) => setAnswers(prev => ({
              ...prev, 
              [question.id]: parseInt(e.target.value)
            }))}
            min={question.validation?.min}
            max={question.validation?.max}
            placeholder={question.placeholder}
            required={question.required}
          />
        );

      case 'select':
        return (
          <select
            value={answers[question.id] || ''}
            onChange={(e) => setAnswers(prev => ({
              ...prev,
              [question.id]: e.target.value
            }))}
            required={question.required}
          >
            {question.options.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        );

      case 'boolean':
        return (
          <label>
            <input
              type="checkbox"
              checked={answers[question.id] || false}
              onChange={(e) => setAnswers(prev => ({
                ...prev,
                [question.id]: e.target.checked
              }))}
            />
            Yes
          </label>
        );

      default:
        return (
          <input
            type="text"
            value={answers[question.id] || ''}
            onChange={(e) => setAnswers(prev => ({
              ...prev,
              [question.id]: e.target.value
            }))}
            placeholder={question.placeholder}
            required={question.required}
          />
        );
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Customize Your Presentation</h2>
        <p>Please answer these questions to create the perfect presentation for you:</p>
        
        <form>
          {questions.map(question => (
            <div key={question.id} className="question-field">
              <label>
                {question.question}
                {question.required && <span className="required">*</span>}
              </label>
              {renderField(question)}
              {question.ai_generated && (
                <small className="ai-recommendation">
                  ✨ {question.recommendation_source}
                </small>
              )}
            </div>
          ))}
        </form>

        <div className="modal-actions">
          <button onClick={onCancel} disabled={isLoading}>
            Cancel
          </button>
          <button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? 'Generating...' : 'Create Presentation'}
          </button>
        </div>
      </div>
    </div>
  );
};
```

### Complete Workflow Component
```javascript
const PowerPointWorkflowComponent = ({ conversationData, userId }) => {
  const {
    stage,
    clarificationQuestions,
    requestClarificationQuestions,
    generatePresentationWithAnswers,
    resetWorkflow,
    isLoading
  } = usePowerPointClarificationWorkflow();

  const [presentationResult, setPresentationResult] = useState(null);

  const handleCreatePresentation = async () => {
    try {
      await requestClarificationQuestions(conversationData, userId);
    } catch (error) {
      alert('Failed to get clarification questions: ' + error.message);
    }
  };

  const handleAnswersSubmit = async (answers) => {
    try {
      const result = await generatePresentationWithAnswers(answers, userId);
      setPresentationResult(result);
    } catch (error) {
      alert('Failed to generate presentation: ' + error.message);
    }
  };

  const downloadPresentation = () => {
    if (!presentationResult?.powerpoint_output) return;

    const { base64_content, filename } = presentationResult.powerpoint_output;
    
    // Convert base64 to blob
    const binaryString = atob(base64_content);
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
    link.download = filename;
    link.click();
    
    URL.revokeObjectURL(url);
  };

  return (
    <div className="powerpoint-workflow">
      {stage === 'ready' && (
        <button 
          onClick={handleCreatePresentation}
          disabled={isLoading}
          className="create-presentation-btn"
        >
          {isLoading ? 'Analyzing...' : 'Create Presentation'}
        </button>
      )}

      {stage === 'questions' && (
        <ClarificationQuestionsModal
          questions={clarificationQuestions}
          onSubmit={handleAnswersSubmit}
          onCancel={resetWorkflow}
          isLoading={isLoading}
        />
      )}

      {stage === 'generating' && (
        <div className="generating-state">
          <div className="spinner"></div>
          <p>Generating your customized presentation...</p>
          <small>This typically takes 6-9 seconds</small>
        </div>
      )}

      {stage === 'completed' && presentationResult && (
        <div className="completion-state">
          <h3>✅ Presentation Ready!</h3>
          <p>{presentationResult.response_text}</p>
          <div className="presentation-details">
            <p><strong>Slides:</strong> {presentationResult.powerpoint_output.slide_count}</p>
            <p><strong>File:</strong> {presentationResult.powerpoint_output.filename}</p>
            <p><strong>Size:</strong> {presentationResult.powerpoint_output.file_size_kb}KB</p>
          </div>
          <div className="actions">
            <button onClick={downloadPresentation} className="download-btn">
              Download Presentation
            </button>
            <button onClick={resetWorkflow} className="create-another-btn">
              Create Another
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```

## Conversation History Format

The API expects conversation history in this specific format:

```javascript
const conversationData = {
  session_id: "unique-session-id",
  total_questions: 3,
  conversation: [
    {
      question_id: "uuid-1",
      question: "Tell me about AI in business",
      response_id: "uuid-2", 
      response: "AI transforms business operations through automation, data analysis...",
      response_timestamp: "2025-07-29T06:02:15.905Z"
    },
    {
      question_id: "uuid-3",
      question: "What are the key benefits?",
      response_id: "uuid-4",
      response: "Key benefits include increased efficiency, cost reduction...",
      response_timestamp: "2025-07-29T06:02:41.329Z"
    }
  ]
};
```

## Error Handling

```javascript
const handleApiError = (error, stage) => {
  console.error(`Stage ${stage} error:`, error);
  
  // Show user-friendly error messages
  switch (stage) {
    case 1:
      return "Unable to analyze your conversation. Please try again.";
    case 2:
      return "Unable to generate presentation. Please check your answers and try again.";
    default:
      return "An unexpected error occurred. Please try again.";
  }
};
```

## Performance Considerations

- **Stage 1**: Typically takes 2-3 seconds (AI slide recommendation)
- **Stage 2**: Typically takes 6-9 seconds (full presentation generation)
- **Total Experience**: 8-12 seconds with user interaction
- **File Sizes**: Generated presentations are typically 800KB - 2MB
- **Concurrent Limits**: Azure Function handles multiple simultaneous requests

## Integration Checklist

- [ ] Implement 2-stage workflow (questions → generation)
- [ ] Handle conversation history format correctly
- [ ] Use exact bracket notation triggers
- [ ] Implement clarification questions modal
- [ ] Handle all field types (number, select, boolean)
- [ ] Implement file download functionality
- [ ] Add proper error handling for both stages
- [ ] Show loading states during processing
- [ ] Test with different conversation content types
- [ ] Validate user inputs before submission

The new 2-stage workflow provides much better user experience with AI-powered recommendations and customizable presentation generation based on user preferences.