import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import './Performance.css';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

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
  const [currentUserId, setCurrentUserId] = useState(null); // Start with no user selected
  const [hasSelectedRole, setHasSelectedRole] = useState(false); // Track if user has selected a role
  const [showAIAnalysis, setShowAIAnalysis] = useState(true); // Toggle for AI analysis visibility
  const [dropdownOpen, setDropdownOpen] = useState(false); // Custom dropdown state
  const [aiAssistantEnabled, setAiAssistantEnabled] = useState(true); // AI assistant toggle
  const [aiAnalysis, setAiAnalysis] = useState(null); // AI analysis data
  const [aiLoading, setAiLoading] = useState(false); // AI loading state
  const [aiProcessingSteps, setAiProcessingSteps] = useState([]); // AI processing steps
  const [aiConfidence, setAiConfidence] = useState(null); // AI confidence score
  const [aiModelInfo, setAiModelInfo] = useState({ model: 'GPT-4', version: '2024-01-01' }); // AI model info
  const [aiStatus, setAiStatus] = useState('ready'); // AI status: ready, processing, error
  const [currentFeedbackIndex, setCurrentFeedbackIndex] = useState(0); // Carousel current index
  const [insight, setInsight] = useState(''); // AI insight state
  const [chartData, setChartData] = useState(null); // Chart data state
  const [goals, setGoals] = useState([
    { id: 1, name: 'Training', progress: 0, target: 100 },
    { id: 2, name: 'Onboarding', progress: 0, target: 100 }
  ]); // Goals state
  const [loadingGoals, setLoadingGoals] = useState(true); // Loading goals state
  const [lastFeedbackCount, setLastFeedbackCount] = useState(0); // Track feedback count for polling
  const [pollingInterval, setPollingInterval] = useState(null); // Polling interval reference
  const [newFeedbackNotification, setNewFeedbackNotification] = useState(null); // New feedback notification

  // Available users from performance testing database
  const availableUsers = [
    { id: "perf_manager001", name: "Alex Thompson", role: "Manager" },
    { id: "perf_employee001", name: "Sarah Chen", role: "Employee" },
    { id: "perf_employee002", name: "David Rodriguez", role: "Employee" },
    { id: "perf_employee003", name: "Lisa Park", role: "Employee" }
  ];

  useEffect(() => {
    if (currentUserId && hasSelectedRole) {
      loadUserProfile();
      loadLatestInsight();
      loadGoalsFromBackend();
      if (isManagerView) {
        loadDirectReports();
        loadManagerFeedbacks();
      } else {
        loadEmployeeFeedbacks();
      }
      
      // Start polling for feedback updates (every 10 seconds)
      startPolling();
    }
    
    // Cleanup polling when component unmounts or dependencies change
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }
    };
  }, [isManagerView, currentUserId, hasSelectedRole]);

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
      const response = await fetch(`http://localhost:8000/api/performance/users/${currentUserId}/profile`);
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
      const response = await fetch(`http://localhost:8000/api/performance/users/${currentUserId}/direct-reports`);
      if (response.ok) {
        const reports = await response.json();
        console.log('Direct reports loaded:', reports);
        setDirectReports(Array.isArray(reports) ? reports : []);
      } else {
        console.error('Failed to load direct reports, status:', response.status);
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
        const feedbackArray = Array.isArray(feedbacks) ? feedbacks : [];
        setFeedbacks(feedbackArray);
        
        // Update feedback count for polling detection
        setLastFeedbackCount(feedbackArray.length);
        
        return feedbackArray;
      } else {
        console.error('Failed to load employee feedbacks');
        setFeedbacks([]);
        setLastFeedbackCount(0);
        return [];
      }
    } catch (err) {
      console.error('Error loading employee feedbacks:', err);
      setFeedbacks([]);
      setLastFeedbackCount(0);
      return [];
    }
  };

  const loadManagerFeedbacks = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/manager/${currentUserId}/feedback`);
      if (response.ok) {
        const feedbacks = await response.json();
        const feedbackArray = Array.isArray(feedbacks) ? feedbacks : [];
        setFeedbacks(feedbackArray);
        
        // Update feedback count for polling detection
        setLastFeedbackCount(feedbackArray.length);
        
        return feedbackArray;
      } else {
        console.error('Failed to load manager feedbacks');
        setFeedbacks([]);
        setLastFeedbackCount(0);
        return [];
      }
    } catch (err) {
      console.error('Error loading manager feedbacks:', err);
      setFeedbacks([]);
      setLastFeedbackCount(0);
      return [];
    }
  };

  const loadLatestInsight = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/performance/users/${currentUserId}/latest-insight`);
      if (response.ok) {
        const data = await response.json();
        if (data.insight) {
          setInsight(data.insight);
        } else {
          setInsight(''); // Clear insight if none available
        }
      } else {
        console.error('Failed to load AI insight from backend');
      }
    } catch (err) {
      console.error('Error loading AI insight:', err);
    }
  };

  const loadGoalsFromBackend = async () => {
    try {
      setLoadingGoals(true);
      const response = await fetch(`http://localhost:8000/api/performance/users/${currentUserId}/goals`);
      if (response.ok) {
        const data = await response.json();
        if (data.goals) {
          setGoals(data.goals);
          
          // Update chart data when goals are loaded
          const chartData = {
            type: "bar",
            labels: data.goals.map(goal => goal.name),
            datasets: [{
              label: "Progress %",
              data: data.goals.map(goal => goal.progress),
              backgroundColor: ["#3498db", "#2980b9"]
            }]
          };
          setChartData(chartData);
        }
      } else {
        console.error('Failed to load goals from backend');
      }
    } catch (err) {
      console.error('Error loading goals:', err);
    } finally {
      setLoadingGoals(false);
    }
  };

  // Polling functions for real-time updates
  const startPolling = () => {
    // Clear any existing polling
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
    
    // Start new polling interval (every 10 seconds)
    const interval = setInterval(async () => {
      if (currentUserId && hasSelectedRole) {
        await checkForNewFeedback();
      }
    }, 10000); // 10 seconds
    
    setPollingInterval(interval);
  };

  const checkForNewFeedback = async () => {
    try {
      let currentFeedbacks = [];
      
      if (isManagerView) {
        currentFeedbacks = await loadManagerFeedbacks();
      } else {
        currentFeedbacks = await loadEmployeeFeedbacks();
      }
      
      // Check if feedback count has changed
      if (currentFeedbacks.length !== lastFeedbackCount) {
        console.log(`New feedback detected! Count changed from ${lastFeedbackCount} to ${currentFeedbacks.length}`);
        
        // Show a subtle notification (optional)
        if (currentFeedbacks.length > lastFeedbackCount) {
          console.log('🎉 New feedback received!');
          setNewFeedbackNotification(`🎉 ${currentFeedbacks.length - lastFeedbackCount} new feedback received!`);
          
          // Auto-hide notification after 5 seconds
          setTimeout(() => {
            setNewFeedbackNotification(null);
          }, 5000);
        }
      }
    } catch (err) {
      console.error('Error checking for new feedback:', err);
    }
  };

  const manualRefresh = async () => {
    console.log('Manual refresh triggered');
    if (currentUserId && hasSelectedRole) {
      if (isManagerView) {
        await loadManagerFeedbacks();
      } else {
        await loadEmployeeFeedbacks();
      }
    }
  };

  const handleUserChange = (userId) => {
    setCurrentUserId(userId);
    const selectedUser = availableUsers.find(user => user.id === userId);
    setIsManagerView(selectedUser?.role === 'Manager');
    setSelectedEmployee(null);
    setFeedbackText('');
    setEditingFeedback(null);
    setHasSelectedRole(true); // Mark that user has selected a role
    
    // Clear user-specific data when switching users
    setInsight('');
    setChartData(null);
    setGoals([
      { id: 1, name: 'Training', progress: 0, target: 100 },
      { id: 2, name: 'Onboarding', progress: 0, target: 100 }
    ]);
    setLoadingGoals(true);
    
    // Reset feedback count
    setLastFeedbackCount(0);
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


  // Debounced AI analysis
  const debouncedAnalyzeFeedback = useCallback(
    debounce((text) => {
      if (text.length > 10) { // Only analyze if text is substantial
        analyzeFeedback(text);
      }
    }, 2000), // Wait 2 seconds after user stops typing
    [aiAssistantEnabled]
  );


  // Handle feedback text changes
  const handleFeedbackTextChange = (e) => {
    const newText = e.target.value;
    setFeedbackText(newText);
    
    // Trigger AI analysis
    if (aiAssistantEnabled) {
      debouncedAnalyzeFeedback(newText);
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
            {hasSelectedRole && (
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
            )}
            <button className="btn btn-secondary" onClick={manualRefresh} title="Refresh feedback">
              🔄 Refresh
            </button>
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
          
          {newFeedbackNotification && (
            <div className="feedback-notification">
              {newFeedbackNotification}
            </div>
          )}

          {!hasSelectedRole ? (
            <div className="empty-state">
              <div className="empty-state-content">
                <div className="empty-state-icon">👤</div>
                <h2>Select Your Role</h2>
                <p>Choose how you'd like to view the Performance Feedback section:</p>
                <div className="role-selection">
                  <button 
                    className="role-btn employee-btn"
                    onClick={() => handleUserChange("perf_employee001")}
                  >
                    <span className="role-icon">👨‍💼</span>
                    <span className="role-title">View as Employee</span>
                    <span className="role-description">See feedback received from your manager</span>
                  </button>
                  <button 
                    className="role-btn manager-btn"
                    onClick={() => handleUserChange("perf_manager001")}
                  >
                    <span className="role-icon">👩‍💼</span>
                    <span className="role-title">View as Manager</span>
                    <span className="role-description">Write and manage feedback for your team</span>
                  </button>
                </div>
              </div>
            </div>
          ) : isManagerView ? (
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
              currentUserId={currentUserId}
              insight={insight}
              setInsight={setInsight}
              chartData={chartData}
              setChartData={setChartData}
              goals={goals}
              setGoals={setGoals}
              loadingGoals={loadingGoals}
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
  
  // Debug logging
  console.log('ManagerView - directReports:', directReports);
  console.log('ManagerView - safeDirectReports:', safeDirectReports);
  console.log('ManagerView - selectedEmployee:', selectedEmployee);
  
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
              <label>Select Employee ({safeDirectReports.length} available):</label>
              <select 
                value={selectedEmployee?.id || ''} 
                onChange={(e) => {
                  console.log('Employee selection changed:', e.target.value);
                  const employee = safeDirectReports.find(emp => emp.id === parseInt(e.target.value));
                  console.log('Found employee:', employee);
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
              {safeDirectReports.length === 0 && (
                <div style={{ color: 'orange', fontSize: '12px', marginTop: '5px' }}>
                  No employees found. Check if manager has direct reports in database.
                </div>
              )}
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
function EmployeeView({ userProfile, feedbacks, loading, showAIAnalysis, setShowAIAnalysis, onGenerateAISummary, currentUserId, insight, setInsight, chartData, setChartData, goals, setGoals, loadingGoals }) {
  // Ensure feedbacks is always an array
  const safeFeedbacks = Array.isArray(feedbacks) ? feedbacks : [];
  
  return (
    <div className="employee-view">
      <div className="employee-dashboard">
        {/* Personal Goals Section - Left Sidebar */}
        <PersonalGoalsSection 
          currentUserId={currentUserId} 
          insight={insight}
          setInsight={setInsight}
          chartData={chartData}
          setChartData={setChartData}
          goals={goals}
          setGoals={setGoals}
          loadingGoals={loadingGoals}
        />
        
        {/* Manager Feedback Section - Right Side */}
        <div className="manager-feedback-section">
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
    </div>
  );
}

// Personal Goals Section Component
function PersonalGoalsSection({ currentUserId, insight, setInsight, chartData, setChartData, goals, setGoals, loadingGoals }) {
  const [progressUpdate, setProgressUpdate] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  // Update chart data when goals change
  useEffect(() => {
    if (goals && goals.length > 0) {
      const chartData = {
        type: "bar",
        labels: goals.map(goal => goal.name),
        datasets: [{
          label: "Progress %",
          data: goals.map(goal => goal.progress),
          backgroundColor: ["#3498db", "#2980b9"]
        }]
      };
      setChartData(chartData);
    }
  }, [goals]);



  const handleProgressUpdate = async () => {
    if (!progressUpdate.trim()) return;
    
    setIsUpdating(true);
    
    try {
      const response = await fetch(`http://localhost:8000/api/progress/update/${currentUserId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          progress_text: progressUpdate,
          current_goals: goals
        }),
      });

      if (response.ok) {
        const result = await response.json();
        
        // Update goals with new progress
        if (result.goals) {
          setGoals(result.goals);
        }
        
        // Update insight
        if (result.insight) {
          setInsight(result.insight);
        }
        
        // Update chart data
        if (result.chart_data) {
          setChartData(result.chart_data);
        }
        
        // Clear input
        setProgressUpdate('');
      } else {
        console.error('Failed to update progress');
      }
    } catch (err) {
      console.error('Error updating progress:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleProgressUpdate();
    }
  };

  return (
    <div className="personal-goals-section">
      <div className="goals-header">
        <h2>Personal Goals</h2>
        <div className="goals-subtitle">Track your progress and achievements</div>
      </div>

      {/* Progress Chart */}
      <div className="progress-chart-container">
        <h3>Goal Progress</h3>
        <div className="chart-wrapper">
          {loadingGoals ? (
            <div className="chart-loading">
              <div className="loading-spinner"></div>
              <p>Loading goals...</p>
            </div>
          ) : chartData ? (
            <ProgressChart data={chartData} />
          ) : (
            <DefaultProgressChart goals={goals} />
          )}
        </div>
      </div>

      {/* AI Insight */}
      {insight && (
        <div className="insight-container">
          <div className="insight-header">
            <span className="insight-icon">💡</span>
            <h4>AI Insight</h4>
          </div>
          <p className="insight-text">{insight}</p>
        </div>
      )}

      {/* Progress Update Input */}
      <div className="progress-update-section">
        <label htmlFor="progress-update" className="update-label">
          Update your progress
        </label>
        <div className="update-input-container">
          <textarea
            id="progress-update"
            value={progressUpdate}
            onChange={(e) => setProgressUpdate(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="I finished my first training course..."
            className="progress-update-input"
            rows={3}
            disabled={isUpdating}
          />
          <button
            onClick={handleProgressUpdate}
            disabled={isUpdating || !progressUpdate.trim()}
            className="update-btn"
          >
            {isUpdating ? 'Updating...' : 'Update'}
          </button>
        </div>
      </div>

      {/* Goals List */}
      <div className="goals-list">
        <h3>Current Goals</h3>
        <div className="goals-grid">
          {goals.map(goal => (
            <div key={goal.id} className="goal-card">
              <div className="goal-header">
                <h4>{goal.name}</h4>
                <span className="goal-progress">{goal.progress}%</span>
              </div>
              <div className="goal-progress-bar">
                <div 
                  className="goal-progress-fill" 
                  style={{ width: `${goal.progress}%` }}
                ></div>
              </div>
              <div className="goal-target">Target: {goal.target}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Progress Chart Component
function ProgressChart({ data }) {
  if (!data) {
    return (
      <div className="chart-container">
        <div className="chart-placeholder">
          <span className="chart-icon">📊</span>
          <p>No chart data available</p>
        </div>
      </div>
    );
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Goal Progress Overview',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      }
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-wrapper">
        <Bar data={data} options={chartOptions} />
      </div>
    </div>
  );
}

// Default Progress Chart Component
function DefaultProgressChart({ goals }) {
  // Create chart data from goals
  const chartData = {
    labels: goals.map(goal => goal.name),
    datasets: [{
      label: 'Progress %',
      data: goals.map(goal => goal.progress),
      backgroundColor: [
        'var(--primary-blue)',
        'var(--secondary-blue)', 
        'var(--dark-blue)',
        'var(--dark-gray)',
        'var(--darker-gray)'
      ],
      borderColor: [
        'var(--secondary-blue)',
        'var(--dark-blue)',
        'var(--dark-gray)',
        'var(--darker-gray)',
        'var(--darkest-gray)'
      ],
      borderWidth: 2
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Goal Progress Overview',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      }
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-wrapper">
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}

export default Performance;
