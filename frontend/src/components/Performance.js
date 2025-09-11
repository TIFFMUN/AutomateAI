import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './Performance.css';

function Performance() {
  const navigate = useNavigate();
  const [isManagerView, setIsManagerView] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [directReports, setDirectReports] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [editingFeedback, setEditingFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentUserId, setCurrentUserId] = useState("manager001"); // Current user ID
  const [showAIAnalysis, setShowAIAnalysis] = useState(true); // Toggle for AI analysis visibility
  const [dropdownOpen, setDropdownOpen] = useState(false); // Custom dropdown state
  const [aiAssistantEnabled, setAiAssistantEnabled] = useState(true); // AI assistant toggle
  const [aiAnalysis, setAiAnalysis] = useState(null); // AI analysis data
  const [aiLoading, setAiLoading] = useState(false); // AI loading state
  const [realtimeSuggestions, setRealtimeSuggestions] = useState(null); // Real-time suggestions
  const [aiProcessingSteps, setAiProcessingSteps] = useState([]); // AI processing steps
  const [aiConfidence, setAiConfidence] = useState(null); // AI confidence score
  const [aiModelInfo, setAiModelInfo] = useState({ model: 'GPT-4', version: '2024-01-01' }); // AI model info
  const [aiStatus, setAiStatus] = useState('ready'); // AI status: ready, processing, error
  const [currentFeedbackIndex, setCurrentFeedbackIndex] = useState(0); // Carousel current index

  // Available users for testing
  const availableUsers = [
    { id: "manager001", name: "Sarah Johnson", role: "Manager" },
    { id: "employee001", name: "John Smith", role: "Employee" },
    { id: "employee002", name: "Emily Davis", role: "Employee" },
    { id: "employee003", name: "Michael Brown", role: "Employee" }
  ];

  useEffect(() => {
    loadUserProfile();
    if (isManagerView) {
      loadDirectReports();
      loadManagerFeedbacks();
    } else {
      loadEmployeeFeedbacks();
    }
  }, [isManagerView, currentUserId]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownOpen && !event.target.closest('.custom-dropdown')) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [dropdownOpen]);

  const loadUserProfile = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/user/${currentUserId}/profile`);
      if (response.ok) {
        const profile = await response.json();
        setUserProfile(profile);
      }
    } catch (err) {
      console.error('Error loading user profile:', err);
    }
  };

  const loadDirectReports = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/user/${currentUserId}/direct-reports`);
      if (response.ok) {
        const reports = await response.json();
        setDirectReports(Array.isArray(reports) ? reports : []);
      } else {
        console.error('Failed to load direct reports');
        setDirectReports([]);
      }
    } catch (err) {
      console.error('Error loading direct reports:', err);
      setDirectReports([]);
    }
  };

  const loadEmployeeFeedbacks = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/user/${currentUserId}/feedback`);
      if (response.ok) {
        const feedbacks = await response.json();
        setFeedbacks(Array.isArray(feedbacks) ? feedbacks : []);
      } else {
        console.error('Failed to load employee feedbacks');
        setFeedbacks([]);
      }
    } catch (err) {
      console.error('Error loading employee feedbacks:', err);
      setFeedbacks([]);
    }
  };

  const loadManagerFeedbacks = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/manager/${currentUserId}/feedback`);
      if (response.ok) {
        const feedbacks = await response.json();
        setFeedbacks(Array.isArray(feedbacks) ? feedbacks : []);
      } else {
        console.error('Failed to load manager feedbacks');
        setFeedbacks([]);
      }
    } catch (err) {
      console.error('Error loading manager feedbacks:', err);
      setFeedbacks([]);
    }
  };

  const handleUserChange = (userId) => {
    setCurrentUserId(userId);
    const selectedUser = availableUsers.find(user => user.id === userId);
    setIsManagerView(selectedUser?.role === 'Manager');
    setSelectedEmployee(null);
    setFeedbackText('');
    setEditingFeedback(null);
  };

  const handleCreateFeedback = async () => {
    if (!selectedEmployee || !feedbackText.trim()) {
      setError('Please select an employee and enter feedback text');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/manager/${currentUserId}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employee_id: selectedEmployee.id,
          feedback_text: feedbackText,
        }),
      });

      if (response.ok) {
        const newFeedback = await response.json();
        setFeedbacks([newFeedback, ...feedbacks]);
        setFeedbackText('');
        setSelectedEmployee(null);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to create feedback');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateFeedback = async (feedbackId) => {
    if (!feedbackText.trim()) {
      setError('Please enter feedback text');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/feedback/${feedbackId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          feedback_text: feedbackText,
        }),
      });

      if (response.ok) {
        const updatedFeedback = await response.json();
        setFeedbacks(feedbacks.map(f => f.id === feedbackId ? updatedFeedback : f));
        setFeedbackText('');
        setEditingFeedback(null);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to update feedback');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAISummary = async (feedbackId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/feedback/${feedbackId}/ai-summary`, {
        method: 'POST',
      });

      if (response.ok) {
        const updatedFeedback = await response.json();
        setFeedbacks(feedbacks.map(f => f.id === feedbackId ? updatedFeedback : f));
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to generate AI summary');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const startEditing = (feedback) => {
    setEditingFeedback(feedback);
    setFeedbackText(feedback.feedback_text);
  };

  const cancelEditing = () => {
    setEditingFeedback(null);
    setFeedbackText('');
  };

  const handleBack = () => {
    navigate('/main');
  };

  // AI Analysis Functions
  const analyzeFeedback = async (text) => {
    if (!text.trim() || !aiAssistantEnabled) return;
    
    setAiLoading(true);
    setAiStatus('processing');
    
    // Initialize processing steps
    const steps = [
      { id: 'tokenize', text: 'Tokenizing feedback text', icon: '🔤', status: 'pending' },
      { id: 'analyze', text: 'Analyzing tone and structure', icon: '🧠', status: 'pending' },
      { id: 'score', text: 'Calculating quality score', icon: '📊', status: 'pending' },
      { id: 'suggest', text: 'Generating suggestions', icon: '💡', status: 'pending' },
      { id: 'confidence', text: 'Computing confidence score', icon: '🎯', status: 'pending' }
    ];
    
    setAiProcessingSteps(steps);
    
    // Simulate processing steps
    const simulateProcessing = async () => {
      for (let i = 0; i < steps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 800));
        
        setAiProcessingSteps(prev => 
          prev.map((step, index) => ({
            ...step,
            status: index < i ? 'completed' : index === i ? 'active' : 'pending'
          }))
        );
      }
    };
    
    try {
      // Start processing simulation
      simulateProcessing();
      
      const response = await fetch('http://localhost:8000/api/feedback/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ feedback_text: text }),
      });

      if (response.ok) {
        const analysis = await response.json();
        setAiAnalysis(analysis);
        
        // Calculate confidence score based on analysis quality
        const confidenceScore = Math.min(95, Math.max(60, 
          (analysis.quality_score * 8) + 
          (analysis.tone_analysis?.constructiveness_score * 1.5) + 
          (analysis.tone_analysis?.balance_score * 1.5) + 
          (analysis.specificity_suggestions?.length * 2) +
          (analysis.missing_areas?.length * 1.5)
        ));
        
        setAiConfidence({
          score: Math.round(confidenceScore),
          level: confidenceScore > 85 ? 'High' : confidenceScore > 70 ? 'Medium' : 'Low',
          reasoning: confidenceScore > 85 ? 'Excellent analysis quality' : 
                    confidenceScore > 70 ? 'Good analysis with minor gaps' : 
                    'Analysis needs improvement'
        });
        
        setAiStatus('ready');
      } else {
        setAiStatus('error');
      }
    } catch (err) {
      console.error('Error analyzing feedback:', err);
      setAiStatus('error');
    } finally {
      setAiLoading(false);
    }
  };

  const getRealtimeSuggestions = async (text) => {
    if (!text.trim() || !aiAssistantEnabled) return;
    
    try {
      const response = await fetch('http://localhost:8000/api/feedback/realtime-suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ feedback_text: text }),
      });

      if (response.ok) {
        const suggestions = await response.json();
        setRealtimeSuggestions(suggestions);
      }
    } catch (err) {
      console.error('Error getting suggestions:', err);
    }
  };

  // Debounced AI analysis
  const debouncedAnalyzeFeedback = useCallback(
    debounce((text) => {
      if (text.length > 10) { // Only analyze if text is substantial
        analyzeFeedback(text);
      }
    }, 2000), // Wait 2 seconds after user stops typing
    [aiAssistantEnabled]
  );

  const debouncedRealtimeSuggestions = useCallback(
    debounce((text) => {
      if (text.length > 5) { // Get suggestions for shorter text
        getRealtimeSuggestions(text);
      }
    }, 1000), // Wait 1 second for real-time suggestions
    [aiAssistantEnabled]
  );

  // Handle feedback text changes
  const handleFeedbackTextChange = (e) => {
    const newText = e.target.value;
    setFeedbackText(newText);
    
    // Trigger AI analysis
    if (aiAssistantEnabled) {
      debouncedAnalyzeFeedback(newText);
      debouncedRealtimeSuggestions(newText);
    }
  };

  // Simple debounce function
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }


  return (
    <div className="performance-page">
      <div className="container">
        <div className="performance-header">
          <h1>Performance Feedback</h1>
          <div className="header-actions">
            <div className="user-selector">
              <label>View as:</label>
              <div className="custom-dropdown">
                <div className="dropdown-selected" onClick={() => setDropdownOpen(!dropdownOpen)}>
                  <span>{availableUsers.find(user => user.id === currentUserId)?.name} ({availableUsers.find(user => user.id === currentUserId)?.role})</span>
                  <span className={`dropdown-arrow ${dropdownOpen ? 'open' : ''}`}>▼</span>
                </div>
                {dropdownOpen && (
                  <div className="dropdown-options">
                    {availableUsers.map(user => (
                      <div 
                        key={user.id} 
                        className={`dropdown-option ${user.id === currentUserId ? 'selected' : ''}`}
                        onClick={() => {
                          handleUserChange(user.id);
                          setDropdownOpen(false);
                        }}
                      >
                        {user.name} ({user.role})
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <button className="btn btn-primary" onClick={handleBack}>
              Back to Main
            </button>
          </div>
        </div>
        
        <div className="performance-content">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {isManagerView ? (
            <ManagerView
              userProfile={userProfile}
              directReports={directReports}
              feedbacks={feedbacks}
              selectedEmployee={selectedEmployee}
              setSelectedEmployee={setSelectedEmployee}
              feedbackText={feedbackText}
              setFeedbackText={setFeedbackText}
              editingFeedback={editingFeedback}
              loading={loading}
              onCreateFeedback={handleCreateFeedback}
              onUpdateFeedback={handleUpdateFeedback}
              onStartEditing={startEditing}
              onCancelEditing={cancelEditing}
              aiAssistantEnabled={aiAssistantEnabled}
              setAiAssistantEnabled={setAiAssistantEnabled}
              aiAnalysis={aiAnalysis}
              aiLoading={aiLoading}
              realtimeSuggestions={realtimeSuggestions}
              onFeedbackTextChange={handleFeedbackTextChange}
              aiProcessingSteps={aiProcessingSteps}
              aiConfidence={aiConfidence}
              aiModelInfo={aiModelInfo}
              aiStatus={aiStatus}
              currentFeedbackIndex={currentFeedbackIndex}
              setCurrentFeedbackIndex={setCurrentFeedbackIndex}
            />
          ) : (
            <EmployeeView
              userProfile={userProfile}
              feedbacks={feedbacks}
              loading={loading}
              showAIAnalysis={showAIAnalysis}
              setShowAIAnalysis={setShowAIAnalysis}
              onGenerateAISummary={handleGenerateAISummary}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// Manager View Component
function ManagerView({
  userProfile,
  directReports,
  feedbacks,
  selectedEmployee,
  setSelectedEmployee,
  feedbackText,
  setFeedbackText,
  editingFeedback,
  loading,
  onCreateFeedback,
  onUpdateFeedback,
  onStartEditing,
  onCancelEditing,
  aiAssistantEnabled,
  setAiAssistantEnabled,
  aiAnalysis,
  aiLoading,
  realtimeSuggestions,
  onFeedbackTextChange,
  aiProcessingSteps,
  aiConfidence,
  aiModelInfo,
  aiStatus,
  currentFeedbackIndex,
  setCurrentFeedbackIndex
}) {
  // Ensure arrays are always arrays
  const safeFeedbacks = Array.isArray(feedbacks) ? feedbacks : [];
  const safeDirectReports = Array.isArray(directReports) ? directReports : [];
  
  // Carousel functions
  const nextFeedback = () => {
    setCurrentFeedbackIndex((prev) => 
      prev < safeFeedbacks.length - 1 ? prev + 1 : 0
    );
  };

  const prevFeedback = () => {
    setCurrentFeedbackIndex((prev) => 
      prev > 0 ? prev - 1 : safeFeedbacks.length - 1
    );
  };

  const goToFeedback = (index) => {
    setCurrentFeedbackIndex(index);
  };
  
  return (
    <div className="manager-view-container">
      <div className={`manager-view ${!aiAssistantEnabled ? 'ai-disabled' : ''}`}>
        <div className="manager-section">
          <h2>Write Performance Feedback</h2>
          
          <div className={`feedback-form ${!aiAssistantEnabled ? 'expanded' : ''}`}>
            <div className="form-group">
              <label>Select Employee:</label>
              <select 
                value={selectedEmployee?.id || ''} 
                onChange={(e) => {
                  const employee = safeDirectReports.find(emp => emp.id === parseInt(e.target.value));
                  setSelectedEmployee(employee);
                }}
                disabled={!!editingFeedback}
              >
                <option value="">Choose an employee...</option>
                {safeDirectReports.map(employee => (
                  <option key={employee.id} value={employee.id}>
                    {employee.name} ({employee.email})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Feedback:</label>
              <textarea
                value={feedbackText}
                onChange={onFeedbackTextChange}
                placeholder="Write your performance feedback here..."
                rows={6}
              />
            </div>

            {/* AI Assistant Toggle */}
            <div className="ai-toggle-switch">
              <label className="ai-toggle-label">
                <input
                  type="checkbox"
                  checked={aiAssistantEnabled}
                  onChange={(e) => setAiAssistantEnabled(e.target.checked)}
                  className="ai-toggle-input"
                />
                <span className="ai-toggle-slider"></span>
                <span>🤖 Enable AI Feedback Assistant</span>
              </label>
            </div>

            <div className="form-actions">
              {editingFeedback ? (
                <>
                  <button 
                    className="btn btn-primary" 
                    onClick={() => onUpdateFeedback(editingFeedback.id)}
                    disabled={loading}
                  >
                    {loading ? 'Updating...' : 'Update Feedback'}
                  </button>
                  <button 
                    className="btn btn-secondary" 
                    onClick={onCancelEditing}
                    disabled={loading}
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <button 
                  className="btn btn-primary" 
                  onClick={onCreateFeedback}
                  disabled={loading || !selectedEmployee || !feedbackText.trim()}
                >
                  {loading ? 'Creating...' : 'Create Feedback'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* AI Feedback Assistant */}
        {aiAssistantEnabled && (
          <div className="ai-feedback-assistant">
            <div className="ai-assistant-header">
              <span className="ai-assistant-icon">🤖</span>
              <h3 className="ai-assistant-title">AI Feedback Assistant</h3>
            </div>
            
            {/* AI Status Indicator */}
            {aiStatus === 'processing' && (
              <div className={`ai-status-indicator ai-status-${aiStatus}`}>
                <div className="ai-status-dot"></div>
                <span>AI Processing...</span>
              </div>
            )}
            
            {aiStatus === 'error' && (
              <div className={`ai-status-indicator ai-status-${aiStatus}`}>
                <div className="ai-status-dot"></div>
                <span>AI Error</span>
              </div>
            )}
            
            {aiLoading ? (
              <div className="ai-thinking-container">
                <div className="ai-thinking-header">
                  <span className="ai-thinking-icon">🧠</span>
                  <div>
                    <div className="ai-thinking-text">AI is analyzing your feedback</div>
                    <div className="ai-thinking-subtext">Processing with advanced language models...</div>
                  </div>
                </div>
                
                <div className="ai-processing-steps">
                  {aiProcessingSteps.map((step, index) => (
                    <div key={step.id} className={`ai-processing-step ${step.status}`}>
                      <span className="ai-step-icon">{step.icon}</span>
                      <span className="ai-step-text">{step.text}</span>
                      <span className="ai-step-status">
                        {step.status === 'completed' ? '✓' : 
                         step.status === 'active' ? '⏳' : '⏸'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : aiAnalysis ? (
              <>
                {/* AI Confidence Score */}
                {aiConfidence && (
                  <div className="ai-confidence-container">
                    <span className="ai-confidence-label">AI Confidence:</span>
                    <div className="ai-confidence-score">
                      <span className="ai-confidence-value">{aiConfidence.score}%</span>
                      <div className="ai-confidence-bar">
                        <div 
                          className="ai-confidence-fill" 
                          style={{ width: `${aiConfidence.score}%` }}
                        ></div>
                      </div>
                      <span className="ai-confidence-text">{aiConfidence.level}</span>
                    </div>
                  </div>
                )}

                {/* Quality Score */}
                <div className="ai-quality-score">
                  <span className="quality-score-label">Quality Score:</span>
                  <span className="quality-score-value">{aiAnalysis.quality_score}/10</span>
                  <div className="quality-score-bar">
                    <div 
                      className="quality-score-fill" 
                      style={{ width: `${(aiAnalysis.quality_score / 10) * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Tone Analysis */}
                {aiAnalysis.tone_analysis && (
                  <div className="ai-tone-analysis">
                    <div className="tone-analysis-header">Tone Analysis</div>
                    <div className="tone-metrics">
                      <div className="tone-metric">
                        <div className="tone-metric-value">{aiAnalysis.tone_analysis.overall_tone}</div>
                        <div className="tone-metric-label">Overall Tone</div>
                      </div>
                      <div className="tone-metric">
                        <div className="tone-metric-value">{aiAnalysis.tone_analysis.constructiveness_score}/10</div>
                        <div className="tone-metric-label">Constructive</div>
                      </div>
                      <div className="tone-metric">
                        <div className="tone-metric-value">{aiAnalysis.tone_analysis.balance_score}/10</div>
                        <div className="tone-metric-label">Balance</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Suggestions Grid */}
                <div className="ai-suggestions-grid">
                  {aiAnalysis.specificity_suggestions && aiAnalysis.specificity_suggestions.length > 0 && (
                    <div className="ai-suggestion-card">
                      <div className="suggestion-card-header">
                        <span className="suggestion-card-icon">🎯</span>
                        <h4 className="suggestion-card-title">Specificity</h4>
                      </div>
                      <ul className="suggestion-list">
                        {aiAnalysis.specificity_suggestions.map((suggestion, index) => (
                          <li key={index} className="suggestion-item">{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {aiAnalysis.missing_areas && aiAnalysis.missing_areas.length > 0 && (
                    <div className="ai-suggestion-card">
                      <div className="suggestion-card-header">
                        <span className="suggestion-card-icon">📋</span>
                        <h4 className="suggestion-card-title">Missing Areas</h4>
                      </div>
                      <ul className="suggestion-list">
                        {aiAnalysis.missing_areas.map((area, index) => (
                          <li key={index} className="suggestion-item">{area}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {aiAnalysis.actionability_suggestions && aiAnalysis.actionability_suggestions.length > 0 && (
                    <div className="ai-suggestion-card">
                      <div className="suggestion-card-header">
                        <span className="suggestion-card-icon">⚡</span>
                        <h4 className="suggestion-card-title">Actionability</h4>
                      </div>
                      <ul className="suggestion-list">
                        {aiAnalysis.actionability_suggestions.map((suggestion, index) => (
                          <li key={index} className="suggestion-item">{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Overall Recommendations */}
                {aiAnalysis.overall_recommendations && (
                  <div className="ai-suggestion-card">
                    <div className="suggestion-card-header">
                      <span className="suggestion-card-icon">💡</span>
                      <h4 className="suggestion-card-title">Key Recommendations</h4>
                    </div>
                    <p style={{ color: 'rgba(255, 255, 255, 0.95)', margin: 0, fontSize: '0.9rem', lineHeight: '1.4' }}>
                      {aiAnalysis.overall_recommendations}
                    </p>
                  </div>
                )}

                {/* AI Model Information */}
                <div className="ai-model-info">
                  <span className="ai-model-icon">🤖</span>
                  <span className="ai-model-text">Powered by {aiModelInfo.model}</span>
                  <span className="ai-model-version">v{aiModelInfo.version}</span>
                </div>
              </>
            ) : (
              <div>
                <p style={{ color: 'rgba(255, 255, 255, 0.8)', margin: 0, fontSize: '0.9rem', marginBottom: '1rem' }}>
                  Start typing your feedback to get AI-powered suggestions and analysis.
                </p>
                
                {/* AI Model Information */}
                <div className="ai-model-info">
                  <span className="ai-model-icon">🤖</span>
                  <span className="ai-model-text">Powered by {aiModelInfo.model}</span>
                  <span className="ai-model-version">v{aiModelInfo.version}</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Previous Feedback - Full Width Bottom Section */}
      <div className="previous-feedback-section">
        <h2>Previous Feedback</h2>
        
        {safeFeedbacks.length === 0 ? (
          <div className="no-feedback">
            <p>No feedback given yet.</p>
          </div>
        ) : (
          <div className="feedback-carousel">
            <div className="feedback-carousel-header">
              <h3 className="feedback-carousel-title">
                Feedback {currentFeedbackIndex + 1} of {safeFeedbacks.length}
              </h3>
              <div className="feedback-carousel-controls">
                <button 
                  className="feedback-carousel-btn"
                  onClick={prevFeedback}
                  disabled={safeFeedbacks.length <= 1}
                >
                  ←
                </button>
                <button 
                  className="feedback-carousel-btn"
                  onClick={nextFeedback}
                  disabled={safeFeedbacks.length <= 1}
                >
                  →
                </button>
              </div>
            </div>
            
            <div className="feedback-carousel-container">
              <div 
                className="feedback-carousel-track"
                style={{ transform: `translateX(-${currentFeedbackIndex * 100}%)` }}
              >
                {safeFeedbacks.map((feedback, index) => (
                  <div key={feedback.id} className="feedback-item">
                    <div className="feedback-header">
                      <h3>{feedback.employee?.name || 'Unknown Employee'}</h3>
                      <span className="feedback-date">
                        {new Date(feedback.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="feedback-content">
                      <p>{feedback.feedback_text}</p>
                    </div>
                    <div className="feedback-actions">
                      <button 
                        className="btn btn-small btn-secondary"
                        onClick={() => onStartEditing(feedback)}
                      >
                        Edit
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {safeFeedbacks.length > 1 && (
              <div className="feedback-carousel-indicators">
                {safeFeedbacks.map((_, index) => (
                  <button
                    key={index}
                    className={`feedback-carousel-indicator ${index === currentFeedbackIndex ? 'active' : ''}`}
                    onClick={() => goToFeedback(index)}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Employee View Component
function EmployeeView({ userProfile, feedbacks, loading, showAIAnalysis, setShowAIAnalysis, onGenerateAISummary }) {
  // Ensure feedbacks is always an array
  const safeFeedbacks = Array.isArray(feedbacks) ? feedbacks : [];
  
  return (
    <div className="employee-view">
      <div className="employee-section">
        <div className="section-header">
          <h2>Your Performance Feedback</h2>
          <div className="ai-toggle">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={showAIAnalysis}
                onChange={(e) => setShowAIAnalysis(e.target.checked)}
                className="toggle-input"
              />
              <span className="toggle-slider"></span>
              <span className="toggle-text">Show AI Analysis</span>
            </label>
          </div>
        </div>
        
        {safeFeedbacks.length === 0 ? (
          <p className="no-feedback">No feedback received yet.</p>
        ) : (
          safeFeedbacks.map(feedback => (
            <div key={feedback.id} className="feedback-card">
              <div className="feedback-header">
                <h3>Feedback from {feedback.manager?.name || 'Your Manager'}</h3>
                <span className="feedback-date">
                  {new Date(feedback.created_at).toLocaleDateString()}
                </span>
              </div>
              
              <div className="feedback-content">
                <div className="original-feedback">
                  <h4>Manager's Feedback:</h4>
                  <p>{feedback.feedback_text}</p>
                </div>

                {feedback.ai_summary && showAIAnalysis && (
                  <div className="ai-analysis">
                    <div className="ai-header">
                      <h4>🤖 AI Analysis</h4>
                      <div className="ai-header-actions">
                        <button 
                          className="regenerate-btn"
                          onClick={() => onGenerateAISummary(feedback.id)}
                          disabled={loading}
                          title="Regenerate AI Analysis"
                        >
                          {loading ? '⏳' : '🔄'} Regenerate
                        </button>
                        <button 
                          className="hide-analysis-btn"
                          onClick={() => setShowAIAnalysis(false)}
                          title="Hide AI Analysis"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                    
                    <div className="analysis-grid">
                      {feedback.ai_summary && (
                        <div className="analysis-card summary-card">
                          <div className="card-icon">📋</div>
                          <h5>Summary</h5>
                          <p>{feedback.ai_summary}</p>
                        </div>
                      )}
                      
                      {feedback.strengths && (
                        <div className="analysis-card strengths-card">
                          <div className="card-icon">💪</div>
                          <h5>Strengths</h5>
                          <p>{feedback.strengths}</p>
                        </div>
                      )}
                      
                      {feedback.areas_for_improvement && (
                        <div className="analysis-card improvement-card">
                          <div className="card-icon">🎯</div>
                          <h5>Areas for Improvement</h5>
                          <p>{feedback.areas_for_improvement}</p>
                        </div>
                      )}
                      
                      {feedback.next_steps && (
                        <div className="analysis-card nextsteps-card">
                          <div className="card-icon">🚀</div>
                          <h5>Next Steps</h5>
                          <p>{feedback.next_steps}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {!feedback.ai_summary && (
                  <div className="ai-actions">
                    <button 
                      className="btn btn-primary"
                      onClick={() => onGenerateAISummary(feedback.id)}
                      disabled={loading}
                    >
                      {loading ? 'Generating...' : 'Generate AI Summary'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Performance;
