// components/ImageUploader.js
import React, { useRef } from 'react';

const ImageUploader = ({ onImageSelect, onTextExtraction, disabled }) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file (JPG, PNG, etc.)');
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
      }

      onImageSelect(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    const files = Array.from(event.dataTransfer.files);
    const imageFile = files.find(file => file.type.startsWith('image/'));
    
    if (imageFile) {
      if (imageFile.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
      }
      onImageSelect(imageFile);
    } else {
      alert('Please drop a valid image file');
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="upload-container">
      {/* File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="d-none"
        disabled={disabled}
      />

      {/* Upload Area */}
      <div 
        className={`border-2 border-dashed rounded-3 p-4 text-center position-relative ${
          disabled ? 'border-secondary bg-light' : 'border-primary bg-light'
        }`}
        style={{ 
          minHeight: '200px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease',
          borderWidth: '2px',
          borderStyle: 'dashed'
        }}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={!disabled ? triggerFileInput : undefined}
      >
        <div className="d-flex flex-column align-items-center justify-content-center h-100">
          <div className={`mb-3 ${disabled ? 'text-secondary' : 'text-primary'}`}>
            <i className="bi bi-cloud-arrow-up" style={{ fontSize: '3rem' }}></i>
          </div>
          
          <h5 className={disabled ? 'text-secondary' : 'text-primary'}>
            {disabled ? 'Processing...' : 'Upload Your Handwritten Image'}
          </h5>
          
          <p className={`mb-3 ${disabled ? 'text-secondary' : 'text-muted'}`}>
            Drag and drop your JPG file here, or click to browse
          </p>
          
          <button 
            type="button"
            className={`btn ${disabled ? 'btn-secondary' : 'btn-primary'}`}
            disabled={disabled}
            onClick={(e) => {
              e.stopPropagation();
              triggerFileInput();
            }}
          >
            <i className="bi bi-folder2-open me-2"></i>
            Choose File
          </button>
          
          <small className="text-muted mt-2">
            Supported formats: JPG, PNG, GIF • Max size: 10MB
          </small>
        </div>
      </div>

      {/* Upload Tips */}
      <div className="mt-3">
        <div className="alert alert-info" role="alert">
          <i className="bi bi-lightbulb me-2"></i>
          <strong>Tips for better results:</strong>
          <ul className="mb-0 mt-2">
            <li>Ensure good lighting and clear handwriting</li>
            <li>Avoid shadows and glare on the paper</li>
            <li>Keep the image straight and well-focused</li>
            <li>Use high contrast (dark text on light background)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ImageUploader;