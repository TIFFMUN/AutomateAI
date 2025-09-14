import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Skills.css';
import API_CONFIG from '../../utils/apiConfig';

function Skills() {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('skills');
  const [recommendations, setRecommendations] = useState([]);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [userSkillsInput, setUserSkillsInput] = useState('');

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

  const courses = [
    {
      id: 1,
      title: 'Introduction to JavaScript',
      instructor: 'FreeCodeCamp',
      duration: '12 hours',
      level: 'Beginner',
      rating: 4.8,
      students: 2100000,
      price: 'FREE',
      image: 'https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?w=400&h=200&fit=crop&crop=center',
      description: 'Learn JavaScript fundamentals with hands-on projects',
      skills: ['JavaScript', 'DOM Manipulation', 'ES6', 'Async Programming'],
      category: 'technical'
    },
    {
      id: 2,
      title: 'Complete Web Development Bootcamp',
      instructor: 'Dr. Angela Yu',
      duration: '65 hours',
      level: 'Beginner to Advanced',
      rating: 4.7,
      students: 1250000,
      price: '$89.99',
      image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=200&fit=crop&crop=center',
      description: 'Learn HTML, CSS, JavaScript, React, Node.js, MongoDB and more!',
      skills: ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'MongoDB'],
      category: 'technical'
    },
    {
      id: 3,
      title: 'Communication Skills for Professionals',
      instructor: 'Coursera',
      duration: '8 hours',
      level: 'All Levels',
      rating: 4.7,
      students: 1800000,
      price: 'FREE',
      image: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop&crop=center',
      description: 'Improve your professional communication and presentation skills',
      skills: ['Public Speaking', 'Email Writing', 'Presentation Skills', 'Active Listening'],
      category: 'soft'
    },
    {
      id: 4,
      title: 'Python for Data Science',
      instructor: 'Jose Portilla',
      duration: '25 hours',
      level: 'Intermediate',
      rating: 4.6,
      students: 850000,
      price: '$94.99',
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop&crop=center',
      description: 'Master Python for data analysis, visualization, and machine learning',
      skills: ['Python', 'Pandas', 'NumPy', 'Matplotlib', 'Scikit-learn'],
      category: 'technical'
    },
    {
      id: 5,
      title: 'Excel for Business Analytics',
      instructor: 'Microsoft Learn',
      duration: '6 hours',
      level: 'Beginner',
      rating: 4.6,
      students: 950000,
      price: 'FREE',
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop&crop=center',
      description: 'Master Excel for data analysis and business intelligence',
      skills: ['Excel', 'Data Analysis', 'Pivot Tables', 'Charts', 'Formulas'],
      category: 'technical'
    },
    {
      id: 6,
      title: 'Leadership and Management',
      instructor: 'Prof. John Smith',
      duration: '15 hours',
      level: 'All Levels',
      rating: 4.8,
      students: 450000,
      price: '$79.99',
      image: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=200&fit=crop&crop=center',
      description: 'Develop essential leadership skills for modern managers',
      skills: ['Communication', 'Team Building', 'Strategic Thinking', 'Decision Making'],
      category: 'leadership'
    },
    {
      id: 7,
      title: 'Time Management Fundamentals',
      instructor: 'LinkedIn Learning',
      duration: '4 hours',
      level: 'All Levels',
      rating: 4.5,
      students: 1200000,
      price: 'FREE',
      image: 'https://images.unsplash.com/photo-1501139083538-0139583c060f?w=400&h=200&fit=crop&crop=center',
      description: 'Learn effective time management strategies for productivity',
      skills: ['Time Management', 'Productivity', 'Goal Setting', 'Prioritization'],
      category: 'soft'
    },
    {
      id: 8,
      title: 'Digital Marketing Masterclass',
      instructor: 'Sarah Johnson',
      duration: '30 hours',
      level: 'Beginner',
      rating: 4.5,
      students: 320000,
      price: '$99.99',
      image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=200&fit=crop&crop=center',
      description: 'Complete guide to digital marketing strategies and tools',
      skills: ['SEO', 'Social Media', 'Content Marketing', 'Analytics'],
      category: 'soft'
    }
  ];

  // Function to get LLM skill recommendations
  const getSkillRecommendations = async () => {
    if (!userSkillsInput.trim()) {
      alert('Please enter your current skills first');
      return;
    }

    setIsLoadingRecommendations(true);
    try {
      // Simulate API call to backend for LLM recommendations
      const response = await fetch(API_CONFIG.buildUrl('/api/skills/recommendations'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_skills: userSkillsInput,
          user_profile: 'professional'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      } else {
        // Fallback recommendations if API fails
        setRecommendations([
          {
            skill: 'Machine Learning',
            reason: 'High demand in tech industry',
            difficulty: 'Advanced',
            estimatedTime: '3-6 months',
            resources: ['Coursera ML Course', 'Kaggle Competitions', 'TensorFlow Tutorials']
          },
          {
            skill: 'Cloud Computing (AWS)',
            reason: 'Essential for modern software development',
            difficulty: 'Intermediate',
            estimatedTime: '2-4 months',
            resources: ['AWS Training', 'Hands-on Labs', 'Certification Prep']
          },
          {
            skill: 'Agile Project Management',
            reason: 'Improves team collaboration and project success',
            difficulty: 'Beginner',
            estimatedTime: '1-2 months',
            resources: ['Scrum Master Training', 'Agile Books', 'Practice Projects']
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      // Fallback recommendations
      setRecommendations([
        {
          skill: 'Machine Learning',
          reason: 'High demand in tech industry',
          difficulty: 'Advanced',
          estimatedTime: '3-6 months',
          resources: ['Coursera ML Course', 'Kaggle Competitions', 'TensorFlow Tutorials']
        },
        {
          skill: 'Cloud Computing (AWS)',
          reason: 'Essential for modern software development',
          difficulty: 'Intermediate',
          estimatedTime: '2-4 months',
          resources: ['AWS Training', 'Hands-on Labs', 'Certification Prep']
        },
        {
          skill: 'Agile Project Management',
          reason: 'Improves team collaboration and project success',
          difficulty: 'Beginner',
          estimatedTime: '1-2 months',
          resources: ['Scrum Master Training', 'Agile Books', 'Practice Projects']
        }
      ]);
    }
    setIsLoadingRecommendations(false);
  };

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
    <div className="main-page skills-page">
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

          {/* Tab Navigation */}
          <div className="tab-navigation">
            <button 
              className={`tab-btn ${activeTab === 'skills' ? 'active' : ''}`}
              onClick={() => setActiveTab('skills')}
            >
              My Skills
            </button>
            <button 
              className={`tab-btn ${activeTab === 'courses' ? 'active' : ''}`}
              onClick={() => setActiveTab('courses')}
            >
              Explore New Courses
            </button>
            <button 
              className={`tab-btn ${activeTab === 'recommendations' ? 'active' : ''}`}
              onClick={() => setActiveTab('recommendations')}
            >
              AI Recommendations
            </button>
          </div>

          {/* Skills Tab Content */}
          {activeTab === 'skills' && (
            <>
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

            </>
          )}

          {/* Courses Tab Content */}
          {activeTab === 'courses' && (
            <div className="courses-section">
              <div className="courses-header">
                <h3>Featured Courses</h3>
                <p>Discover top-rated courses to enhance your skills</p>
              </div>
              
              <div className="courses-grid">
                {courses.map(course => (
                  <div key={course.id} className="course-card">
                    <div className="course-image">
                      <img src={course.image} alt={course.title} />
                      <div className="course-level">{course.level}</div>
                    </div>
                    
                    <div className="course-content">
                      <h4>{course.title}</h4>
                      <p className="course-instructor">by {course.instructor}</p>
                      <p className="course-description">{course.description}</p>
                      
                      <div className="course-stats">
                        <div className="stat">
                          <span className="stat-icon">⭐</span>
                          <span>{course.rating}</span>
                        </div>
                        <div className="stat">
                          <span className="stat-icon">👥</span>
                          <span>{course.students.toLocaleString()}</span>
                        </div>
                        <div className="stat">
                          <span className="stat-icon">⏱️</span>
                          <span>{course.duration}</span>
                        </div>
                      </div>
                      
                      <div className="course-skills">
                        {course.skills.map((skill, index) => (
                          <span key={index} className="skill-tag">{skill}</span>
                        ))}
                      </div>
                      
                      <div className="course-footer">
                        <span className="course-price">{course.price}</span>
                        <button className="btn btn-primary">Enroll Now</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Recommendations Tab Content */}
          {activeTab === 'recommendations' && (
            <div className="recommendations-section">
              <div className="recommendations-header">
                <h3>AI-Powered Skill Recommendations</h3>
                <p>Get personalized skill recommendations based on your current abilities</p>
              </div>
              
              <div className="recommendations-input">
                {isLoadingRecommendations ? (
                  <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Getting your personalized skill recommendations...</p>
                  </div>
                ) : (
                  <>
                    <textarea
                      placeholder="Tell us about your current skills, experience, and career goals..."
                      value={userSkillsInput}
                      onChange={(e) => setUserSkillsInput(e.target.value)}
                      className="skills-input"
                      rows="4"
                    />
                    <button 
                      onClick={getSkillRecommendations}
                      className="recommendations-btn"
                      disabled={isLoadingRecommendations}
                    >
                      Get Recommendations
                    </button>
                  </>
                )}
              </div>
              
              {recommendations.length > 0 ? (
                <div className="recommendations-results">
                  <h4>Recommended Skills for You</h4>
                  <div className="recommendations-grid">
                    {recommendations.map((rec, index) => (
                      <div key={index} className="recommendation-card">
                        <div className="recommendation-header">
                          <h5>{rec.skill}</h5>
                          <span className={`difficulty-badge ${rec.difficulty.toLowerCase()}`}>
                            {rec.difficulty}
                          </span>
                        </div>
                        
                        <p className="recommendation-reason">{rec.reason}</p>
                        
                        <div className="recommendation-details">
                          <div className="detail">
                            <span className="detail-label">Time to Learn:</span>
                            <span className="detail-value">{rec.estimatedTime}</span>
                          </div>
                        </div>
                        
                       
                        <div className="recommendation-resources">
                          <span className="resources-label">Recommended Resources:</span>
                          <div className="resources-list">
                            {rec.resources.map((resource, idx) => (
                              <a 
                                key={idx} 
                                href={typeof resource === 'string' ? '#' : resource.link} 
                                target="_blank" 
                                rel="noopener noreferrer" 
                                className="resource-link"
                              >
                                {typeof resource === 'string' ? resource : resource.title}
                              </a>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Skills;
