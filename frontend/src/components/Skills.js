import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Skills/Skills.css';

function Skills() {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const skillCategories = [
    { id: 'all', name: 'All Skills', color: '#667eea' },
    { id: 'technical', name: 'Technical', color: '#f093fb' },
    { id: 'soft', name: 'Soft Skills', color: '#4facfe' },
    { id: 'leadership', name: 'Leadership', color: '#43e97b' }
  ];

  const skills = [
    {
      id: 1,
      name: 'React Development',
      category: 'technical',
      level: 'Intermediate',
      progress: 75,
      description: 'Frontend development with React.js',
      learningPath: ['Basics', 'Hooks', 'State Management', 'Advanced Patterns'],
      estimatedTime: '40 hours',
      resources: ['React Docs', 'Online Course', 'Practice Projects']
    },
    {
      id: 2,
      name: 'Project Management',
      category: 'soft',
      level: 'Beginner',
      progress: 45,
      description: 'Managing projects and teams effectively',
      learningPath: ['Planning', 'Execution', 'Monitoring', 'Closure'],
      estimatedTime: '60 hours',
      resources: ['PMBOK Guide', 'Agile Training', 'Case Studies']
    },
    {
      id: 3,
      name: 'Data Analysis',
      category: 'technical',
      level: 'Advanced',
      progress: 90,
      description: 'Analyzing and interpreting data',
      learningPath: ['Statistics', 'Tools', 'Visualization', 'Machine Learning'],
      estimatedTime: '80 hours',
      resources: ['Python Course', 'Statistics Book', 'Kaggle Projects']
    },
    {
      id: 4,
      name: 'Team Leadership',
      category: 'leadership',
      level: 'Intermediate',
      progress: 60,
      description: 'Leading and motivating teams',
      learningPath: ['Communication', 'Delegation', 'Conflict Resolution', 'Vision'],
      estimatedTime: '50 hours',
      resources: ['Leadership Books', 'Mentorship', 'Workshops']
    }
  ];

  const filteredSkills = skills.filter(skill => {
    const matchesCategory = selectedCategory === 'all' || skill.category === selectedCategory;
    const matchesSearch = skill.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         skill.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getProgressColor = (progress) => {
    if (progress >= 80) return '#43e97b';
    if (progress >= 60) return '#4facfe';
    if (progress >= 40) return '#f093fb';
    return '#667eea';
  };

  return (
    <div className="main-page">
      <div className="container">
        <div className="main-header">
          <h1>Skills Development</h1>
          <button className="btn btn-primary" onClick={() => navigate('/main')}>
            Back to Main
          </button>
        </div>
        
        <div className="main-content">
          {/* Header Section */}
          <div className="skills-header">
            <h2>Develop Your Professional Skills</h2>
            <p>Track your progress, discover learning opportunities, and advance your career</p>
          </div>

          {/* Search and Filter */}
          <div className="skills-controls">
            <div className="search-box">
              <input
                type="text"
                placeholder="Search skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            <div className="category-filters">
              {skillCategories.map(category => (
                <button
                  key={category.id}
                  className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category.id)}
                  style={{ '--category-color': category.color }}
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>

          {/* Skills Grid */}
          <div className="skills-grid">
            {filteredSkills.map(skill => (
              <div key={skill.id} className="skill-card">
                <div className="skill-header">
                  <h3>{skill.name}</h3>
                  <span className={`skill-level ${skill.level.toLowerCase()}`}>
                    {skill.level}
                  </span>
                </div>
                
                <p className="skill-description">{skill.description}</p>
                
                <div className="skill-progress">
                  <div className="progress-info">
                    <span>Progress</span>
                    <span>{skill.progress}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ 
                        width: `${skill.progress}%`,
                        backgroundColor: getProgressColor(skill.progress)
                      }}
                    ></div>
                  </div>
                </div>

                <div className="skill-details">
                  <div className="detail-item">
                    <span className="detail-label">Learning Path:</span>
                    <div className="learning-path">
                      {skill.learningPath.map((step, index) => (
                        <span key={index} className="path-step">
                          {step}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="detail-item">
                    <span className="detail-label">Estimated Time:</span>
                    <span className="detail-value">{skill.estimatedTime}</span>
                  </div>
                  
                  <div className="detail-item">
                    <span className="detail-label">Resources:</span>
                    <div className="resources">
                      {skill.resources.map((resource, index) => (
                        <span key={index} className="resource-tag">
                          {resource}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="skill-actions">
                  <button className="btn btn-primary">Continue Learning</button>
                  <button className="btn btn-secondary">View Details</button>
                </div>
              </div>
            ))}
          </div>

          {/* Add New Skill */}
          <div className="add-skill-section">
            <button className="btn btn-success add-skill-btn">
              + Add New Skill
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Skills;
