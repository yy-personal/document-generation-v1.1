import React, { useState } from 'react';
import { Upload, FileText, Download, Loader, AlertCircle, CheckCircle } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [userMessage, setUserMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [conversation, setConversation] = useState([]);

  // API Configuration
  const API_CONFIG = {
    PPT_GENERATION_API: 'http://localhost:7071/api/powerpoint_generation'
  };

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile && (uploadedFile.type.includes('pdf') || uploadedFile.type.includes('word') || uploadedFile.name.endsWith('.docx'))) {
      setFile(uploadedFile);
      setError(null);
    } else {
      setError('Please upload a PDF or Word document');
    }
  };

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  const generatePresentation = async () => {
    if (!file) {
      setError('Please upload a document first');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Convert file to base64
      const base64Data = await fileToBase64(file);
      
      // Build user message with base64 content
      const fileTypeTag = file.type.includes('pdf') ? 'pdf_extraction' : 'word_document_extraction';
      const fullMessage = `${userMessage}[${fileTypeTag}]${base64Data}`;

      // Generate PowerPoint
      const pptResponse = await fetch(API_CONFIG.PPT_GENERATION_API, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_message: fullMessage,
          entra_id: 'frontend-test',
          conversation_history: conversation
        })
      });

      if (!pptResponse.ok) {
        throw new Error(`PowerPoint generation failed: ${pptResponse.status}`);
      }

      const pptData = await pptResponse.json();
      setResults(pptData);
      setConversation(pptData.response_data.conversation_history || []);

    } catch (error) {
      setError(error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadPowerPoint = () => {
    if (!results?.response_data?.powerpoint_output) return;

    const { ppt_data, filename } = results.response_data.powerpoint_output;
    const binaryString = atob(ppt_data);
    const bytes = new Uint8Array(binaryString.length);
    
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    
    const blob = new Blob([bytes], { 
      type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' 
    });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const resetTest = () => {
    setFile(null);
    setUserMessage('');
    setResults(null);
    setError(null);
    setConversation([]);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            PowerPoint Generation Test Interface
          </h1>
          <p className="text-gray-600">
            Upload a document and generate professional PowerPoint presentations (12 slides)
          </p>
        </div>

        {/* Main Interface */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          
          {/* File Upload */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Document
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600">
                  {file ? (
                    <span className="flex items-center justify-center">
                      <FileText className="h-4 w-4 mr-2" />
                      {file.name}
                    </span>
                  ) : (
                    'Click to upload PDF or Word document'
                  )}
                </p>
              </label>
            </div>
          </div>

          {/* User Message */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Request (Optional)
            </label>
            <textarea
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              placeholder="e.g., 'Create a presentation' or leave blank for automatic processing"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
            />
          </div>

          {/* Generate Button */}
          <button
            onClick={generatePresentation}
            disabled={!file || isProcessing}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isProcessing ? (
              <>
                <Loader className="h-4 w-4 mr-2 animate-spin" />
                Generating Presentation...
              </>
            ) : (
              'Generate PowerPoint'
            )}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Results Display */}
        {results && results.response_data.status === 'completed' && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                <h3 className="text-lg font-semibold text-green-800">
                  Presentation Generated Successfully!
                </h3>
              </div>
              <button
                onClick={downloadPowerPoint}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center"
              >
                <Download className="h-4 w-4 mr-2" />
                Download PowerPoint
              </button>
            </div>

            {/* Processing Info */}
            <div className="bg-white rounded-lg p-4 mb-4">
              <h4 className="font-medium text-gray-900 mb-2">Processing Details:</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Presentation Type:</span>
                  <span className="ml-2 text-gray-600">
                    {results.response_data.processing_info?.presentation_type?.replace('_', ' ')}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Target Slides:</span>
                  <span className="ml-2 text-gray-600">
                    {results.response_data.processing_info?.target_slides}
                  </span>
                </div>
                <div>
                  <span className="font-medium">File Type:</span>
                  <span className="ml-2 text-gray-600">
                    {results.response_data.processing_info?.file_type?.toUpperCase()}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Session ID:</span>
                  <span className="ml-2 text-gray-600 font-mono text-xs">
                    {results.response_data.session_id}
                  </span>
                </div>
              </div>
            </div>

            {/* Pipeline Info */}
            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Processing Pipeline:</h4>
              <div className="flex flex-wrap gap-2">
                {results.response_data.pipeline_info?.map((agent, index) => (
                  <span
                    key={index}
                    className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs"
                  >
                    {agent}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Reset Button */}
        {(results || error) && (
          <div className="text-center">
            <button
              onClick={resetTest}
              className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700"
            >
              Start New Test
            </button>
          </div>
        )}

        {/* Configuration Info */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-6">
          <h4 className="font-medium text-yellow-800 mb-2">Configuration:</h4>
          <div className="text-sm text-yellow-700">
            <p><strong>PowerPoint Generation:</strong> {API_CONFIG.PPT_GENERATION_API}</p>
            <p className="mt-2 text-xs">
              Files are processed directly by the PowerPoint service.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;