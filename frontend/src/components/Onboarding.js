import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Onboarding.css';

function Onboarding() {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [userInput, setUserInput] = useState('');

  // Initialize chat
  useEffect(() => {
    if (chatMessages.length === 0) {
      const welcomeMessage = {
        id: Date.now(),
        type: 'agent',
        text: "🎉 Welcome aboard! I'm your AI Assistant. How can I help you today?",
        timestamp: new Date()
      };
      
      setChatMessages([welcomeMessage]);
    }
  }, []);

  // Handle user message
  const handleUserMessage = async (message) => {
    if (!message.trim()) return;
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: message,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMessage]);
    setUserInput('');
    
    // Call backend API
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
      
      // Add AI response
      const aiResponse = {
        id: Date.now() + 1,
        type: 'agent',
        text: data.agent_response,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, aiResponse]);
      
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
            <span className="progress-text">AI Assistant</span>
          </div>
        </div>
        <button className="back-btn" onClick={() => navigate('/main')}>
          ← Back to Main
        </button>
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
    </div>
  );
}

export default Onboarding;