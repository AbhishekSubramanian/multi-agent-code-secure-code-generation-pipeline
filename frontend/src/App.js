import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [request, setRequest] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState(null);
  const [examples, setExamples] = useState([]);
  const [enableReview, setEnableReview] = useState(true);
  const [currentStage, setCurrentStage] = useState('');

  useEffect(() => {
    // Load configuration and examples on mount
    loadConfig();
    loadExamples();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await axios.get('/api/config');
      setConfig(response.data);
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const loadExamples = async () => {
    try {
      const response = await axios.get('/api/examples');
      setExamples(response.data);
    } catch (error) {
      console.error('Error loading examples:', error);
    }
  };

  const handleGenerate = async () => {
    if (!request.trim()) {
      alert('Please enter a code generation request');
      return;
    }

    setLoading(true);
    setResult(null);
    setCurrentStage('Initializing...');

    try {
      const response = await axios.post('/api/generate', {
        request: request,
        enable_review: enableReview
      });

      setResult(response.data);
      setCurrentStage('Completed');
    } catch (error) {
      setResult({
        status: 'error',
        error: error.response?.data?.error || error.message
      });
      setCurrentStage('Failed');
    } finally {
      setLoading(false);
    }
  };

  const loadExample = (example) => {
    setRequest(example.request);
    setResult(null);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Code copied to clipboard!');
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <h1 className="title">🤖 Multi-Agent Code Generator</h1>
          <p className="subtitle">
            AI-Powered Code Generation with Syntax Validation, Hallucination Detection & Code Review
          </p>
          {config && (
            <div className="config-badge">
              <span className="provider-badge">
                {config.provider === 'ollama' ? '🖥️ Ollama' : '☁️ Claude'}
              </span>
              <span className="model-badge">{config.model}</span>
            </div>
          )}
        </div>
      </header>

      <div className="container main-content">
        <div className="layout">
          {/* Left Panel - Input */}
          <div className="input-panel">
            <div className="card">
              <h2 className="card-title">📝 Code Request</h2>

              <textarea
                className="input-textarea"
                value={request}
                onChange={(e) => setRequest(e.target.value)}
                placeholder="Describe the code you want to generate... e.g., 'Create a function to validate email addresses using regex'"
                rows={6}
                disabled={loading}
              />

              <div className="controls">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={enableReview}
                    onChange={(e) => setEnableReview(e.target.checked)}
                    disabled={loading}
                  />
                  <span>Enable Code Review</span>
                </label>

                <button
                  className="btn btn-primary"
                  onClick={handleGenerate}
                  disabled={loading || !request.trim()}
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Generating...
                    </>
                  ) : (
                    <>⚡ Generate Code</>
                  )}
                </button>
              </div>

              {loading && currentStage && (
                <div className="status-indicator">
                  <div className="status-pulse"></div>
                  <span>{currentStage}</span>
                </div>
              )}
            </div>

            {/* Examples */}
            <div className="card examples-card">
              <h3 className="card-subtitle">💡 Example Requests</h3>
              <div className="examples-grid">
                {examples.map((example) => (
                  <button
                    key={example.id}
                    className="example-btn"
                    onClick={() => loadExample(example)}
                    disabled={loading}
                  >
                    <span className="example-title">{example.title}</span>
                    <span className="example-text">{example.request}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Panel - Output */}
          <div className="output-panel">
            {result ? (
              <div className="card">
                {result.status === 'success' ? (
                  <>
                    {/* Generated Code */}
                    <div className="result-section">
                      <div className="section-header">
                        <h2 className="card-title">✅ Generated Code</h2>
                        <button
                          className="btn btn-secondary"
                          onClick={() => copyToClipboard(result.final_code)}
                        >
                          📋 Copy
                        </button>
                      </div>
                      <pre className="code-block">
                        <code>{result.final_code}</code>
                      </pre>
                    </div>

                    {/* Pipeline Status */}
                    <div className="result-section">
                      <h3 className="section-title">🔄 Pipeline Status</h3>
                      <div className="pipeline-status">
                        <div className="status-item success">
                          <span className="status-icon">✓</span>
                          <span>Code Generation</span>
                        </div>
                        <div className="status-item success">
                          <span className="status-icon">✓</span>
                          <span>Syntax Check</span>
                        </div>
                        <div className="status-item success">
                          <span className="status-icon">✓</span>
                          <span>Hallucination Detection</span>
                        </div>
                        {enableReview && (
                          <div className="status-item success">
                            <span className="status-icon">✓</span>
                            <span>Code Review</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Code Review */}
                    {result.review && (
                      <div className="result-section">
                        <h3 className="section-title">📊 Code Review</h3>
                        <div className="review-content">
                          <pre className="review-text">{result.review}</pre>
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="metadata">
                      <span>Request ID: {result.request_id}</span>
                      <span>Generation Attempts: {result.metadata?.attempts?.generation || 0}</span>
                    </div>
                  </>
                ) : (
                  <>
                    {/* Error Display */}
                    <div className="error-section">
                      <h2 className="card-title error-title">❌ Generation Failed</h2>
                      <div className="error-content">
                        <p className="error-message">{result.error}</p>

                        {result.error_details && result.error_details.length > 0 && (
                          <div className="error-details">
                            <h4>Error Details:</h4>
                            <ul>
                              {result.error_details.map((detail, index) => (
                                <li key={index}>{detail}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {result.failed_stage && (
                          <div className="metadata">
                            <span>Failed at: {result.failed_stage}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="card placeholder-card">
                <div className="placeholder-content">
                  <div className="placeholder-icon">🚀</div>
                  <h3>Ready to Generate Code</h3>
                  <p>Enter your request or select an example to get started</p>
                  <div className="feature-list">
                    <div className="feature-item">
                      <span className="feature-icon">✨</span>
                      <span>AI-Powered Code Generation</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-icon">🔍</span>
                      <span>Automatic Syntax Validation</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-icon">🛡️</span>
                      <span>Hallucination Detection</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-icon">📝</span>
                      <span>Code Quality Review</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
