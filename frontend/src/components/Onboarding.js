import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Onboarding.css';

function Onboarding() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [completedTasks, setCompletedTasks] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(null);

  // AI Agents configuration
  const agents = {
    culture: {
      name: "Culture & Knowledge Agent",
      avatar: "🏢",
      color: "#4CAF50",
      description: "Company guidelines, office perks, compliance"
    },
    forms: {
      name: "Form-Filler Agent",
      avatar: "📝",
      color: "#2196F3",
      description: "Auto-fills HR/IT/SAP forms; validates fields"
    },
    sap: {
      name: "SAP Coach Agent",
      avatar: "🎯",
      color: "#FF9800",
      description: "Guides sandbox SAP tasks with step-by-step hints"
    },
    coordination: {
      name: "Coordination Agent",
      avatar: "🤝",
      color: "#9C27B0",
      description: "Handles account setup, permissions, intro meetings"
    }
  };

  // Onboarding tasks with agent assignments
  const onboardingTasks = [
    {
      id: 1,
      title: "Welcome & Company Overview",
      description: "Learn about SAP's culture, values, and company policies",
      agent: "culture",
      status: "pending",
      actions: [
        { label: "Watch Welcome Video", action: "watch_video" },
        { label: "Review Company Policies", action: "review_policies" },
        { label: "Complete Culture Quiz", action: "take_quiz" }
      ]
    },
    {
      id: 2,
      title: "Account Setup & Permissions",
      description: "Get your SAP accounts and system access configured",
      agent: "coordination",
      status: "pending",
      actions: [
        { label: "Setup Email Account", action: "setup_email" },
        { label: "Configure SAP Access", action: "setup_sap_access" },
        { label: "Request Permissions", action: "request_permissions" }
      ]
    },
    {
      id: 3,
      title: "HR Documentation",
      description: "Complete required HR forms and documentation",
      agent: "forms",
      status: "pending",
      actions: [
        { label: "Fill Personal Information", action: "fill_personal_info" },
        { label: "Complete Tax Forms", action: "complete_tax_forms" },
        { label: "Submit Benefits Selection", action: "submit_benefits" }
      ]
    },
    {
      id: 4,
      title: "SAP System Introduction",
      description: "Learn the basics of SAP systems and navigation",
      agent: "sap",
      status: "pending",
      actions: [
        { label: "SAP Navigation Tutorial", action: "sap_tutorial" },
        { label: "Practice in Sandbox", action: "sandbox_practice" },
        { label: "Complete SAP Quiz", action: "sap_quiz" }
      ]
    },
    {
      id: 5,
      title: "Team Introduction",
      description: "Meet your team and schedule initial meetings",
      agent: "coordination",
      status: "pending",
      actions: [
        { label: "Schedule Team Meeting", action: "schedule_meeting" },
        { label: "Review Team Structure", action: "review_team" },
        { label: "Setup Communication Tools", action: "setup_communication" }
      ]
    },
    {
      id: 6,
      title: "IT Setup & Security",
      description: "Configure your workstation and security protocols",
      agent: "coordination",
      status: "pending",
      actions: [
        { label: "Workstation Setup", action: "workstation_setup" },
        { label: "Security Training", action: "security_training" },
        { label: "VPN Configuration", action: "vpn_setup" }
      ]
    }
  ];

  const handleBack = () => {
    navigate('/main');
  };

  const handleTaskAction = async (taskId, action) => {
    setIsProcessing(true);
    setCurrentAgent(onboardingTasks.find(task => task.id === taskId)?.agent);
    
    // Simulate AI agent processing
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mark task as completed
    if (!completedTasks.includes(taskId)) {
      setCompletedTasks([...completedTasks, taskId]);
    }
    
    setIsProcessing(false);
    setCurrentAgent(null);
  };

  const handleNextStep = () => {
    if (currentStep < onboardingTasks.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const getProgressPercentage = () => {
    return (completedTasks.length / onboardingTasks.length) * 100;
  };

  const getCurrentTask = () => onboardingTasks[currentStep];

  return (
    <div className="onboarding-page">
      <div className="onboarding-header">
        <div className="header-content">
          <h1>Welcome to SAP! 🚀</h1>
          <p>Your guided onboarding journey with AI assistance</p>
          <button className="btn btn-secondary" onClick={handleBack}>
            ← Back to Main
          </button>
        </div>
      </div>

      <div className="onboarding-container">
        {/* Progress Bar */}
        <div className="progress-section">
          <div className="progress-header">
            <h3>Onboarding Progress</h3>
            <span className="progress-text">{completedTasks.length}/{onboardingTasks.length} completed</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${getProgressPercentage()}%` }}
            ></div>
          </div>
          <div className="agent-progress">
            {Object.entries(agents).map(([key, agent]) => {
              const agentTasks = onboardingTasks.filter(task => task.agent === key);
              const completedAgentTasks = agentTasks.filter(task => completedTasks.includes(task.id));
              const agentProgress = agentTasks.length > 0 ? (completedAgentTasks.length / agentTasks.length) * 100 : 0;
              
              return (
                <div key={key} className="agent-progress-item">
                  <span className="agent-avatar">{agent.avatar}</span>
                  <div className="agent-progress-bar">
                    <div 
                      className="agent-progress-fill" 
                      style={{ 
                        width: `${agentProgress}%`,
                        backgroundColor: agent.color 
                      }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Current Task Card */}
        <div className="task-section">
          <div className="step-indicator">
            <span className="step-number">{currentStep + 1}</span>
            <span className="step-text">of {onboardingTasks.length}</span>
          </div>
          
          <div className="task-card">
            <div className="task-header">
              <div className="agent-info">
                <span className="agent-avatar-large">
                  {agents[getCurrentTask()?.agent]?.avatar}
                </span>
                <div className="agent-details">
                  <h3 className="agent-name">{agents[getCurrentTask()?.agent]?.name}</h3>
                  <p className="agent-description">{agents[getCurrentTask()?.agent]?.description}</p>
                </div>
              </div>
              <div className="task-status">
                {completedTasks.includes(getCurrentTask()?.id) ? (
                  <span className="status-completed">✓ Completed</span>
                ) : (
                  <span className="status-pending">⏳ In Progress</span>
                )}
              </div>
            </div>

            <div className="task-content">
              <h2>{getCurrentTask()?.title}</h2>
              <p>{getCurrentTask()?.description}</p>
              
              <div className="task-actions">
                {getCurrentTask()?.actions.map((action, index) => (
                  <button
                    key={index}
                    className={`action-btn ${completedTasks.includes(getCurrentTask()?.id) ? 'completed' : ''}`}
                    onClick={() => handleTaskAction(getCurrentTask()?.id, action.action)}
                    disabled={isProcessing}
                  >
                    {isProcessing && currentAgent === getCurrentTask()?.agent ? (
                      <span className="loading-spinner">⏳</span>
                    ) : (
                      action.label
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="navigation-section">
          <button 
            className="nav-btn prev-btn" 
            onClick={handlePreviousStep}
            disabled={currentStep === 0}
          >
            ← Previous
          </button>
          
          <div className="step-dots">
            {onboardingTasks.map((task, index) => (
              <span 
                key={index}
                className={`step-dot ${index === currentStep ? 'active' : ''} ${completedTasks.includes(task.id) ? 'completed' : ''}`}
                onClick={() => setCurrentStep(index)}
              ></span>
            ))}
          </div>
          
          <button 
            className="nav-btn next-btn" 
            onClick={handleNextStep}
            disabled={currentStep === onboardingTasks.length - 1}
          >
            Next →
          </button>
        </div>

        {/* AI Processing Indicator */}
        {isProcessing && (
          <div className="ai-processing">
            <div className="processing-content">
              <span className="processing-avatar">
                {agents[currentAgent]?.avatar}
              </span>
              <div className="processing-text">
                <h4>{agents[currentAgent]?.name} is working...</h4>
                <p>Please wait while I assist you with this task</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Onboarding;
