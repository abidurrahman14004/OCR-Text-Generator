// src/App.jsx
import React, { useState } from 'react';
import ImageUploader from './components/ImageUploader';
import ImagePreview from './components/ImagePreview';
import TextOutput from './components/TextOutput';
import LoadingSpinner from './components/LoadingSpinner';

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

const App = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [originalText, setOriginalText] = useState('');
  const [ocrStats, setOcrStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleImageSelect = (imageFile) => {
    setSelectedImage(imageFile);
    setExtractedText('');
    setOriginalText('');
    setOcrStats(null);
    setError('');
  };

  const handleTextExtraction = async (imageFile) => {
    setIsLoading(true);
    setError('');
    
    try {
      console.log('🚀 Starting OCR process...');
      console.log('📤 File:', imageFile.name, 'Size:', imageFile.size, 'Type:', imageFile.type);
      
      const formData = new FormData();
      formData.append('file', imageFile);

      const response = await fetch('http://127.0.0.1:5000/api/extract-text', {
        method: 'POST',
        body: formData,
      });

      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('📥 API Response:', result);
      
      if (result.success) {
        const extractedText = result.extracted_text || result.corrected_text || '';
        
        if (extractedText.trim()) {
          setExtractedText(extractedText);
          setOriginalText(result.original_text || result.raw_text || '');
          setOcrStats(result.statistics || null);
          console.log('✅ Text extracted successfully!');
        } else {
          setError('No text found in the image. Please try a clearer image with more text.');
        }
      } else {
        setError(result.error || 'Failed to extract text from image');
      }
      
    } catch (error) {
      console.error('❌ Error details:', error);
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        setError('Cannot connect to OCR service. Make sure the backend server is running on http://127.0.0.1:5000');
      } else {
        setError(`Failed to process image: ${error.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadText = () => {
    if (!extractedText.trim()) {
      alert('No text to download!');
      return;
    }

    try {
      // Create blob with extracted text
      const blob = new Blob([extractedText], { type: 'text/plain' });
      
      // Create download URL
      const url = window.URL.createObjectURL(blob);
      
      // Create temporary download link
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename with timestamp
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      link.download = `extracted-text-${timestamp}.txt`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('📥 Text downloaded successfully');
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download text. Please try copying the text instead.');
    }
  };

  const handleCopyText = async () => {
    if (!extractedText.trim()) {
      alert('No text to copy!');
      return;
    }

    try {
      await navigator.clipboard.writeText(extractedText);
      alert('Text copied to clipboard!');
      console.log('📋 Text copied to clipboard');
    } catch (error) {
      console.error('Copy error:', error);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = extractedText;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      alert('Text copied to clipboard!');
    }
  };

  const handleClearAll = () => {
    setSelectedImage(null);
    setExtractedText('');
    setOriginalText('');
    setOcrStats(null);
    setError('');
  };

  return (
    <div className="min-vh-100 bg-light">
      {/* Navigation */}
      <nav className="navbar navbar-dark shadow-sm">
        <div className="container">
          <span className="navbar-brand mb-0 h1">
            <i className="bi bi-magic me-3"></i>
            Handwriting to Text Converter
          </span>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-lg-10">
            {/* Header */}
            <div className="text-center mb-5">
              <h1 className="main-title">
                Transform Your Handwriting
              </h1>
              <p className="subtitle">
                Upload a JPG image of your handwritten text and convert it to editable digital text with AI-powered OCR technology
              </p>
            </div>

            {/* Error Alert */}
            {error && (
              <div className="alert alert-danger alert-dismissible fade show" role="alert">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                {error}
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setError('')}
                ></button>
              </div>
            )}

            {/* Main Content Area */}
            <div className="row g-4">
              {/* Left Column - Image Upload and Preview */}
              <div className="col-md-6">
                <div className="card h-100 shadow-sm">
                  <div className="card-header bg-primary text-white">
                    <h5 className="card-title mb-0">
                      <i className="bi bi-cloud-upload me-2"></i>
                      Upload Image
                    </h5>
                  </div>
                  <div className="card-body">
                    <ImageUploader 
                      onImageSelect={handleImageSelect}
                      onTextExtraction={handleTextExtraction}
                      disabled={isLoading}
                    />
                    
                    {selectedImage && (
                      <div className="mt-3">
                        <ImagePreview 
                          imageFile={selectedImage}
                          onExtractText={() => handleTextExtraction(selectedImage)}
                          isLoading={isLoading}
                        />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column - Text Output */}
              <div className="col-md-6">
                <div className="card h-100 shadow-sm">
                  <div className="card-header bg-success text-white d-flex justify-content-between align-items-center">
                    <h5 className="card-title mb-0">
                      <i className="bi bi-file-text me-2"></i>
                      Extracted Text
                    </h5>
                    
                    {/* Download and Copy Buttons */}
                    {extractedText && (
                      <div className="btn-group">
                        <button 
                          className="btn btn-sm btn-outline-light"
                          onClick={handleCopyText}
                          title="Copy to clipboard"
                        >
                          <i className="bi bi-clipboard"></i>
                        </button>
                        <button 
                          className="btn btn-sm btn-outline-light"
                          onClick={handleDownloadText}
                          title="Download as text file"
                        >
                          <i className="bi bi-download"></i>
                        </button>
                      </div>
                    )}
                  </div>
                  <div className="card-body">
                    {isLoading ? (
                      <div className="text-center">
                        <LoadingSpinner />
                        <p className="mt-3 text-muted">
                          <i className="bi bi-gear-fill me-2"></i>
                          Processing image with AI OCR...
                        </p>
                      </div>
                    ) : extractedText ? (
                      <>
                        <TextOutput 
                          text={extractedText}
                          onTextChange={setExtractedText}
                        />
                        
                        {/* Text Actions */}
                        <div className="mt-3 d-flex gap-2">
                          <button 
                            className="btn btn-sm btn-outline-primary"
                            onClick={handleCopyText}
                          >
                            <i className="bi bi-clipboard me-1"></i>
                            Copy Text
                          </button>
                          <button 
                            className="btn btn-sm btn-outline-success"
                            onClick={handleDownloadText}
                          >
                            <i className="bi bi-download me-1"></i>
                            Download
                          </button>
                        </div>
                        
                        {/* Show OCR confidence and stats */}
                        {ocrStats && (
                          <div className="mt-3 p-2 bg-light rounded">
                            <small className="text-muted">
                              <strong>OCR Results:</strong><br/>
                              • Words: {ocrStats.corrected_word_count || ocrStats.raw_word_count || 'N/A'}<br/>
                              • Characters: {extractedText.length}<br/>
                              • Corrections: {ocrStats.corrections_applied || 0}<br/>
                              • Quality: {ocrStats.quality_assessment || 'Good'}
                            </small>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-center text-muted py-5">
                        <i className="bi bi-file-text display-4 mb-3"></i>
                        <h6>No Text Extracted Yet</h6>
                        <p>Upload an image and extract text to see the results here.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            {(selectedImage || extractedText) && (
              <div className="text-center mt-4">
                <button 
                  className="btn btn-outline-secondary me-2"
                  onClick={handleClearAll}
                >
                  <i className="bi bi-arrow-clockwise me-2"></i>
                  Start Over
                </button>
                
                {/* Show original text button if corrections were made */}
                {originalText && originalText !== extractedText && (
                  <button 
                    className="btn btn-outline-info"
                    onClick={() => {
                      const temp = extractedText;
                      setExtractedText(originalText);
                      setOriginalText(temp);
                    }}
                  >
                    <i className="bi bi-arrow-left-right me-2"></i>
                    Toggle Original/Corrected
                  </button>
                )}
              </div>
            )}

            {/* Instructions */}
            <div className="card mt-4 border-info">
              <div className="card-header bg-info text-white">
                <h6 className="mb-0">
                  <i className="bi bi-info-circle me-2"></i>
                  How to Use
                </h6>
              </div>
              <div className="card-body">
                <ol className="mb-0">
                  <li>Click "Choose File" to select a JPG image of your handwritten text</li>
                  <li>Preview your image to ensure it's clear and readable</li>
                  <li>Click "Extract Text" to convert handwriting to digital text</li>
                  <li>AI will automatically correct common OCR errors</li>
                  <li>Edit the extracted text if needed</li>
                  <li>Copy or download the final text using the buttons</li>
                </ol>
                
                <div className="mt-3 p-2 bg-light rounded">
                  <small>
                    <strong>✨ Features:</strong> Intelligent error correction, spell checking, 
                    one-click copy, automatic download, and text statistics.
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;