import React, { useState, useEffect } from 'react';
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
  onCancelEditing
}) {
  // Ensure arrays are always arrays
  const safeFeedbacks = Array.isArray(feedbacks) ? feedbacks : [];
  const safeDirectReports = Array.isArray(directReports) ? directReports : [];
  
  return (
    <div className="manager-view">
      <div className="manager-section">
        <h2>Write Performance Feedback</h2>
        
        <div className="feedback-form">
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
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Write your performance feedback here..."
              rows={6}
            />
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

      <div className="manager-section">
        <h2>Previous Feedback</h2>
        <div className="feedback-list">
          {safeFeedbacks.length === 0 ? (
            <p className="no-feedback">No feedback given yet.</p>
          ) : (
            safeFeedbacks.map(feedback => (
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
            ))
          )}
        </div>
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
