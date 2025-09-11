import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Performance/Performance.css';

function Performance() {
  const navigate = useNavigate();
  const [selectedPeriod, setSelectedPeriod] = useState('current');
  const [activeTab, setActiveTab] = useState('overview');

  const performanceData = {
    current: {
      overall: 4.2,
      categories: [
        { name: 'Technical Skills', score: 4.5, target: 4.0, trend: 'up' },
        { name: 'Communication', score: 4.0, target: 4.0, trend: 'stable' },
        { name: 'Leadership', score: 3.8, target: 4.0, trend: 'up' },
        { name: 'Innovation', score: 4.5, target: 4.0, trend: 'up' },
        { name: 'Teamwork', score: 4.3, target: 4.0, trend: 'stable' }
      ]
    },
    previous: {
      overall: 4.0,
      categories: [
        { name: 'Technical Skills', score: 4.2, target: 4.0, trend: 'up' },
        { name: 'Communication', score: 3.8, target: 4.0, trend: 'up' },
        { name: 'Leadership', score: 3.5, target: 4.0, trend: 'up' },
        { name: 'Innovation', score: 4.2, target: 4.0, trend: 'up' },
        { name: 'Teamwork', score: 4.1, target: 4.0, trend: 'stable' }
      ]
    }
  };

  const feedbackHistory = [
    {
      id: 1,
      date: '2024-01-15',
      reviewer: 'Sarah Johnson',
      role: 'Senior Manager',
      rating: 4.5,
      feedback: 'Excellent work on the Q4 project. Your technical skills and leadership have been outstanding. Continue to mentor junior team members.',
      areas: ['Technical Skills', 'Leadership'],
      actionItems: ['Lead next project planning session', 'Share best practices with team']
    },
    {
      id: 2,
      date: '2024-01-01',
      reviewer: 'Mike Chen',
      role: 'Project Lead',
      rating: 4.0,
      feedback: 'Great collaboration on the client project. Communication could be improved in cross-functional meetings.',
      areas: ['Teamwork', 'Communication'],
      actionItems: ['Prepare agenda for meetings', 'Follow up with action items']
    }
  ];

  const goals = [
    {
      id: 1,
      title: 'Improve Public Speaking',
      description: 'Present confidently in team meetings and client presentations',
      target: 'Q2 2024',
      progress: 60,
      status: 'in-progress'
    },
    {
      id: 2,
      title: 'Master Advanced React Patterns',
      description: 'Learn and implement advanced React concepts and patterns',
      target: 'Q3 2024',
      progress: 30,
      status: 'in-progress'
    },
    {
      id: 3,
      title: 'Lead a Major Project',
      description: 'Take ownership of a significant project from start to finish',
      target: 'Q4 2024',
      progress: 0,
      status: 'planned'
    }
  ];

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      case 'stable': return '➡️';
      default: return '➡️';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#43e97b';
      case 'in-progress': return '#4facfe';
      case 'planned': return '#f093fb';
      default: return '#667eea';
    }
  };

  return (
    <div className="main-page">
      <div className="container">
        <div className="main-header">
          <h1>Performance Feedback</h1>
          <button className="btn btn-primary" onClick={() => navigate('/main')}>
            Back to Main
          </button>
        </div>
        
        <div className="main-content">
          {/* Header Section */}
          <div className="performance-header">
            <h2>Track Your Performance and Growth</h2>
            <p>Monitor your progress, receive feedback, and set goals for continuous improvement</p>
          </div>

          {/* Period Selector */}
          <div className="period-selector">
            <button 
              className={`period-btn ${selectedPeriod === 'current' ? 'active' : ''}`}
              onClick={() => setSelectedPeriod('current')}
            >
              Current Period
            </button>
            <button 
              className={`period-btn ${selectedPeriod === 'previous' ? 'active' : ''}`}
              onClick={() => setSelectedPeriod('previous')}
            >
              Previous Period
            </button>
          </div>

          {/* Tab Navigation */}
          <div className="tab-navigation">
            <button 
              className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button 
              className={`tab-btn ${activeTab === 'feedback' ? 'active' : ''}`}
              onClick={() => setActiveTab('feedback')}
            >
              Feedback History
            </button>
            <button 
              className={`tab-btn ${activeTab === 'goals' ? 'active' : ''}`}
              onClick={() => setActiveTab('goals')}
            >
              Goals & Objectives
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="overview-content">
              {/* Overall Score */}
              <div className="overall-score">
                <div className="score-circle">
                  <span className="score-number">{performanceData[selectedPeriod].overall}</span>
                  <span className="score-label">Overall Rating</span>
                </div>
                <div className="score-details">
                  <h3>Performance Summary</h3>
                  <p>You're performing above target in most areas. Keep up the excellent work!</p>
                </div>
              </div>

              {/* Category Breakdown */}
              <div className="category-breakdown">
                <h3>Performance by Category</h3>
                <div className="category-grid">
                  {performanceData[selectedPeriod].categories.map((category, index) => (
                    <div key={index} className="category-card">
                      <div className="category-header">
                        <h4>{category.name}</h4>
                        <span className="trend-icon">{getTrendIcon(category.trend)}</span>
                      </div>
                      <div className="category-score">
                        <span className="current-score">{category.score}</span>
                        <span className="target-score">/ {category.target}</span>
                      </div>
                      <div className="score-bar">
                        <div 
                          className="score-fill" 
                          style={{ width: `${(category.score / category.target) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'feedback' && (
            <div className="feedback-content">
              <h3>Recent Feedback</h3>
              <div className="feedback-list">
                {feedbackHistory.map(feedback => (
                  <div key={feedback.id} className="feedback-card">
                    <div className="feedback-header">
                      <div className="feedback-meta">
                        <span className="reviewer">{feedback.reviewer}</span>
                        <span className="role">{feedback.role}</span>
                        <span className="date">{feedback.date}</span>
                      </div>
                      <div className="feedback-rating">
                        <span className="rating">{feedback.rating}/5.0</span>
                      </div>
                    </div>
                    <p className="feedback-text">{feedback.feedback}</p>
                    <div className="feedback-areas">
                      <span className="areas-label">Key Areas:</span>
                      {feedback.areas.map((area, index) => (
                        <span key={index} className="area-tag">{area}</span>
                      ))}
                    </div>
                    <div className="action-items">
                      <span className="actions-label">Action Items:</span>
                      {feedback.actionItems.map((item, index) => (
                        <span key={index} className="action-item">{item}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'goals' && (
            <div className="goals-content">
              <h3>Performance Goals</h3>
              <div className="goals-list">
                {goals.map(goal => (
                  <div key={goal.id} className="goal-card">
                    <div className="goal-header">
                      <h4>{goal.title}</h4>
                      <span className={`goal-status ${goal.status}`}>
                        {goal.status.replace('-', ' ')}
                      </span>
                    </div>
                    <p className="goal-description">{goal.description}</p>
                    <div className="goal-progress">
                      <div className="progress-info">
                        <span>Progress</span>
                        <span>{goal.progress}%</span>
                      </div>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ 
                            width: `${goal.progress}%`,
                            backgroundColor: getStatusColor(goal.status)
                          }}
                        ></div>
                      </div>
                    </div>
                    <div className="goal-target">
                      <span className="target-label">Target:</span>
                      <span className="target-date">{goal.target}</span>
                    </div>
                    <div className="goal-actions">
                      <button className="btn btn-primary">Update Progress</button>
                      <button className="btn btn-secondary">View Details</button>
                    </div>
                  </div>
                ))}
              </div>
              <button className="btn btn-success add-goal-btn">
                + Add New Goal
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Performance;
