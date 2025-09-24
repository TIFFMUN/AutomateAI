import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import API_CONFIG from '../../utils/apiConfig';
import './ChatBot.css';

function ChatBot() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [hasShownWelcome, setHasShownWelcome] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Show welcome notification after component mounts
  useEffect(() => {
    const timer = setTimeout(() => {
      setHasShownWelcome(true);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  const handleToggleChat = () => {
    setIsOpen(!isOpen);
    // Initialize with welcome message if opening for the first time
    if (!isOpen && messages.length === 0) {
      setMessages([{
        id: Date.now(),
        type: 'bot',
        content: `Hi ${user?.username || 'there'}! I'm your AutomateAI assistant. What questions do you have?`,
        timestamp: new Date()
      }]);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      // Call a standalone chat endpoint (not connected to onboarding)
      const requestData = { 
        message: inputMessage.trim(),
        user_id: String(user?.id || 'anonymous')
      };
      
      console.log('ChatBot: Sending request to', API_CONFIG.buildUrl('/api/chat'));
      console.log('ChatBot: Request data:', requestData);
      
      const response = await axios.post(
        API_CONFIG.buildUrl('/api/chat'),
        requestData,
        { withCredentials: true }
      );

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.response,
        timestamp: new Date(),
        ragEnabled: response.data.rag_enabled,
        sources: response.data.sources || [],
        contextDocs: response.data.context_docs || 0
      };

      console.log('ChatBot: Response received:', {
        ragEnabled: response.data.rag_enabled,
        contextDocs: response.data.context_docs,
        sources: response.data.sources,
        fallback: response.data.fallback,
        fullResponse: response.data.response
      });
      
      console.log('ChatBot: Response type check:', {
        isRagResponse: response.data.rag_enabled === true,
        hasContextDocs: response.data.context_docs > 0,
        responseLength: response.data.response?.length || 0
      });

      // Add typing delay for more natural feel with SAP-style animation
      setTimeout(() => {
        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);
        setIsLoading(false);
      }, 1500); // Slightly longer delay for better UX

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Fallback to simple responses if API fails
      const fallbackResponses = [
        "I'm here to help! What would you like to know about SAP or your career development?",
        "That's interesting! Can you tell me more about what you're working on?",
        "I'd be happy to assist you with career guidance, skills development, or any SAP-related questions.",
        "Let me help you with that. What specific area would you like to focus on?"
      ];
      
      const randomResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: randomResponse,
        timestamp: new Date()
      };
      
      setTimeout(() => {
        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);
        setIsLoading(false);
      }, 1500);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chatbot-container">
      {/* Chat Interface */}
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div className="chatbot-avatar">
              <span className="chatbot-emoji">🤖</span>
            </div>
            <div className="chatbot-info">
              <h3>AutomateAI Assistant</h3>
              <span className="status">Online</span>
            </div>
            <button className="close-btn" onClick={handleToggleChat}>
              ×
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.type}`}>
                {message.type === 'bot' && (
                  <div className="message-avatar">
                    <span className="chatbot-emoji">🤖</span>
                  </div>
                )}
                {message.type === 'user' && (
                  <div className="message-avatar" data-initial={user?.username?.charAt(0)?.toUpperCase() || 'U'}>
                    {user?.username?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                )}
                <div className="message-content">
                  <div className="message-text">
                    {message.content.split('\n').map((line, index) => (
                      <div key={index}>{line}</div>
                    ))}
                    {message.ragEnabled && message.contextDocs > 0 && (
                      <div className="rag-indicator">
                        <span className="rag-badge">Knowledge Base</span>
                      </div>
                    )}
                    {message.ragEnabled === false && (
                      <div className="rag-indicator">
                        <span className="rag-badge">Generic Response</span>
                      </div>
                    )}
                  </div>
                  <div className="message-time">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message bot">
                <div className="message-avatar">
                  <span className="chatbot-emoji">🤖</span>
                </div>
                <div className="message-content typing">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          <div className="chatbot-input">
            <div className="chatbot-input-container">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={isLoading}
                maxLength={500}
              />
              <button 
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="send-btn"
                title="Send message"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Chat Button */}
      <button 
        className={`chatbot-toggle ${isOpen ? 'open' : ''}`}
        onClick={handleToggleChat}
        aria-label={isOpen ? "Close AI Assistant" : "Open AI Assistant"}
        title={isOpen ? "Close chat" : "Open AI Assistant"}
      >
        <span className="chatbot-icon">{isOpen ? '×' : '🤖'}</span>
        {!isOpen && hasShownWelcome && (
          <div className="chatbot-notification">
            <span>!</span>
          </div>
        )}
      </button>
    </div>
  );
}

export default ChatBot;
