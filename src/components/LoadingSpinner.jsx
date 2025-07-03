// components/LoadingSpinner.js
import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="loading-spinner-container position-relative">
      <div className="text-center py-5">
        {/* Main Spinner */}
        <div className="mb-4">
          <div 
            className="spinner-border text-primary" 
            role="status" 
            style={{ width: '3rem', height: '3rem' }}
          >
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>

        {/* Loading Text */}
        <h5 className="text-primary mb-3">
          <i className="bi bi-magic me-2"></i>
          Processing Your Image
        </h5>

        <p className="text-muted mb-4">
          Our OCR technology is analyzing your handwritten text...
        </p>

        {/* Progress Steps */}
        <div className="row justify-content-center">
          <div className="col-md-8">
            <div className="card bg-light border-0">
              <div className="card-body py-3">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <small className="text-muted">Processing Steps:</small>
                  <div className="spinner-border spinner-border-sm text-secondary" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
                
                <div className="progress mb-2" style={{ height: '6px' }}>
                  <div 
                    className="progress-bar progress-bar-striped progress-bar-animated" 
                    role="progressbar" 
                    style={{ width: '60%' }}
                  ></div>
                </div>

                <div className="small text-start">
                  <div className="d-flex align-items-center mb-1">
                    <i className="bi bi-check-circle-fill text-success me-2"></i>
                    <span>Image loaded successfully</span>
                  </div>
                  <div className="d-flex align-items-center mb-1">
                    <i className="bi bi-check-circle-fill text-success me-2"></i>
                    <span>Image preprocessing completed</span>
                  </div>
                  <div className="d-flex align-items-center mb-1">
                    <div className="spinner-border spinner-border-sm text-primary me-2" style={{ width: '1rem', height: '1rem' }}>
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <span className="text-primary">Extracting text content...</span>
                  </div>
                  <div className="d-flex align-items-center text-muted">
                    <i className="bi bi-circle me-2"></i>
                    <span>Finalizing results</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading Tips */}
        <div className="mt-4">
          <div className="alert alert-info border-0" role="alert">
            <div className="d-flex align-items-start">
              <i className="bi bi-lightbulb-fill text-warning me-2 flex-shrink-0"></i>
              <div className="text-start">
                <strong>Did you know?</strong>
                <br />
                <small>
                  OCR accuracy improves with clear, well-lit images and legible handwriting. 
                  The processing time depends on image size and complexity.
                </small>
              </div>
            </div>
          </div>
        </div>

        {/* Estimated Time */}
        <div className="mt-3">
          <small className="text-muted d-flex align-items-center justify-content-center">
            <i className="bi bi-clock me-1"></i>
            Estimated time: 10-30 seconds
          </small>
        </div>
      </div>

      {/* Custom CSS for animations */}
      <style jsx>{`
        .loading-spinner-container::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(
            90deg,
            transparent,
            rgba(0, 123, 255, 0.1),
            transparent
          );
          animation: shimmer 2s infinite;
          z-index: -1;
        }
        
        @keyframes shimmer {
          0% { left: -100%; }
          100% { left: 100%; }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;