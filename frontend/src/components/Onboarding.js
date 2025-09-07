import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Onboarding.css';

function Onboarding() {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [showVideoPopup, setShowVideoPopup] = useState(false);
  const [showPolicyPopup, setShowPolicyPopup] = useState(false);
  const [showQuizPopup, setShowQuizPopup] = useState(false);
  const [currentPolicyIndex, setCurrentPolicyIndex] = useState(0);
  
  const policies = [
    { name: 'Code of Conduct', icon: '📋', description: 'Ethical principles and standards of behavior expected of all SAP employees.' },
    { name: 'Data Protection', icon: '🔒', description: 'Guidelines for handling personal and sensitive data in compliance with regulations.' },
    { name: 'Workplace Safety', icon: '🛡️', description: 'Safety protocols and procedures to ensure a secure working environment.' },
    { name: 'Diversity & Inclusion', icon: '🤝', description: 'Commitment to creating an inclusive workplace that values diversity.' }
  ];
  
  const [currentNode, setCurrentNode] = useState('welcome_overview');
  const [nodeTasks, setNodeTasks] = useState({
    welcome_overview: {
      welcome_video: false,
      company_policies: false,
      culture_quiz: false
    },
    account_setup: {
      email_setup: false,
      sap_access: false,
      permissions: false
    }
  });

  // Initialize chat with state loading
  useEffect(() => {
    loadUserState();
  }, []);

  const loadUserState = async () => {
    try {
      // Load user state from backend
      const response = await fetch(`http://localhost:8000/api/user/test_user/state`);
      const data = await response.json();
      
      if (data.chat_messages && data.chat_messages.length > 0) {
        // Convert backend messages to frontend format
        const messages = data.chat_messages.map(msg => ({
          id: Date.now() + Math.random(),
          type: msg.role === 'user' ? 'user' : 'agent',
          text: msg.content,
          timestamp: new Date(msg.timestamp)
        }));
        setChatMessages(messages);
        
        // Update state from backend
        if (data.current_node) {
          setCurrentNode(data.current_node);
        }
        if (data.node_tasks) {
          setNodeTasks(data.node_tasks);
        }
      } else {
        // No existing state, show welcome message
        const welcomeMessage = {
          id: Date.now(),
          type: 'agent',
          text: "Welcome to SAP! Let's get you set up.\n\n1. Watch Welcome Video\n2. Review Company Policies\n3. Set up accounts\n\nI'll guide you step by step!\n\nAny questions about SAP or the onboarding process before we begin?",
          timestamp: new Date()
        };
        setChatMessages([welcomeMessage]);
      }
    } catch (error) {
      console.error('Error loading user state:', error);
      // Fallback to welcome message
        const welcomeMessage = {
          id: Date.now(),
          type: 'agent',
          text: "Welcome to SAP! Let's get you set up.\n\n1. Watch Welcome Video\n2. Review Company Policies\n3. Set up accounts\n\nI'll guide you step by step!\n\nAny questions about SAP or the onboarding process before we begin?",
          timestamp: new Date()
        };
      setChatMessages([welcomeMessage]);
    }
  };

  // Handle video popup
  const handleShowVideo = () => {
    setShowVideoPopup(true);
  };

  const handleCloseVideo = () => {
    setShowVideoPopup(false);
    // Send a message indicating video was watched
    handleUserMessage("I've watched the video");
  };

  // Handle policy popup
  const handleShowPolicy = () => {
    setCurrentPolicyIndex(0); // Start with first policy
    setShowPolicyPopup(true);
  };

  const handleClosePolicy = () => {
    setShowPolicyPopup(false);
    // Send a message indicating all policies were reviewed
    handleUserMessage("I've reviewed all company policies");
  };

  const handleNextPolicy = () => {
    if (currentPolicyIndex < policies.length - 1) {
      setCurrentPolicyIndex(currentPolicyIndex + 1);
    }
  };

  const handlePrevPolicy = () => {
    if (currentPolicyIndex > 0) {
      setCurrentPolicyIndex(currentPolicyIndex - 1);
    }
  };

  // Handle quiz popup
  const handleShowQuiz = () => {
    setShowQuizPopup(true);
  };

  const handleCloseQuiz = () => {
    setShowQuizPopup(false);
    // Send a message indicating quiz was completed
    handleUserMessage("I've completed the culture quiz");
  };

  const handleSkipQuiz = () => {
    setShowQuizPopup(false);
    // Send a message indicating quiz was skipped
    handleUserMessage("I skipped the culture quiz");
  };

  // Handle user message
  const handleUserMessage = async (message) => {
    if (!message.trim()) return;
    
    console.log('Sending message:', message);
    setIsProcessing(true);
    try {
      const response = await fetch(`http://localhost:8000/api/user/test_user/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'test_user',
          message: message
        })
      });
      
      const data = await response.json();
      
      // Handle restart case first
      if (data.restarted) {
        // Replace chat messages with restart message only
        const restartMessage = {
          id: Date.now(),
          type: 'agent',
          text: data.agent_response,
          timestamp: new Date(),
          current_node: data.current_node,
          node_tasks: data.node_tasks
        };
        setChatMessages([restartMessage]);
        setIsProcessing(false);
        return;
      }
      
      // For non-restart messages, add user message first
      const userMessage = {
        id: Date.now(),
        type: 'user',
        text: message,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, userMessage]);
      setUserInput('');
      
      // Update node information
      if (data.current_node) {
        setCurrentNode(data.current_node);
      }
      if (data.node_tasks) {
        setNodeTasks(data.node_tasks);
      }
      
      // Check if response contains video button trigger
      if (data.agent_response.includes('SHOW_VIDEO_BUTTON')) {
        // Remove the trigger text and add video button
        const cleanResponse = data.agent_response.replace('SHOW_VIDEO_BUTTON', '');
        const aiResponse = {
          id: Date.now() + 1,
          type: 'agent',
          text: cleanResponse,
          timestamp: new Date(),
          current_node: data.current_node,
          node_tasks: data.node_tasks,
          showVideoButton: true
        };
        setChatMessages(prev => [...prev, aiResponse]);
      } else if (data.agent_response.includes('SHOW_COMPANY_POLICIES_BUTTON')) {
        // Remove the trigger text and add single policy button
        const cleanResponse = data.agent_response.replace('SHOW_COMPANY_POLICIES_BUTTON', '');
        const aiResponse = {
          id: Date.now() + 1,
          type: 'agent',
          text: cleanResponse,
          timestamp: new Date(),
          current_node: data.current_node,
          node_tasks: data.node_tasks,
          showCompanyPoliciesButton: true
        };
        setChatMessages(prev => [...prev, aiResponse]);
      } else if (data.agent_response.includes('SHOW_CULTURE_QUIZ_BUTTON')) {
        // Remove the trigger text and add quiz button
        const cleanResponse = data.agent_response.replace('SHOW_CULTURE_QUIZ_BUTTON', '');
        const aiResponse = {
          id: Date.now() + 1,
          type: 'agent',
          text: cleanResponse,
          timestamp: new Date(),
          current_node: data.current_node,
          node_tasks: data.node_tasks,
          showCultureQuizButton: true
        };
        setChatMessages(prev => [...prev, aiResponse]);
      } else {
      // Add AI response
      const aiResponse = {
        id: Date.now() + 1,
        type: 'agent',
        text: data.agent_response,
          timestamp: new Date(),
          current_node: data.current_node,
          node_tasks: data.node_tasks
      };
      setChatMessages(prev => [...prev, aiResponse]);
      }
      
    } catch (error) {
      console.error('Error calling backend:', error);
      const errorResponse = {
        id: Date.now() + 1,
        type: 'agent',
        text: "Sorry, I'm having trouble connecting. Please try again.",
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorResponse]);
    }
    
    setIsProcessing(false);
  };

  return (
    <div className="onboarding-page">
      {/* Header */}
      <div className="progress-header">
        <div className="progress-container">
          <div className="progress-info">
            <span className="progress-text">
              {currentNode === 'welcome_overview' ? 'Welcome & Company Overview' : 'Personal Information & Legal Forms'}
            </span>
            <div className="node-indicator">
              <div className={`node ${currentNode === 'welcome_overview' ? 'active' : 'completed'}`}>
                Node 1: Welcome & Overview
              </div>
              <div className={`node ${currentNode === 'personal_info' ? 'active' : ''}`}>
                Node 2: Personal Information
              </div>
            </div>
          </div>
        </div>
        <div className="header-buttons">
          <button className="restart-btn" onClick={() => handleUserMessage('restart')}>
            🔄 Restart
          </button>
        <button className="back-btn" onClick={() => navigate('/main')}>
          ← Back to Main
        </button>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="chat-container">
        <div className="chat-messages">
          {chatMessages.map((message) => (
            <div key={message.id} className={`message ${message.type}-message`}>
              {message.type === 'agent' && (
                <div className="message-avatar">🤖</div>
              )}
              <div className="message-content">
                <div className="message-text">{message.text}</div>
                {message.showVideoButton && (
                  <button 
                    className="video-button"
                    onClick={handleShowVideo}
                  >
                    🎥 Show Video
                  </button>
                )}
                {message.showCompanyPoliciesButton && (
                  <div className="single-policy-button">
                    <button 
                      className="policy-button"
                      onClick={handleShowPolicy}
                    >
                      📋 Company Policies
                    </button>
                  </div>
                )}
                {message.showCultureQuizButton && (
                  <div className="single-policy-button">
                    <button 
                      className="policy-button"
                      onClick={handleShowQuiz}
                    >
                      🧠 Culture Quiz
                    </button>
                  </div>
                )}
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
              {message.type === 'user' && (
                <div className="message-avatar user-avatar">👤</div>
              )}
            </div>
          ))}
          
          {isProcessing && (
            <div className="message agent-message">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-text typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Chat Input */}
        <div className="chat-input-container">
          <div className="chat-input">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleUserMessage(userInput)}
              placeholder="Type your message..."
              disabled={isProcessing}
            />
            <button
              className="send-btn"
              onClick={() => handleUserMessage(userInput)}
              disabled={isProcessing || !userInput.trim()}
            >
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Video Popup */}
      {showVideoPopup && (
        <div className="video-popup-overlay">
          <div className="video-popup">
            <div className="video-popup-header">
              <h3>SAP Welcome Video</h3>
              <button className="close-btn" onClick={handleCloseVideo}>×</button>
            </div>
            <div className="video-content">
              <div className="video-placeholder">
                <div className="video-icon">🎥</div>
                <p>SAP Welcome Video</p>
                <p className="work-in-progress">Work in Progress</p>
                <p>This video will introduce you to SAP's mission, values, and culture.</p>
              </div>
            </div>
            <div className="video-popup-footer">
              <button className="btn-primary" onClick={handleCloseVideo}>
                I've Watched the Video
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Policy Popup */}
      {showPolicyPopup && (
        <div className="video-popup-overlay">
          <div className="video-popup policy-popup">
            <div className="video-popup-header">
              <h3>SAP Company Policies</h3>
              <button className="close-btn" onClick={handleClosePolicy}>×</button>
            </div>
            <div className="video-content">
              <div className="policy-slider">
                <div className="policy-slide">
                  <div className="policy-icon">{policies[currentPolicyIndex].icon}</div>
                  <h4>{policies[currentPolicyIndex].name}</h4>
                  <p className="work-in-progress">Work in Progress</p>
                  <p>{policies[currentPolicyIndex].description}</p>
                </div>
                
                <div className="policy-navigation">
                  <button 
                    className="nav-btn prev-btn" 
                    onClick={handlePrevPolicy}
                    disabled={currentPolicyIndex === 0}
                  >
                    ← Previous
                  </button>
                  <span className="policy-counter">
                    {currentPolicyIndex + 1} of {policies.length}
                  </span>
                  <button 
                    className="nav-btn next-btn" 
                    onClick={handleNextPolicy}
                    disabled={currentPolicyIndex === policies.length - 1}
                  >
                    Next →
                  </button>
                </div>
              </div>
            </div>
            <div className="video-popup-footer">
              <button className="btn-primary" onClick={handleClosePolicy}>
                I've Reviewed All Policies
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Culture Quiz Popup */}
      {showQuizPopup && (
        <div className="video-popup-overlay">
          <div className="video-popup quiz-popup">
            <div className="video-popup-header">
              <h3>SAP Culture Quiz</h3>
              <button className="close-btn" onClick={handleSkipQuiz}>×</button>
            </div>
            <div className="video-content">
              <div className="quiz-placeholder">
                <div className="quiz-icon">🧠</div>
                <h4>SAP Culture Quiz</h4>
                <p className="work-in-progress">Work in Progress</p>
                <p>This quiz will test your knowledge of SAP's mission, values, and culture.</p>
              </div>
            </div>
            <div className="video-popup-footer">
              <button className="btn-primary" onClick={handleCloseQuiz}>
                Finish Quiz
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Onboarding;