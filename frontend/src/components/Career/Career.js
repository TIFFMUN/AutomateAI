import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Career.css';
import apiConfig from '../../utils/apiConfig';


function Career() {
  const navigate = useNavigate();
  const [activeSegment, setActiveSegment] = useState('quiz');
  const [quizStep, setQuizStep] = useState(0);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [jobsToShow, setJobsToShow] = useState(4);
  const [isLoading, setIsLoading] = useState(false);
  const [careerResponse, setCareerResponse] = useState(null);
  const [error, setError] = useState(null);


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


  const getCareerRecommendations = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiConfig.BASE_URL}/api/career/coach`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          answers: quizAnswers
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setCareerResponse(data);
    } catch (err) {
      console.error('Error fetching career recommendations:', err);
      setError('Failed to get career recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };


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
                              .map((line, index) => (
                                <p key={index} className="suggestion-line">
                                  {line.trim().replace(/\*\*/g, '')}
                                </p>
                              ))}
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
                  <h3>SAP Job Opportunities</h3>
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
        </div>
      </div>
    </div>
  );
}


export default Career;