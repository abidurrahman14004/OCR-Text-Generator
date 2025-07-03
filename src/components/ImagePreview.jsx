// components/ImagePreview.js
import React, { useState, useEffect } from 'react';

const ImagePreview = ({ imageFile, onExtractText, isLoading }) => {
  const [imageUrl, setImageUrl] = useState(null);

  useEffect(() => {
    if (imageFile) {
      const url = URL.createObjectURL(imageFile);
      setImageUrl(url);

      // Cleanup URL when component unmounts or file changes
      return () => {
        URL.revokeObjectURL(url);
      };
    }
  }, [imageFile]);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!imageFile || !imageUrl) {
    return null;
  }

  return (
    <div className="image-preview-container">
      {/* Image Info Card */}
      <div className="card mb-3">
        <div className="card-header bg-light">
          <h6 className="mb-0">
            <i className="bi bi-image me-2"></i>
            Image Details
          </h6>
        </div>
        <div className="card-body py-2">
          <div className="row text-sm">
            <div className="col-6">
              <strong>Name:</strong>
              <br />
              <span className="text-muted" title={imageFile.name}>
                {imageFile.name.length > 20 
                  ? imageFile.name.substring(0, 20) + '...' 
                  : imageFile.name}
              </span>
            </div>
            <div className="col-6">
              <strong>Size:</strong>
              <br />
              <span className="text-muted">{formatFileSize(imageFile.size)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Image Preview */}
      <div className="card">
        <div className="card-header bg-light d-flex justify-content-between align-items-center">
          <h6 className="mb-0">
            <i className="bi bi-eye me-2"></i>
            Preview
          </h6>
          <div className="badge bg-primary">
            {imageFile.type}
          </div>
        </div>
        <div className="card-body p-0">
          <div className="text-center position-relative">
            <img
              src={imageUrl}
              alt="Handwritten text preview"
              className="img-fluid rounded-bottom"
              style={{
                maxHeight: '400px',
                width: '100%',
                objectFit: 'contain',
                backgroundColor: '#f8f9fa'
              }}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <div 
              className="alert alert-danger m-3" 
              style={{ display: 'none' }}
              role="alert"
            >
              <i className="bi bi-exclamation-triangle me-2"></i>
              Unable to preview this image format
            </div>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div className="d-grid gap-2 mt-3">
        <button
          type="button"
          className={`btn btn-success btn-lg ${isLoading ? 'disabled' : ''}`}
          onClick={onExtractText}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <div className="spinner-border spinner-border-sm me-2" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              Processing Image...
            </>
          ) : (
            <>
              <i className="bi bi-magic me-2"></i>
              Extract Text from Image
            </>
          )}
        </button>
      </div>

      {/* Image Guidelines */}
      <div className="mt-3">
        <div className="alert alert-warning" role="alert">
          <i className="bi bi-info-circle me-2"></i>
          <strong>Image Quality Check:</strong>
          <ul className="mb-0 mt-2 small">
            <li>✓ Text should be clearly visible</li>
            <li>✓ Good contrast between text and background</li>
            <li>✓ Image should be well-lit without shadows</li>
            <li>✓ Text should not be blurry or distorted</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ImagePreview;