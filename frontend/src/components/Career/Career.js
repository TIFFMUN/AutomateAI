import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Career.css';
import apiConfig from '../../utils/apiConfig';
import { useAuth } from '../../contexts/AuthContext';


function Career() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeSegment, setActiveSegment] = useState('quiz');
  const [quizStep, setQuizStep] = useState(0);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [jobsToShow, setJobsToShow] = useState(4);
  const [isLoading, setIsLoading] = useState(false);
  const [careerResponse, setCareerResponse] = useState(null);
  const [error, setError] = useState(null);
  const [totalPoints, setTotalPoints] = useState(0);
  const [pointsEarned, setPointsEarned] = useState(0);
  const [showPointsAnimation, setShowPointsAnimation] = useState(false);
  
  // Career Oracle states
  const [oracleData, setOracleData] = useState(null);
  const [oracleLoading, setOracleLoading] = useState(false);
  const [oracleError, setOracleError] = useState(null);
  const [selectedRole, setSelectedRole] = useState('');
  const [experienceYears, setExperienceYears] = useState('');
  const [careerGoal, setCareerGoal] = useState('');


  // Career Coach AI Quiz Data
  const quizQuestions = [
      {
        id: 1,
      question: "What is your primary career goal for the next 2-3 years?",
      options: [
        { value: "technical_expert", label: "Become a technical expert in my field" },
        { value: "team_lead", label: "Move into team leadership role" },
        { value: "management", label: "Transition to management" },
        { value: "entrepreneur", label: "Start my own business" }
      ]
      },
      {
        id: 2,
      question: "Which work environment motivates you most?",
      options: [
        { value: "startup", label: "Fast-paced startup environment" },
        { value: "enterprise", label: "Large enterprise with structure" },
        { value: "consulting", label: "Consulting with diverse clients" },
        { value: "remote", label: "Remote/flexible work arrangement" }
      ]
    },
    {
      id: 3,
      question: "What type of learning excites you most?",
      options: [
        { value: "technical", label: "Deep technical skills and certifications" },
        { value: "business", label: "Business strategy and market understanding" },
        { value: "leadership", label: "Leadership and people management" },
        { value: "innovation", label: "Cutting-edge technology and innovation" }
      ]
    },
    {
      id: 4,
      question: "How do you prefer to solve problems?",
      options: [
        { value: "analytical", label: "Through data analysis and research" },
        { value: "collaborative", label: "By collaborating with others" },
        { value: "creative", label: "Using creative and innovative approaches" },
        { value: "systematic", label: "Following systematic processes" }
      ]
    },
    {
      id: 5,
      question: "What's most important to you in a career?",
      options: [
        { value: "impact", label: "Making a significant impact" },
        { value: "growth", label: "Continuous personal growth" },
        { value: "stability", label: "Job security and stability" },
        { value: "recognition", label: "Recognition and advancement" }
      ]
    }
  ];


  // SAP Jobs Data
  const sapJobs = [
    {
      id: 1,
      title: "SAP FICO Consultant",
      experience: "3-5 years",
      salary: "$90,000 - $120,000",
      description: "Seeking experienced SAP FICO consultant to implement and support financial modules.",
      posted: "2 days ago",
      featured: true
    },
    {
      id: 2,
      title: "SAP MM Consultant",
      experience: "2-4 years",
      salary: "$80,000 - $100,000",
      description: "Join our team to implement SAP MM solutions for supply chain optimization.",
      posted: "1 week ago",
      featured: false
    },
    {
      id: 3,
      title: "SAP HANA Developer",
      experience: "4-6 years",
      salary: "$110,000 - $140,000",
      description: "Develop and optimize SAP HANA solutions for enterprise data management.",
      posted: "3 days ago",
      featured: true
    },
    {
      id: 4,
      title: "SAP SuccessFactors Consultant",
      experience: "2-3 years",
      salary: "$75,000 - $95,000",
      description: "Implement and configure SAP SuccessFactors modules for HR transformation.",
      posted: "5 days ago",
      featured: false
    },
    {
      id: 5,
      title: "SAP Security Consultant",
      experience: "3-5 years",
      salary: "$95,000 - $115,000",
      description: "Design and implement SAP security solutions for enterprise environments.",
      posted: "1 week ago",
      featured: false
    }
  ];


  const handleQuizAnswer = (questionId, answer) => {
    setQuizAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };


  const nextQuizStep = async () => {
    if (quizStep < quizQuestions.length - 1) {
      setQuizStep(quizStep + 1);
    } else {
      // Quiz completed, show results and get AI recommendations
      setShowResults(true);
      await getCareerRecommendations();
    }
  };


  const prevQuizStep = () => {
    if (quizStep > 0) {
      setQuizStep(quizStep - 1);
    }
  };


  const resetQuiz = () => {
    setQuizStep(0);
    setQuizAnswers({});
    setShowResults(false);
    setCareerResponse(null);
    setError(null);
  };


  const loadMoreJobs = () => {
    setJobsToShow(sapJobs.length);
  };

  // Career Oracle API call
  const predictCareerPath = async () => {
    // Clear previous errors
    setOracleError(null);
    
    // Validate inputs
    if (!selectedRole) {
      setOracleError('Please select your current role');
      return;
    }
    
    if (!experienceYears || experienceYears < 0 || experienceYears > 20) {
      setOracleError('Please enter a valid number of years (0-20)');
      return;
    }

    setOracleLoading(true);
    setOracleData(null);

    try {
      const response = await fetch(apiConfig.buildUrl('/api/career/oracle'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify({
          current_role: selectedRole,
          experience_years: parseInt(experienceYears),
          goal: careerGoal || null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get career predictions');
      }

          const data = await response.json();
          console.log('Oracle API Response:', data);
          console.log('Career Trees:', data.career_trees);
          console.log('Full response structure:', JSON.stringify(data, null, 2));
          setOracleData(data);
    } catch (err) {
      console.error('Career Oracle error:', err);
      setOracleError(err.message || 'Failed to get career predictions');
    } finally {
      setOracleLoading(false);
    }
  };


  const getCareerRecommendations = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(apiConfig.buildUrl('/api/career/coach'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify({
          answers: quizAnswers
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setCareerResponse(data);

      // Award points for completing the career coach quiz
      try {
        const userId = user?.id;
        if (userId) {
          const awardRes = await fetch(apiConfig.buildUrl(`/api/user/${userId}/points`), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ task_name: 'career_coach_quiz' })
          });
          if (awardRes.ok) {
            const awardData = await awardRes.json();
            const gained = awardData.awarded_points || 300;
            setPointsEarned(gained);
            // Prefer reloading from server to avoid drift
            try {
              const stateRes = await fetch(apiConfig.buildUrl(`/api/user/${userId}/state`), { credentials: 'include' });
              if (stateRes.ok) {
                const stateData = await stateRes.json();
                if (typeof stateData.total_points === 'number') {
                  setTotalPoints(stateData.total_points);
                } else {
                  setTotalPoints((prev) => prev + gained);
                }
              } else {
                setTotalPoints((prev) => prev + gained);
              }
            } catch (_) {
              setTotalPoints((prev) => prev + gained);
            }
            setShowPointsAnimation(true);
            setTimeout(() => setShowPointsAnimation(false), 3000);
          } else {
            console.warn('Award points request failed:', awardRes.status);
          }
        }
      } catch (e) {
        console.warn('Failed to award points for career coach quiz:', e);
      }
    } catch (err) {
      console.error('Error fetching career recommendations:', err);
      setError('Failed to get career recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Load current total points when component mounts or user changes
  React.useEffect(() => {
    const loadPoints = async () => {
      try {
        const userId = user?.id;
        if (!userId) return;
        const res = await fetch(apiConfig.buildUrl(`/api/user/${userId}/state`), { credentials: 'include' });
        if (res.ok) {
          const data = await res.json();
          if (typeof data.total_points === 'number') setTotalPoints(data.total_points);
        }
      } catch (_) {}
    };
    loadPoints();
  }, [user?.id]);


  return (
    <div className="main-page">
      <div className="container">
        <div className="main-content">
          {/* Combined Header with Navigation */}
          <div className="career-header-container">
            <div className="career-header-content">
              <h1>Long Term Career Growth</h1>
              <button className="btn btn-primary" onClick={() => navigate('/main')}>
                Back to Main
              </button>
            </div>
            <div className="segment-navigation">
              <button
                  className={`segment-btn ${activeSegment === 'quiz' ? 'active' : ''}`}
                  onClick={() => setActiveSegment('quiz')}
              >
                  Career Coach Quiz
              </button>
              <button
                  className={`segment-btn ${activeSegment === 'jobs' ? 'active' : ''}`}
                  onClick={() => setActiveSegment('jobs')}
              >
                  SAP Jobs
              </button>
              <button
                  className={`segment-btn ${activeSegment === 'oracle' ? 'active' : ''}`}
                  onClick={() => setActiveSegment('oracle')}
              >
                  Career Oracle
              </button>
            </div>
          </div>


          {/* Career Coach AI Quiz Segment */}
          {activeSegment === 'quiz' && (
            <div className="quiz-segment">
              <div className="quiz-container">
                <div className="quiz-header">
                  <h3>Career Coach AI Quiz</h3>
                  <p>Answer a few questions to get personalized career recommendations</p>
          </div>


                {!showResults ? (
                  <div className="quiz-content">
                    <div className="quiz-progress">
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{ width: `${((quizStep + 1) / quizQuestions.length) * 100}%` }}
                        ></div>
                      </div>
                      <span className="progress-text">
                        Question {quizStep + 1} of {quizQuestions.length}
                      </span>
                    </div>


                    <div className="quiz-question">
                      <h4>{quizQuestions[quizStep].question}</h4>
                      <div className="quiz-options">
                        {quizQuestions[quizStep].options.map((option) => (
                          <button
                            key={option.value}
                            className={`quiz-option ${quizAnswers[quizQuestions[quizStep].id] === option.value ? 'selected' : ''}`}
                            onClick={() => handleQuizAnswer(quizQuestions[quizStep].id, option.value)}
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                    </div>


                    <div className="quiz-navigation">
                      <button
                        className="btn btn-secondary"
                        onClick={prevQuizStep}
                        disabled={quizStep === 0}
                      >
                        Previous
                      </button>
                      <button
                        className="btn btn-primary"
                        onClick={nextQuizStep}
                        disabled={!quizAnswers[quizQuestions[quizStep].id]}
                      >
                        {quizStep === quizQuestions.length - 1 ? 'Get Results' : 'Next'}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="quiz-results">
                    {isLoading ? (
                      <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Getting your personalized career recommendations...</p>
                      </div>
                    ) : error ? (
                      <div className="error-state">
                        <p className="error-message">{error}</p>
                        <button className="btn btn-primary" onClick={getCareerRecommendations}>
                          Try Again
                        </button>
                      </div>
                    ) : careerResponse ? (
                      <div className="ai-recommendations">
                        <div className="profile-summary">
                          <h4>Your Profile Summary</h4>
                          <p>{careerResponse.profile_summary.replace(/\*\*/g, '').replace(/^\d+\.\s*/gm, '').trim()}</p>
                        </div>
                        
                        <div className="role-suggestions">
                          <h4>Recommended SAP Roles</h4>
                          <div className="suggestions-content">
                            {careerResponse.suggestions
                              .split('\n')
                              .filter(line => line.trim() !== '')
                              .map((line, index) => {
                                const cleanLine = line.trim().replace(/\*\*/g, '');
                                // Extract role name (everything before the first colon)
                                const colonIndex = cleanLine.indexOf(':');
                                if (colonIndex > 0) {
                                  const roleName = cleanLine.substring(0, colonIndex);
                                  const description = cleanLine.substring(colonIndex + 1);
                                  return (
                                    <p key={index} className="suggestion-line">
                                      <strong>{roleName}:</strong>{description}
                                    </p>
                                  );
                                }
                                return (
                                  <p key={index} className="suggestion-line">
                                    {cleanLine}
                                  </p>
                                );
                              })}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="no-results">
                        <p>No recommendations available. Please try again.</p>
                        <button className="btn btn-primary" onClick={getCareerRecommendations}>
                          Get Recommendations
                        </button>
                      </div>
                    )}

                    <div className="results-actions">
                      <button className="btn btn-primary" onClick={resetQuiz}>
                        Retake Quiz
                      </button>
                      <button className="btn btn-secondary" onClick={() => setActiveSegment('jobs')}>
                        View SAP Jobs
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}


          {/* SAP Jobs Segment */}
          {activeSegment === 'jobs' && (
            <div className="jobs-segment">
              <div className="jobs-container">
                <div className="jobs-header">
                  <h3><strong>SAP Job Opportunities</strong></h3>
                  <p>Explore current SAP positions that match your career goals</p>
                </div>




                <div className="jobs-list">
                  {sapJobs.slice(0, jobsToShow).map((job) => (
                    <div key={job.id} className={`job-card ${job.featured ? 'featured' : ''}`}>
                      {job.featured && <div className="featured-badge">Featured</div>}
                      <div className="job-header">
                        <h4>{job.title}</h4>
                      </div>
                     
                      <div className="job-details">
                        <div className="job-info">
                          <div className="info-item">
                            <span className="label">Experience:</span>
                            <span className="value">{job.experience}</span>
                          </div>
                          <div className="info-item">
                            <span className="label">Salary:</span>
                            <span className="value">{job.salary}</span>
                          </div>
                          <div className="info-item">
                            <span className="label">Posted:</span>
                            <span className="value">{job.posted}</span>
                          </div>
                        </div>
                       
                        <p className="job-description">{job.description}</p>
                      </div>
                     
                      <div className="job-actions">
                        <button className="btn btn-primary">Apply Now</button>
                        <button className="btn btn-secondary">Save Job</button>
                      </div>
                    </div>
                  ))}
                </div>


                {jobsToShow < sapJobs.length && (
                  <div className="jobs-pagination">
                    <button className="btn btn-secondary" onClick={loadMoreJobs}>
                      Load More Jobs
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Career Oracle Segment */}
          {activeSegment === 'oracle' && (
            <div className="oracle-segment">
              <div className="oracle-container">
                <div className="oracle-header">
                  <div className="oracle-icon">🔮</div>
                  <h3><strong>AI Career Path Oracle</strong></h3>
                  <p>Watch our AI craft a personalized career route based on your profile and constraints</p>
                </div>
                
                <div className="oracle-content">
                  <div className="role-selection">
                    <div className="input-row">
                      <div className="role-input-group">
                        <label htmlFor="current-role">Current Role *</label>
                        <select
                          id="current-role"
                          className="role-select"
                          value={selectedRole}
                          onChange={(e) => setSelectedRole(e.target.value)}
                          required
                        >
                          <option value="">Choose your current SAP role...</option>
                          <option value="SAP Junior Developer">SAP Junior Developer</option>
                          <option value="SAP Functional Consultant">SAP Functional Consultant</option>
                          <option value="SAP Business Analyst">SAP Business Analyst</option>
                          <option value="SAP Project Manager">SAP Project Manager</option>
                          <option value="SAP Solution Architect">SAP Solution Architect</option>
                        </select>
                      </div>
                      
                      <div className="experience-input-group">
                        <label htmlFor="experience-years">Years of Experience *</label>
                        <input 
                          type="number" 
                          id="experience-years" 
                          className="experience-input"
                          min="0" 
                          max="20" 
                          placeholder="Enter years (0-20)"
                          value={experienceYears}
                          onChange={(e) => setExperienceYears(e.target.value)}
                          required
                        />
                      </div>
                    </div>
                    
                    <div className="goal-input-group">
                      <label htmlFor="career-goal">Career Goal (Optional)</label>
                      <select 
                        id="career-goal" 
                        className="goal-select"
                        value={careerGoal}
                        onChange={(e) => setCareerGoal(e.target.value)}
                      >
                        <option value="">Choose your career goal...</option>
                        <option value="leadership">Leadership & Management</option>
                        <option value="technical mastery">Technical Mastery</option>
                        <option value="architecture">Solution Architecture</option>
                        <option value="consulting">Consulting Excellence</option>
                        <option value="innovation">Innovation & R&D</option>
                      </select>
                    </div>
                    
                    <button 
                      className="btn btn-primary oracle-btn"
                      onClick={predictCareerPath}
                      disabled={oracleLoading || !selectedRole || !experienceYears}
                    >
                      {oracleLoading ? '🔮 AI is crafting your route...' : '🔮 Craft My Career Route'}
                    </button>
                  </div>
                  
                  {/* Error Display */}
                  {oracleError && (
                    <div className="oracle-error">
                      <div className="error-icon">⚠️</div>
                      <p>{oracleError}</p>
                    </div>
                  )}
                  
                  {/* AI Crafting Process Display */}
                  {oracleLoading && (
                    <div className="ai-crafting-process">
                      <div className="crafting-header">
                        <div className="ai-icon">🔮</div>
                        <h4>AI is crafting your personalized career route...</h4>
                        <p>Analyzing your profile: <strong>{selectedRole}</strong> with <strong>{experienceYears} years</strong> experience</p>
                        {careerGoal && <p>Goal: <strong>{careerGoal}</strong></p>}
                      </div>
                      
                      <div className="crafting-steps">
                        <div className="step">
                          <div className="step-icon">🔍</div>
                          <div className="step-content">
                            <h5>Analyzing Constraints</h5>
                            <p>Reviewing SAP role requirements and experience levels</p>
                          </div>
                        </div>
                        
                        <div className="step">
                          <div className="step-icon">🎯</div>
                          <div className="step-content">
                            <h5>Mapping Career Goals</h5>
                            <p>Aligning your goals with realistic progression paths</p>
                          </div>
                        </div>
                        
                        <div className="step">
                          <div className="step-icon">⚡</div>
                          <div className="step-content">
                            <h5>Generating Routes</h5>
                            <p>Creating personalized career progression sequences</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Results Display */}
                  {oracleData && (
                    <div className="oracle-results">
                      <div className="results-header">
                        <h4>🔮 Your AI-Crafted Career Route</h4>
                        <p>Based on your profile: <strong>{oracleData.current_role}</strong> • <strong>{oracleData.experience_years} years</strong> experience</p>
                      </div>
                      
                      <div className="career-route-display">
                        {/* Current Role */}
                        <div className="current-role-card">
                          <div className="role-icon">📍</div>
                          <div className="role-content">
                            <h5>Your Starting Point</h5>
                            <h4>{oracleData.current_role}</h4>
                            <p>{oracleData.experience_years} years of experience</p>
                          </div>
                        </div>
                        
                        {/* Career Routes */}
                        {oracleData.career_trees && oracleData.career_trees.length > 0 ? (
                          oracleData.career_trees.map((tree, treeIndex) => (
                            <div key={treeIndex} className="career-route-card">
                              <div className="route-header">
                                <span className="route-icon">{tree.tree_icon || '🎯'}</span>
                                <div className="route-info">
                                  <h5>{tree.tree_name}</h5>
                                  <p>{tree.tree_description}</p>
                                </div>
                                <span className="ai-badge">🔮 AI Crafted</span>
                              </div>
                              
                              <div className="route-path">
                                {tree.progressive_paths && tree.progressive_paths.map((path, pathIndex) => (
                                  <div key={pathIndex} className="path-step">
                                    <div className="step-connector"></div>
                                    <div className="step-content">
                                      <div className="step-header">
                                        <h6>{path.role}</h6>
                                        <span className="step-timeline">{path.timeline}</span>
                                      </div>
                                      
                                      <div className="step-story">
                                        <p>{path.story}</p>
                                      </div>
                                      
                                      <div className="step-skills">
                                        <div className="skills-required">
                                          <strong>Skills to Develop:</strong>
                                          <div className="skill-tags">
                                            {(path.skills_required || []).map((skill, skillIndex) => (
                                              <span key={skillIndex} className="skill-tag required">{skill}</span>
                                            ))}
                                          </div>
                                        </div>
                                        
                                        <div className="skills-gained">
                                          <strong>Skills You'll Gain:</strong>
                                          <div className="skill-tags">
                                            {(path.skills_gained || []).map((skill, skillIndex) => (
                                              <span key={skillIndex} className="skill-tag gained">{skill}</span>
                                            ))}
                                          </div>
                                        </div>
                                      </div>
                                      
                                      <div className="step-actions">
                                        <button className="develop-skills-btn">
                                          Develop Skills
                                        </button>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="no-routes">
                            <div className="no-routes-icon">🔮</div>
                            <h4>No career routes generated</h4>
                            <p>Unable to generate career routes. Please try again or check your inputs.</p>
                            <button 
                              className="btn btn-primary"
                              onClick={predictCareerPath}
                              disabled={oracleLoading}
                            >
                              Try Again
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Points Display (standardized with Onboarding) */}
      <div className="points-display">
        <div className="points-container">
          <div className="points-icon">⭐</div>
          <div className="points-text">
            <span className="points-label">Points</span>
            <span className="points-value">{totalPoints}</span>
          </div>
        </div>
        {showPointsAnimation && (
          <div className="points-animation">
            <div className="points-earned">+{pointsEarned}</div>
          </div>
        )}
      </div>
    </div>
  );
}


export default Career;