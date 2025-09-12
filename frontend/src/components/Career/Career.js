import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Career.css';

function Career() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('roadmap');
  const [selectedTimeline, setSelectedTimeline] = useState('5year');

  const careerRoadmap = {
    '1year': [
      {
        id: 1,
        title: 'Master Current Role',
        description: 'Excel in your current position and become the go-to person',
        timeline: '6-12 months',
        status: 'in-progress',
        progress: 70,
        milestones: ['Complete advanced training', 'Lead 2-3 projects', 'Mentor junior team members'],
        skills: ['Technical Excellence', 'Project Leadership', 'Mentoring']
      },
      {
        id: 2,
        title: 'Expand Network',
        description: 'Build relationships across departments and with industry professionals',
        timeline: '3-12 months',
        status: 'in-progress',
        progress: 45,
        milestones: ['Attend industry events', 'Join professional groups', 'Connect with senior leaders'],
        skills: ['Networking', 'Communication', 'Industry Knowledge']
      }
    ],
    '5year': [
      {
        id: 3,
        title: 'Senior Developer/Lead',
        description: 'Take on technical leadership responsibilities and guide team decisions',
        timeline: '2-3 years',
        status: 'planned',
        progress: 0,
        milestones: ['Lead technical architecture', 'Manage 3-5 developers', 'Drive technical strategy'],
        skills: ['Technical Architecture', 'Team Management', 'Strategic Thinking']
      },
      {
        id: 4,
        title: 'Technical Manager',
        description: 'Manage development teams and technical projects',
        timeline: '3-4 years',
        status: 'planned',
        progress: 0,
        milestones: ['Manage 8-12 developers', 'Oversee multiple projects', 'Interface with stakeholders'],
        skills: ['People Management', 'Project Portfolio Management', 'Stakeholder Communication']
      }
    ],
    '10year': [
      {
        id: 5,
        title: 'Engineering Director',
        description: 'Lead engineering organization and drive technical vision',
        timeline: '5-8 years',
        status: 'vision',
        progress: 0,
        milestones: ['Lead 50+ engineers', 'Define technical strategy', 'Influence company direction'],
        skills: ['Organizational Leadership', 'Strategic Planning', 'Executive Communication']
      }
    ]
  };

  const developmentAreas = [
    {
      category: 'Technical Skills',
      skills: [
        { name: 'Advanced React Patterns', level: 'Intermediate', target: 'Expert', priority: 'High' },
        { name: 'System Design', level: 'Beginner', target: 'Advanced', priority: 'Medium' },
        { name: 'Cloud Architecture', level: 'Beginner', target: 'Intermediate', priority: 'High' },
        { name: 'DevOps Practices', level: 'Beginner', target: 'Intermediate', priority: 'Medium' }
      ]
    },
    {
      category: 'Leadership Skills',
      skills: [
        { name: 'Team Management', level: 'Beginner', target: 'Advanced', priority: 'High' },
        { name: 'Strategic Planning', level: 'Beginner', target: 'Intermediate', priority: 'Medium' },
        { name: 'Change Management', level: 'Beginner', target: 'Intermediate', priority: 'Low' },
        { name: 'Executive Communication', level: 'Beginner', target: 'Advanced', priority: 'High' }
      ]
    },
    {
      category: 'Business Acumen',
      skills: [
        { name: 'Product Strategy', level: 'Beginner', target: 'Intermediate', priority: 'Medium' },
        { name: 'Financial Analysis', level: 'Beginner', target: 'Intermediate', priority: 'Low' },
        { name: 'Market Analysis', level: 'Beginner', target: 'Intermediate', priority: 'Medium' },
        { name: 'Customer Understanding', level: 'Beginner', target: 'Advanced', priority: 'High' }
      ]
    }
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High': return '#e74c3c';
      case 'Medium': return '#f39c12';
      case 'Low': return '#95a5a6';
      default: return '#95a5a6';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#43e97b';
      case 'in-progress': return '#4facfe';
      case 'planned': return '#f093fb';
      case 'vision': return '#667eea';
      default: return '#667eea';
    }
  };

  return (
    <div className="main-page">
      <div className="container">
        <div className="main-header">
          <h1>Long Term Career Growth</h1>
          <button className="btn btn-primary" onClick={() => navigate('/main')}>
            Back to Main
          </button>
        </div>
        
        <div className="main-content">
          {/* Header Section */}
          <div className="career-header">
            <h2>Plan Your Long-Term Career Path</h2>
            <p>Set ambitious goals, track your progress, and build the career you envision</p>
          </div>

          {/* Timeline Selector */}
          <div className="timeline-selector">
            <button 
              className={`timeline-btn ${selectedTimeline === '1year' ? 'active' : ''}`}
              onClick={() => setSelectedTimeline('1year')}
            >
              1 Year
            </button>
            <button 
              className={`timeline-btn ${selectedTimeline === '5year' ? 'active' : ''}`}
              onClick={() => setSelectedTimeline('5year')}
            >
              5 Years
            </button>
            <button 
              className={`timeline-btn ${selectedTimeline === '10year' ? 'active' : ''}`}
              onClick={() => setSelectedTimeline('10year')}
            >
              10 Years
            </button>
          </div>

          {/* Tab Navigation */}
          <div className="tab-navigation">
            <button 
              className={`tab-btn ${activeTab === 'roadmap' ? 'active' : ''}`}
              onClick={() => setActiveTab('roadmap')}
            >
              Career Roadmap
            </button>
            <button 
              className={`tab-btn ${activeTab === 'development' ? 'active' : ''}`}
              onClick={() => setActiveTab('development')}
            >
              Development Areas
            </button>
            <button 
              className={`tab-btn ${activeTab === 'mentorship' ? 'active' : ''}`}
              onClick={() => setActiveTab('mentorship')}
            >
              Mentorship
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'roadmap' && (
            <div className="roadmap-content">
              <h3>Your {selectedTimeline === '1year' ? '1 Year' : selectedTimeline === '5year' ? '5 Year' : '10 Year'} Career Roadmap</h3>
              <div className="roadmap-timeline">
                {careerRoadmap[selectedTimeline].map((goal, index) => (
                  <div key={goal.id} className="roadmap-goal">
                    <div className="goal-header">
                      <h4>{goal.title}</h4>
                      <span className={`goal-status ${goal.status}`}>
                        {goal.status.replace('-', ' ')}
                      </span>
                    </div>
                    <p className="goal-description">{goal.description}</p>
                    <div className="goal-timeline">
                      <span className="timeline-label">Timeline:</span>
                      <span className="timeline-value">{goal.timeline}</span>
                    </div>
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
                    <div className="goal-milestones">
                      <span className="milestones-label">Key Milestones:</span>
                      <ul className="milestones-list">
                        {goal.milestones.map((milestone, index) => (
                          <li key={index}>{milestone}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="goal-skills">
                      <span className="skills-label">Skills to Develop:</span>
                      <div className="skills-tags">
                        {goal.skills.map((skill, index) => (
                          <span key={index} className="skill-tag">{skill}</span>
                        ))}
                      </div>
                    </div>
                    <div className="goal-actions">
                      <button className="btn btn-primary">Update Progress</button>
                      <button className="btn btn-secondary">View Details</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'development' && (
            <div className="development-content">
              <h3>Skills Development Areas</h3>
              <div className="development-areas">
                {developmentAreas.map((area, index) => (
                  <div key={index} className="development-area">
                    <h4>{area.category}</h4>
                    <div className="skills-list">
                      {area.skills.map((skill, skillIndex) => (
                        <div key={skillIndex} className="skill-item">
                          <div className="skill-info">
                            <span className="skill-name">{skill.name}</span>
                            <span className="skill-levels">
                              {skill.level} → {skill.target}
                            </span>
                          </div>
                          <span 
                            className="priority-badge"
                            style={{ backgroundColor: getPriorityColor(skill.priority) }}
                          >
                            {skill.priority}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'mentorship' && (
            <div className="mentorship-content">
              <h3>Mentorship & Guidance</h3>
              <div className="mentorship-section">
                <div className="mentor-card">
                  <h4>Find a Mentor</h4>
                  <p>Connect with experienced professionals who can guide your career growth</p>
                  <button className="btn btn-primary">Browse Mentors</button>
                </div>
                <div className="mentor-card">
                  <h4>Become a Mentor</h4>
                  <p>Share your knowledge and experience with junior team members</p>
                  <button className="btn btn-secondary">Start Mentoring</button>
                </div>
                <div className="mentor-card">
                  <h4>Career Coaching</h4>
                  <p>Get personalized career advice and development planning</p>
                  <button className="btn btn-success">Book Session</button>
                </div>
              </div>
            </div>
          )}

          {/* Add New Goal */}
          <div className="add-goal-section">
            <button className="btn btn-success add-goal-btn">
              + Add New Career Goal
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Career;
