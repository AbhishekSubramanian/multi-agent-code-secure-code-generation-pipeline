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

  // Agent pipeline state - tracks real backend status
  const [pipelineState, setPipelineState] = useState({
    codeGeneration: { status: 'pending', output: null, attempts: 0, message: '' },
    syntaxCheck: { status: 'pending', output: null, attempts: 0, message: '' },
    hallucinationCheck: { status: 'pending', output: null, attempts: 0, message: '' },
    codeReview: { status: 'pending', output: null, attempts: 0, message: '' }
  });

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState(null);
  const [modalTitle, setModalTitle] = useState('');

  useEffect(() => {
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

  const resetPipelineState = () => {
    setPipelineState({
      codeGeneration: { status: 'pending', output: null, attempts: 0, message: '' },
      syntaxCheck: { status: 'pending', output: null, attempts: 0, message: '' },
      hallucinationCheck: { status: 'pending', output: null, attempts: 0, message: '' },
      codeReview: { status: 'pending', output: null, attempts: 0, message: '' }
    });
  };

  const handleGenerate = async () => {
    if (!request.trim()) {
      alert('Please enter a code generation request');
      return;
    }

    setLoading(true);
    setResult(null);
    resetPipelineState();

    // Update to running state immediately
    setPipelineState(prev => ({
      ...prev,
      codeGeneration: { ...prev.codeGeneration, status: 'running', message: 'Generating code...' }
    }));

    try {
      const response = await axios.post('/api/generate', {
        request: request,
        enable_review: enableReview
      });

      // Extract actual attempt counts from metadata
      const metadata = response.data.metadata || {};
      const genAttempts = metadata.attempts?.generation || metadata.generation_attempts || 1;
      const syntaxAttempts = metadata.attempts?.syntax_fix || metadata.syntax_fix_attempts || 0;
      const hallAttempts = metadata.attempts?.hallucination_fix || metadata.hallucination_fix_attempts || 0;

      // Update pipeline with actual backend results
      setPipelineState({
        codeGeneration: {
          status: 'completed',
          output: response.data.code,
          attempts: genAttempts,
          message: `Generated successfully in ${genAttempts} attempt(s)`
        },
        syntaxCheck: {
          status: 'completed',
          output: response.data.validation?.syntax || { status: 'SYNTAX_VALID' },
          attempts: syntaxAttempts,
          message: syntaxAttempts > 0 ? `Fixed ${syntaxAttempts} syntax issue(s)` : 'Syntax validated'
        },
        hallucinationCheck: {
          status: 'completed',
          output: response.data.validation?.hallucination || { status: 'VERIFIED' },
          attempts: hallAttempts,
          message: hallAttempts > 0 ? `Fixed ${hallAttempts} hallucination(s)` : 'All imports verified'
        },
        codeReview: enableReview ? {
          status: 'completed',
          output: response.data.review_details || response.data.review || null,
          attempts: 1,
          message: response.data.review_details?.score
            ? `Review complete - Score: ${response.data.review_details.score}/10`
            : 'Review completed'
        } : {
          status: 'skipped',
          output: null,
          attempts: 0,
          message: 'Review disabled'
        }
      });

      setResult(response.data);
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.message;
      const errorDetails = error.response?.data?.error_details || error.response?.data?.errors || [];

      // Determine which stage failed
      const failedStage = error.response?.data?.failed_stage || 'code_generation';

      setPipelineState(prev => {
        const newState = { ...prev };

        // Mark stages as completed up to the failure point
        if (failedStage === 'code_generation') {
          newState.codeGeneration.status = 'failed';
          newState.codeGeneration.message = errorMsg;
          newState.codeGeneration.output = { error: errorMsg, details: errorDetails };
        } else {
          newState.codeGeneration.status = 'completed';
          newState.codeGeneration.message = 'Generated';

          if (failedStage === 'syntax_validation') {
            newState.syntaxCheck.status = 'failed';
            newState.syntaxCheck.message = errorMsg;
            newState.syntaxCheck.output = { error: errorMsg, details: errorDetails };
          } else {
            newState.syntaxCheck.status = 'completed';
            newState.syntaxCheck.message = 'Validated';

            if (failedStage === 'hallucination_detection') {
              newState.hallucinationCheck.status = 'failed';
              newState.hallucinationCheck.message = errorMsg;
              newState.hallucinationCheck.output = { error: errorMsg, details: errorDetails };
            } else {
              newState.hallucinationCheck.status = 'completed';
              newState.hallucinationCheck.message = 'Verified';

              if (failedStage === 'code_review' || failedStage === 'review') {
                newState.codeReview.status = 'failed';
                newState.codeReview.message = errorMsg;
                newState.codeReview.output = { error: errorMsg, details: errorDetails };
              }
            }
          }
        }

        return newState;
      });

      setResult({
        status: 'error',
        error: errorMsg,
        errors: errorDetails,
        failed_stage: failedStage
      });
    } finally {
      setLoading(false);
    }
  };

  const loadExample = (example) => {
    setRequest(example.request);
    setResult(null);
    resetPipelineState();
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    const button = document.activeElement;
    if (button && button.tagName === 'BUTTON') {
      const originalText = button.textContent;
      button.textContent = 'Copied!';
      setTimeout(() => {
        button.textContent = originalText;
      }, 2000);
    }
  };

  const openModal = (title, content, stageName) => {
    setModalTitle(title);
    setModalContent({ content, stageName });
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalContent(null);
    setModalTitle('');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <span className="status-icon success">✓</span>;
      case 'running':
        return <span className="status-icon running">⟳</span>;
      case 'failed':
        return <span className="status-icon failed">✕</span>;
      case 'skipped':
        return <span className="status-icon skipped">−</span>;
      default:
        return <span className="status-icon pending">○</span>;
    }
  };

  const renderModalContent = () => {
    if (!modalContent) return null;

    const { content, stageName } = modalContent;
    const stageData = pipelineState[stageName];

    return (
      <div className="modal-body">
        <div className="modal-section">
          <h4 className="modal-section-title">Status</h4>
          <div className="modal-status-row">
            {getStatusIcon(stageData.status)}
            <span className="modal-status-text">{stageData.message || stageData.status}</span>
          </div>
          {stageData.attempts > 0 && (
            <p className="modal-meta">Attempts: {stageData.attempts}</p>
          )}
        </div>

        {stageData.output && (
          <div className="modal-section">
            <h4 className="modal-section-title">Details</h4>
            {stageData.output.error ? (
              <div className="modal-error">
                <p className="modal-error-message">{stageData.output.error}</p>
                {stageData.output.details && stageData.output.details.length > 0 && (
                  <ul className="modal-error-list">
                    {stageData.output.details.map((detail, idx) => (
                      <li key={idx}>{detail}</li>
                    ))}
                  </ul>
                )}
              </div>
            ) : stageName === 'codeReview' && stageData.output.raw_review ? (
              <div className="modal-review">
                <pre className="modal-review-text">{stageData.output.raw_review}</pre>
              </div>
            ) : stageName === 'codeGeneration' && typeof stageData.output === 'string' ? (
              <div className="modal-code-preview">
                <pre><code>{stageData.output.substring(0, 500)}{stageData.output.length > 500 ? '...' : ''}</code></pre>
              </div>
            ) : (
              <div className="modal-output">
                <pre>{JSON.stringify(stageData.output, null, 2)}</pre>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="header-title">
              <h1 className="title">AgentLab</h1>
              <p className="subtitle">Secure Multi-Agent Code Generation System</p>
            </div>
            {config && (
              <div className="config-info">
                <div className="config-item">
                  <span className="config-label">Provider</span>
                  <span className="config-value">{config.provider === 'ollama' ? 'Ollama' : 'Claude'}</span>
                </div>
                <div className="config-item">
                  <span className="config-label">Model</span>
                  <span className="config-value">{config.model}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="container main-content">
        <div className="layout">
          {/* Left Panel - Input */}
          <div className="input-panel">
            <div className="card">
              <h2 className="card-title">Code Request</h2>

              <textarea
                className="input-textarea"
                value={request}
                onChange={(e) => setRequest(e.target.value)}
                placeholder="Describe the code you want to generate...&#10;&#10;Example: Create a function to validate email addresses using regex"
                rows={8}
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
                    'Generate Code'
                  )}
                </button>
              </div>
            </div>

            {/* Examples */}
            {examples.length > 0 && (
              <div className="card">
                <h3 className="card-subtitle">Example Requests</h3>
                <div className="examples-list">
                  {examples.map((example) => (
                    <button
                      key={example.id}
                      className="example-item"
                      onClick={() => loadExample(example)}
                      disabled={loading}
                    >
                      <span className="example-title">{example.title}</span>
                      <span className="example-desc">{example.request}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Pipeline & Output */}
          <div className="output-panel">
            {(loading || result) ? (
              <>
                {/* Pipeline Status */}
                <div className="card pipeline-card">
                  <h2 className="card-title">Pipeline Status</h2>

                  <div className="pipeline-stages">
                    {/* Code Generation */}
                    <div
                      className={`stage-item ${pipelineState.codeGeneration.status}`}
                      onClick={() => pipelineState.codeGeneration.output && openModal('Code Generation', pipelineState.codeGeneration.output, 'codeGeneration')}
                      style={{ cursor: pipelineState.codeGeneration.output ? 'pointer' : 'default' }}
                    >
                      <div className="stage-header">
                        <div className="stage-info">
                          {getStatusIcon(pipelineState.codeGeneration.status)}
                          <div className="stage-details">
                            <span className="stage-name">Code Generation</span>
                            <span className="stage-meta">{pipelineState.codeGeneration.message || pipelineState.codeGeneration.status}</span>
                          </div>
                        </div>
                        {pipelineState.codeGeneration.output && (
                          <button className="view-btn" onClick={(e) => { e.stopPropagation(); openModal('Code Generation', pipelineState.codeGeneration.output, 'codeGeneration'); }}>
                            View
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Syntax Check */}
                    <div
                      className={`stage-item ${pipelineState.syntaxCheck.status}`}
                      onClick={() => pipelineState.syntaxCheck.output && openModal('Syntax Validation', pipelineState.syntaxCheck.output, 'syntaxCheck')}
                      style={{ cursor: pipelineState.syntaxCheck.output ? 'pointer' : 'default' }}
                    >
                      <div className="stage-header">
                        <div className="stage-info">
                          {getStatusIcon(pipelineState.syntaxCheck.status)}
                          <div className="stage-details">
                            <span className="stage-name">Syntax Validation</span>
                            <span className="stage-meta">{pipelineState.syntaxCheck.message || pipelineState.syntaxCheck.status}</span>
                          </div>
                        </div>
                        {pipelineState.syntaxCheck.output && (
                          <button className="view-btn" onClick={(e) => { e.stopPropagation(); openModal('Syntax Validation', pipelineState.syntaxCheck.output, 'syntaxCheck'); }}>
                            View
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Hallucination Check */}
                    <div
                      className={`stage-item ${pipelineState.hallucinationCheck.status}`}
                      onClick={() => pipelineState.hallucinationCheck.output && openModal('Hallucination Detection', pipelineState.hallucinationCheck.output, 'hallucinationCheck')}
                      style={{ cursor: pipelineState.hallucinationCheck.output ? 'pointer' : 'default' }}
                    >
                      <div className="stage-header">
                        <div className="stage-info">
                          {getStatusIcon(pipelineState.hallucinationCheck.status)}
                          <div className="stage-details">
                            <span className="stage-name">Hallucination Detection</span>
                            <span className="stage-meta">{pipelineState.hallucinationCheck.message || pipelineState.hallucinationCheck.status}</span>
                          </div>
                        </div>
                        {pipelineState.hallucinationCheck.output && (
                          <button className="view-btn" onClick={(e) => { e.stopPropagation(); openModal('Hallucination Detection', pipelineState.hallucinationCheck.output, 'hallucinationCheck'); }}>
                            View
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Code Review */}
                    {enableReview && (
                      <div
                        className={`stage-item ${pipelineState.codeReview.status}`}
                        onClick={() => pipelineState.codeReview.output && openModal('Code Review', pipelineState.codeReview.output, 'codeReview')}
                        style={{ cursor: pipelineState.codeReview.output ? 'pointer' : 'default' }}
                      >
                        <div className="stage-header">
                          <div className="stage-info">
                            {getStatusIcon(pipelineState.codeReview.status)}
                            <div className="stage-details">
                              <span className="stage-name">Code Review</span>
                              <span className="stage-meta">{pipelineState.codeReview.message || pipelineState.codeReview.status}</span>
                            </div>
                          </div>
                          {pipelineState.codeReview.output && (
                            <button className="view-btn" onClick={(e) => { e.stopPropagation(); openModal('Code Review', pipelineState.codeReview.output, 'codeReview'); }}>
                              View
                            </button>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Generated Code */}
                {result?.status === 'success' && result.code && (
                  <div className="card code-card">
                    <div className="code-header">
                      <h2 className="card-title">Generated Code</h2>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => copyToClipboard(result.code)}
                      >
                        Copy Code
                      </button>
                    </div>
                    <div className="code-wrapper">
                      <pre className="code-block"><code>{result.code}</code></pre>
                    </div>
                  </div>
                )}

                {/* Error Display */}
                {result?.status === 'error' && (
                  <div className="card error-card">
                    <h2 className="card-title error-title">Generation Failed</h2>
                    <div className="error-content">
                      <p className="error-message">{result.error}</p>
                      {result.errors && result.errors.length > 0 && (
                        <div className="error-list">
                          <h4>Error Details:</h4>
                          <ul>
                            {result.errors.map((err, index) => (
                              <li key={index}>{err}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {result.failed_stage && (
                        <p className="error-stage">Failed at: {result.failed_stage.replace('_', ' ')}</p>
                      )}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="card placeholder-card">
                <div className="placeholder-content">
                  <svg className="placeholder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <h3>Ready to Generate Code</h3>
                  <p>Enter your request or select an example to begin</p>
                  <div className="feature-grid">
                    <div className="feature-item">
                      <div className="feature-icon">✓</div>
                      <span>AI-Powered Generation</span>
                    </div>
                    <div className="feature-item">
                      <div className="feature-icon">✓</div>
                      <span>Syntax Validation</span>
                    </div>
                    <div className="feature-item">
                      <div className="feature-icon">✓</div>
                      <span>Hallucination Detection</span>
                    </div>
                    <div className="feature-item">
                      <div className="feature-icon">✓</div>
                      <span>Quality Review</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">{modalTitle}</h3>
              <button className="modal-close" onClick={closeModal}>✕</button>
            </div>
            {renderModalContent()}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
