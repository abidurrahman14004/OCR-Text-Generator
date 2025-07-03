// components/TextOutput.js
import React, { useState, useRef } from 'react';

const TextOutput = ({ text, onTextChange }) => {
  const [isCopied, setIsCopied] = useState(false);
  const textAreaRef = useRef(null);

  const handleCopyText = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      // Fallback for older browsers
      textAreaRef.current?.select();
      document.execCommand('copy');
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  const handleDownloadText = () => {
    const element = document.createElement('a');
    const file = new Blob([text], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `extracted-text-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    URL.revokeObjectURL(element.href);
  };

  const handleClearText = () => {
    onTextChange('');
  };

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const charCount = text.length;
  const lineCount = text.split('\n').length;

  return (
    <div className="text-output-container">
      {text ? (
        <>
          {/* Text Statistics */}
          <div className="row mb-3">
            <div className="col-4 text-center">
              <div className="bg-light rounded p-2">
                <div className="fw-bold text-primary">{wordCount}</div>
                <small className="text-muted">Words</small>
              </div>
            </div>
            <div className="col-4 text-center">
              <div className="bg-light rounded p-2">
                <div className="fw-bold text-success">{charCount}</div>
                <small className="text-muted">Characters</small>
              </div>
            </div>
            <div className="col-4 text-center">
              <div className="bg-light rounded p-2">
                <div className="fw-bold text-info">{lineCount}</div>
                <small className="text-muted">Lines</small>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="d-flex gap-2 mb-3 flex-wrap">
            <button
              type="button"
              className={`btn btn-outline-primary btn-sm ${isCopied ? 'btn-success' : ''}`}
              onClick={handleCopyText}
              disabled={!text.trim()}
            >
              <i className={`bi ${isCopied ? 'bi-check2' : 'bi-clipboard'} me-1`}></i>
              {isCopied ? 'Copied!' : 'Copy Text'}
            </button>

            <button
              type="button"
              className="btn btn-outline-success btn-sm"
              onClick={handleDownloadText}
              disabled={!text.trim()}
            >
              <i className="bi bi-download me-1"></i>
              Download
            </button>

            <button
              type="button"
              className="btn btn-outline-danger btn-sm"
              onClick={handleClearText}
              disabled={!text.trim()}
            >
              <i className="bi bi-trash me-1"></i>
              Clear
            </button>
          </div>

          {/* Editable Text Area */}
          <div className="form-group">
            <label htmlFor="extractedText" className="form-label fw-bold">
              <i className="bi bi-pencil-square me-2"></i>
              Extracted Text (Editable)
            </label>
            <textarea
              ref={textAreaRef}
              id="extractedText"
              className="form-control"
              value={text}
              onChange={(e) => onTextChange(e.target.value)}
              placeholder="Extracted text will appear here..."
              rows={12}
              style={{
                fontFamily: 'Georgia, serif',
                fontSize: '14px',
                lineHeight: '1.6',
                resize: 'vertical'
              }}
            />
            <div className="form-text">
              You can edit the extracted text above to correct any OCR errors.
            </div>
          </div>

          {/* Text Formatting Options */}
          <div className="mt-3">
            <div className="card">
              <div className="card-header">
                <h6 className="mb-0">
                  <i className="bi bi-tools me-2"></i>
                  Quick Actions
                </h6>
              </div>
              <div className="card-body">
                <div className="d-flex gap-2 flex-wrap">
                  <button
                    type="button"
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() => onTextChange(text.toUpperCase())}
                  >
                    <i className="bi bi-type me-1"></i>
                    UPPERCASE
                  </button>
                  
                  <button
                    type="button"
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() => onTextChange(text.toLowerCase())}
                  >
                    <i className="bi bi-type me-1"></i>
                    lowercase
                  </button>
                  
                  <button
                    type="button"
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() => onTextChange(
                      text.split('\n')
                        .map(line => line.trim())
                        .filter(line => line.length > 0)
                        .join('\n')
                    )}
                  >
                    <i className="bi bi-justify me-1"></i>
                    Remove Extra Spaces
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : (
        /* Empty State */
        <div className="text-center py-5">
          <div className="text-muted mb-3">
            <i className="bi bi-file-text" style={{ fontSize: '4rem' }}></i>
          </div>
          <h5 className="text-muted">No Text Extracted Yet</h5>
          <p className="text-muted mb-0">
            Upload an image and extract text to see the results here.
          </p>
        </div>
      )}
    </div>
  );
};

export default TextOutput;