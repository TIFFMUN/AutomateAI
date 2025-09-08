import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './Onboarding.css';

function Onboarding() {
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  
  // Chat state
  const [isProcessing, setIsProcessing] = useState(false);
  const [showLoading, setShowLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  
  // Node state
  const [currentNode, setCurrentNode] = useState('welcome_overview');
  
  // Points state
  const [totalPoints, setTotalPoints] = useState(0);
  const [pointsEarned, setPointsEarned] = useState(0);
  const [showPointsAnimation, setShowPointsAnimation] = useState(false);
  
  // Popup states
  const [showVideoPopup, setShowVideoPopup] = useState(false);
  const [showPolicyPopup, setShowPolicyPopup] = useState(false);
  const [showQuizPopup, setShowQuizPopup] = useState(false);
  const [showEmployeePerksPopup, setShowEmployeePerksPopup] = useState(false);
  const [showPersonalInfoFormPopup, setShowPersonalInfoFormPopup] = useState(false);
  
  // Form state
  const [personalInfoForm, setPersonalInfoForm] = useState({
    fullName: '',
    preferredName: '',
    email: '',
    phone: '',
    address: '',
    emergencyContactName: '',
    emergencyContactPhone: '',
    relationship: '',
    employmentContract: false,
    nda: false,
    taxWithholding: false
  });
  
  // Slider states
  const [currentPolicyIndex, setCurrentPolicyIndex] = useState(0);
  const [currentPerksIndex, setCurrentPerksIndex] = useState(0);

  // Data constants
  const policies = [
    { name: 'Code of Conduct', icon: '📋', description: 'Ethical principles and standards of behavior expected of all SAP employees.' },
    { name: 'Data Protection', icon: '🔒', description: 'Guidelines for handling personal and sensitive data in compliance with regulations.' },
    { name: 'Workplace Safety', icon: '🛡️', description: 'Safety protocols and procedures to ensure a secure working environment.' },
    { name: 'Diversity & Inclusion', icon: '🤝', description: 'Commitment to creating an inclusive workplace that values diversity.' }
  ];

  const employeePerks = [
    { name: 'Health & Wellness', icon: '🏥', description: 'Comprehensive health insurance, dental, vision, and wellness programs for you and your family.' },
    { name: 'Learning & Development', icon: '📚', description: 'Access to training programs, conferences, certifications, and continuous learning opportunities.' },
    { name: 'Work-Life Balance', icon: '⚖️', description: 'Flexible working arrangements, paid time off, and programs to support work-life integration.' },
    { name: 'Career Growth', icon: '🚀', description: 'Mentorship programs, internal mobility, and clear career progression paths within SAP.' }
  ];

  // Initialize chat with state loading
  useEffect(() => {
    loadUserState();
  }, []);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  // Auto-focus input field when component mounts
  useEffect(() => {
    const inputElement = document.querySelector('.chat-input input');
    if (inputElement) {
      inputElement.focus();
    }
  }, []);

  // Auto-focus input after each message
  useEffect(() => {
    const inputElement = document.querySelector('.chat-input input');
    if (inputElement && !isProcessing) {
      inputElement.focus();
    }
  }, [chatMessages, isProcessing]);

  // Delayed loading indicator
  useEffect(() => {
    let timeoutId;
    if (isProcessing) {
      // Show loading indicator after 1 second delay
      timeoutId = setTimeout(() => {
        setShowLoading(true);
      }, 1000);
    } else {
      setShowLoading(false);
    }
    
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [isProcessing]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

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
        if (data.total_points !== undefined) {
          setTotalPoints(data.total_points);
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

  // Navigation helpers
  const navigateSlider = (type, direction) => {
    const isPolicy = type === 'policy';
    const currentIndex = isPolicy ? currentPolicyIndex : currentPerksIndex;
    const setCurrentIndex = isPolicy ? setCurrentPolicyIndex : setCurrentPerksIndex;
    const maxIndex = isPolicy ? policies.length - 1 : employeePerks.length - 1;
    
    if (direction === 'next' && currentIndex < maxIndex) {
      setCurrentIndex(currentIndex + 1);
    } else if (direction === 'prev' && currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
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

  // Handle employee perks popup
  const handleShowEmployeePerks = () => {
    setShowEmployeePerksPopup(true);
  };

  const handleCloseEmployeePerks = () => {
    setShowEmployeePerksPopup(false);
    // Send a message indicating perks were reviewed
    handleUserMessage("I've reviewed the employee perks");
  };

  // Handle personal info form popup
  const handleShowPersonalInfoForm = () => {
    setShowPersonalInfoFormPopup(true);
  };

  const handleClosePersonalInfoForm = () => {
    setShowPersonalInfoFormPopup(false);
    // Send form data to agent for intelligent analysis
    const formData = {
      fullName: personalInfoForm.fullName,
      preferredName: personalInfoForm.preferredName,
      email: personalInfoForm.email,
      phone: personalInfoForm.phone,
      address: personalInfoForm.address,
      emergencyContactName: personalInfoForm.emergencyContactName,
      emergencyContactPhone: personalInfoForm.emergencyContactPhone,
      relationship: personalInfoForm.relationship,
      employmentContract: personalInfoForm.employmentContract,
      nda: personalInfoForm.nda,
      taxWithholding: personalInfoForm.taxWithholding
    };
    
    // Send detailed form data to agent
    handleUserMessage(`I've submitted the personal information form with the following details: ${JSON.stringify(formData)}`);
  };

  const handleFormInputChange = (field, value) => {
    setPersonalInfoForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSkipPersonalInfoForm = () => {
    setShowPersonalInfoFormPopup(false);
    // Send a message indicating form was skipped
    handleUserMessage("I skipped the personal information form");
  };

  // Handle user message
  const handleUserMessage = async (message) => {
    if (!message.trim()) return;
    
    console.log('Sending message:', message);
    
    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: message,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMessage]);
    setUserInput('');
    
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
          current_node: data.current_node
        };
        setChatMessages([restartMessage]);
        setTotalPoints(0);
        setPointsEarned(0);
        setShowPointsAnimation(false);
        
        setIsProcessing(false);
        return;
      }
      
      // Update node information
      if (data.current_node) {
        setCurrentNode(data.current_node);
      }
      
      // Handle points
      if (data.points_earned && data.points_earned > 0) {
        setPointsEarned(data.points_earned);
        setTotalPoints(data.total_points);
        setShowPointsAnimation(true);
        
        // Hide animation after 3 seconds
        setTimeout(() => {
          setShowPointsAnimation(false);
        }, 3000);
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
          showCultureQuizButton: true
        };
        setChatMessages(prev => [...prev, aiResponse]);
      } else if (data.agent_response.includes('SHOW_PERSONAL_INFO_FORM_BUTTON')) {
        // Remove the trigger text and add personal info form button
        const cleanResponse = data.agent_response.replace('SHOW_PERSONAL_INFO_FORM_BUTTON', '');
        const aiResponse = {
          id: Date.now() + 1,
          type: 'agent',
          text: cleanResponse,
          timestamp: new Date(),
          current_node: data.current_node,
          showPersonalInfoFormButton: true
        };
        setChatMessages(prev => [...prev, aiResponse]);
      } else if (data.agent_response.includes('SHOW_EMPLOYEE_PERKS_BUTTON')) {
        // Remove the trigger text and add employee perks button
        const cleanResponse = data.agent_response.replace('SHOW_EMPLOYEE_PERKS_BUTTON', '');
        const aiResponse = {
          id: Date.now() + 1,
          type: 'agent',
          text: cleanResponse,
          timestamp: new Date(),
          current_node: data.current_node,
          showEmployeePerksButton: true
        };
        setChatMessages(prev => [...prev, aiResponse]);
      } else {
      // Add AI response
      const aiResponse = {
        id: Date.now() + 1,
        type: 'agent',
        text: data.agent_response,
        timestamp: new Date(),
        current_node: data.current_node
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
              {currentNode === 'welcome_overview' ? 'Welcome & Company Overview' : 
               currentNode === 'personal_info' ? 'SAP Onboarding' : 
               currentNode === 'onboarding_complete' ? 'Onboarding Complete!' :
               'Account Setup'}
            </span>
            <div className="node-indicator">
              <div className={`node ${currentNode === 'welcome_overview' ? 'active' : 'completed'}`}>
                Node 1: Company Welcome
              </div>
              <div className={`node ${currentNode === 'personal_info' ? 'active' : currentNode === 'account_setup' || currentNode === 'onboarding_complete' ? 'completed' : ''}`}>
                Node 2: Personal Information
              </div>
              <div className={`node ${currentNode === 'account_setup' ? 'active' : currentNode === 'onboarding_complete' ? 'completed' : ''}`}>
                Node 3: Account Setup
              </div>
            </div>
          </div>
        </div>
        <div className="header-buttons">
          <button className="restart-btn" onClick={() => handleUserMessage('restart')}>
            Restart
          </button>
        <button className="back-btn" onClick={() => navigate('/main')}>
          Back to Main
        </button>
        </div>
      </div>

      {/* Points Display */}
      <div className="points-display">
        <div className="points-container">
          <div className="points-icon">⭐</div>
          <div className="points-text">
            <span className="points-label">Points</span>
            <span className="points-value">{totalPoints}</span>
          </div>
        </div>
        
        {/* Points Animation */}
        {showPointsAnimation && (
          <div className="points-animation">
            <div className="points-earned">+{pointsEarned}</div>
          </div>
        )}
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
                <div className="message-text-wrapper">
                  <div className="message-text">{message.text}</div>
                  <div className="message-time">{message.timestamp.toLocaleTimeString()}</div>
                </div>
                {message.showVideoButton && (
                  <button 
                    className="video-button"
                    onClick={handleShowVideo}
                  >
                    🎥 Show Video
                  </button>
                )}
                {message.showCompanyPoliciesButton && (
                  <button 
                    className="video-button"
                    onClick={handleShowPolicy}
                  >
                    📋 Company Policies
                  </button>
                )}
                {message.showCultureQuizButton && (
                  <button 
                    className="video-button"
                    onClick={handleShowQuiz}
                  >
                    🧠 Culture Quiz
                  </button>
                )}
                {message.showPersonalInfoFormButton && (
                  <button 
                    className="video-button"
                    onClick={handleShowPersonalInfoForm}
                  >
                    📝 Personal Information Form
                  </button>
                )}
                {message.showEmployeePerksButton && (
                  <button 
                    className="video-button"
                    onClick={handleShowEmployeePerks}
                  >
                    🎁 Employee Perks
                  </button>
                )}
              </div>
              {message.type === 'user' && (
                <div className="message-avatar user-avatar">👤</div>
              )}
            </div>
          ))}
          
          {showLoading && (
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
          <div ref={messagesEndRef} />
        </div>
        
        {/* Chat Input */}
        <div className="chat-input-container">
          <div className="chat-input">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey && userInput.trim()) {
                  e.preventDefault();
                  handleUserMessage(userInput);
                  setUserInput(''); // Clear input after sending
                }
              }}
              placeholder="Type your message and press Enter..."
              disabled={isProcessing}
              autoFocus
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
                    onClick={() => navigateSlider('policy', 'prev')}
                    disabled={currentPolicyIndex === 0}
                  >
                    ← Previous
                  </button>
                  <span className="policy-counter">
                    {currentPolicyIndex + 1} of {policies.length}
                  </span>
                  <button 
                    className="nav-btn next-btn" 
                    onClick={() => navigateSlider('policy', 'next')}
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
      
      {/* Employee Perks Popup */}
      {showEmployeePerksPopup && (
        <div className="video-popup-overlay">
          <div className="video-popup perks-popup">
            <div className="video-popup-header">
              <h3>SAP Employee Perks</h3>
              <button className="close-btn" onClick={handleCloseEmployeePerks}>×</button>
            </div>
            <div className="video-content">
              <div className="policy-slider">
                <div className="policy-slide">
                  <div className="policy-icon">{employeePerks[currentPerksIndex].icon}</div>
                  <h4>{employeePerks[currentPerksIndex].name}</h4>
                  <p className="work-in-progress">Work in Progress</p>
                  <p>{employeePerks[currentPerksIndex].description}</p>
                </div>
                
                <div className="policy-navigation">
                  <button 
                    className="nav-btn prev-btn" 
                    onClick={() => navigateSlider('perks', 'prev')}
                    disabled={currentPerksIndex === 0}
                  >
                    ← Previous
                  </button>
                  <span className="policy-counter">
                    {currentPerksIndex + 1} of {employeePerks.length}
                  </span>
                  <button 
                    className="nav-btn next-btn" 
                    onClick={() => navigateSlider('perks', 'next')}
                    disabled={currentPerksIndex === employeePerks.length - 1}
                  >
                    Next →
                  </button>
                </div>
              </div>
            </div>
            <div className="video-popup-footer">
              <button className="btn-primary" onClick={handleCloseEmployeePerks}>
                I've Reviewed All Perks
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Personal Information Form Popup */}
      {showPersonalInfoFormPopup && (
        <div className="video-popup-overlay">
          <div className="video-popup personal-info-popup">
            <div className="video-popup-header">
              <h3>Personal Information Form</h3>
              <button className="close-btn" onClick={handleSkipPersonalInfoForm}>×</button>
            </div>
            <div className="video-content">
              <div className="personal-info-form">
                <div className="form-section">
                  <h4>👤 Personal Information</h4>
                  <div className="form-group">
                    <label>Full Name:</label>
                    <input 
                      type="text" 
                      placeholder="Enter your full name" 
                      value={personalInfoForm.fullName}
                      onChange={(e) => handleFormInputChange('fullName', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Preferred Name:</label>
                    <input 
                      type="text" 
                      placeholder="Enter your preferred name" 
                      value={personalInfoForm.preferredName}
                      onChange={(e) => handleFormInputChange('preferredName', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Email Address:</label>
                    <input 
                      type="text" 
                      placeholder="Enter your email address" 
                      value={personalInfoForm.email}
                      onChange={(e) => handleFormInputChange('email', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Phone Number:</label>
                    <input 
                      type="text" 
                      placeholder="Enter your phone number" 
                      value={personalInfoForm.phone}
                      onChange={(e) => handleFormInputChange('phone', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Home Address:</label>
                    <textarea 
                      placeholder="Enter your home address"
                      value={personalInfoForm.address}
                      onChange={(e) => handleFormInputChange('address', e.target.value)}
                    ></textarea>
                  </div>
                </div>
                
                <div className="form-section">
                  <h4>🚨 Emergency Contact</h4>
                  <div className="form-group">
                    <label>Emergency Contact Name:</label>
                    <input 
                      type="text" 
                      placeholder="Enter emergency contact name" 
                      value={personalInfoForm.emergencyContactName}
                      onChange={(e) => handleFormInputChange('emergencyContactName', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Emergency Contact Phone:</label>
                    <input 
                      type="text" 
                      placeholder="Enter emergency contact phone" 
                      value={personalInfoForm.emergencyContactPhone}
                      onChange={(e) => handleFormInputChange('emergencyContactPhone', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Relationship:</label>
                    <input 
                      type="text" 
                      placeholder="e.g., Spouse, Parent, Sibling" 
                      value={personalInfoForm.relationship}
                      onChange={(e) => handleFormInputChange('relationship', e.target.value)}
                    />
                  </div>
                </div>
                
                <div className="form-section">
                  <h4>📋 Legal/Compliance Forms</h4>
                  <div className="form-group checkbox-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={personalInfoForm.employmentContract}
                        onChange={(e) => handleFormInputChange('employmentContract', e.target.checked)}
                      />
                      I acknowledge the employment contract
                    </label>
                  </div>
                  <div className="form-group checkbox-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={personalInfoForm.nda}
                        onChange={(e) => handleFormInputChange('nda', e.target.checked)}
                      />
                      I agree to the non-disclosure agreement
                    </label>
                  </div>
                  <div className="form-group checkbox-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={personalInfoForm.taxWithholding}
                        onChange={(e) => handleFormInputChange('taxWithholding', e.target.checked)}
                      />
                      I understand the tax withholding requirements
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <div className="video-popup-footer">
              <button className="btn-primary" onClick={handleClosePersonalInfoForm}>
                Submit Information
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Onboarding;