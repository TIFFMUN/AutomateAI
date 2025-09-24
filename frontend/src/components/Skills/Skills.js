import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Skills.css';
import API_CONFIG from '../../utils/apiConfig';
import { useAuth } from '../../contexts/AuthContext';

function Skills() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('skills');
  const [recommendations, setRecommendations] = useState([]);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [userSkillsInput, setUserSkillsInput] = useState('');
  
  // Role selection state
  const [isManagerView, setIsManagerView] = useState(false);
  const [hasSelectedRole, setHasSelectedRole] = useState(false);
  
  // Course form state
  const [courseImage, setCourseImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [courseForm, setCourseForm] = useState({
    title: '',
    instructor: '',
    description: '',
    duration: '',
    level: '',
    skills: '',
    url: ''
  });
  
  // Points state
  const [totalPoints, setTotalPoints] = useState(0);
  const [pointsEarned, setPointsEarned] = useState(0);
  const [showPointsAnimation, setShowPointsAnimation] = useState(false);
  const [completedSkills, setCompletedSkills] = useState(new Set());
  
  // Visual points notification state
  const [showVisualPointsNotification, setShowVisualPointsNotification] = useState(false);
  const [visualPointsValue, setVisualPointsValue] = useState(0);
  const [visualPointsMessage, setVisualPointsMessage] = useState('');

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
      progress: 100,
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

  // Load courses from localStorage or use default courses
  const getInitialCourses = () => {
    try {
      const savedCourses = localStorage.getItem('automateAI_courses');
      if (savedCourses) {
        return JSON.parse(savedCourses);
      }
    } catch (error) {
      console.warn('Failed to load courses from localStorage:', error);
    }
    // Return default courses if no saved data
    return [
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
  };

  const [courses, setCourses] = useState(getInitialCourses);

  // Function to save courses to localStorage
  const saveCoursesToStorage = (coursesToSave) => {
    try {
      localStorage.setItem('automateAI_courses', JSON.stringify(coursesToSave));
    } catch (error) {
      console.warn('Failed to save courses to localStorage:', error);
    }
  };

  // Function to reset courses to default (useful for testing)
  const resetCoursesToDefault = () => {
    const defaultCourses = getInitialCourses();
    setCourses(defaultCourses);
    saveCoursesToStorage(defaultCourses);
  };

  // Function to get LLM skill recommendations
  const getSkillRecommendations = useCallback(async () => {
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
  }, [userSkillsInput]);

  // Load current total points when component mounts or user changes
  useEffect(() => {
    const loadPoints = async () => {
      try {
        const userId = user?.id;
        if (!userId) return;
        const res = await fetch(API_CONFIG.buildUrl(`/api/user/${userId}/state`), { credentials: 'include' });
        if (res.ok) {
          const data = await res.json();
          if (typeof data.total_points === 'number') setTotalPoints(data.total_points);
        }
      } catch (_) {}
    };
    loadPoints();
  }, [user?.id]);

  // Show visual points notification
  const showVisualPoints = (points, message) => {
    setVisualPointsValue(points);
    setVisualPointsMessage(message);
    setShowVisualPointsNotification(true);
    
    // Hide notification after 2 seconds
    setTimeout(() => {
      setShowVisualPointsNotification(false);
    }, 2000);
  };

  // Award points for skill completion
  const awardSkillCompletionPoints = async (skillId, skillName) => {
    try {
      const userId = user?.id;
      console.log('Attempting to award points for user:', userId, 'skill:', skillName);
      if (userId && !completedSkills.has(skillId)) {
        const requestBody = { 
          task_name: 'skill_completion',
          message: `Completed skill: ${skillName}` 
        };
        console.log('Sending request body:', requestBody);
        
        const awardRes = await fetch(API_CONFIG.buildUrl(`/api/user/${userId}/points`), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(requestBody)
        });

        console.log('Points API response status:', awardRes.status);
        if (awardRes.ok) {
          const awardData = await awardRes.json();
          console.log('Points awarded successfully:', awardData);
          const gained = awardData.awarded_points || 500;
          setPointsEarned(gained);
          
          // Update total points
          try {
            const stateRes = await fetch(API_CONFIG.buildUrl(`/api/user/${userId}/state`), { credentials: 'include' });
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
          
          // Mark skill as completed
          setCompletedSkills(prev => new Set([...prev, skillId]));
          
          // Show visual notification only after successful database update
          showVisualPoints(500, "Course Completed!");
          
          // Show animation
          setShowPointsAnimation(true);
          setTimeout(() => setShowPointsAnimation(false), 3000);
          
          return true;
        } else {
          console.warn('Failed to award points - API returned error:', awardRes.status);
          const errorText = await awardRes.text();
          console.warn('Error response:', errorText);
        }
      } else {
        console.warn('No user ID or skill already completed');
      }
    } catch (e) {
      console.warn('Failed to award points for skill completion:', e);
    }
    return false;
  };

  // Handle role selection
  const handleRoleSelection = (isManager) => {
    setIsManagerView(isManager);
    setHasSelectedRole(true);
    // Reset tab to appropriate default
    setActiveTab(isManager ? 'courses' : 'skills');
  };

  // Image upload handlers
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setCourseImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleImageRemove = () => {
    setCourseImage(null);
    setImagePreview(null);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('image/')) {
        setCourseImage(file);
        const reader = new FileReader();
        reader.onload = (e) => {
          setImagePreview(e.target.result);
        };
        reader.readAsDataURL(file);
      }
    }
  };

  // Form input handlers
  const handleFormInputChange = (field, value) => {
    setCourseForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Course submission handler
  const handleAddCourse = (event) => {
    event.preventDefault();
    
    // Validate required fields
    if (!courseForm.title || !courseForm.instructor || !courseForm.description) {
      alert('Please fill in all required fields (Title, Instructor, Description)');
      return;
    }

    // Create new course object
    const newCourse = {
      id: Date.now(), // Simple ID generation
      title: courseForm.title,
      instructor: courseForm.instructor,
      description: courseForm.description,
      duration: courseForm.duration || 'TBD',
      level: courseForm.level || 'All Levels',
      skills: courseForm.skills ? courseForm.skills.split(',').map(s => s.trim()) : [],
      url: courseForm.url || '#',
      image: imagePreview || '/api/placeholder/300/200', // Default placeholder if no image
      rating: 0,
      students: 0,
      price: 'Free',
      category: 'Management Added'
    };

    // Add to courses array and save to localStorage
    const updatedCourses = [newCourse, ...courses];
    setCourses(updatedCourses);
    saveCoursesToStorage(updatedCourses);

    // Reset form
    setCourseForm({
      title: '',
      instructor: '',
      description: '',
      duration: '',
      level: '',
      skills: '',
      url: ''
    });
    setCourseImage(null);
    setImagePreview(null);

    // Show success message and switch to courses tab
    alert('Course added successfully! You can now see it in the "View All Courses" tab.');
    setActiveTab('courses');
  };

  // Reset form handler
  const handleResetForm = () => {
    setCourseForm({
      title: '',
      instructor: '',
      description: '',
      duration: '',
      level: '',
      skills: '',
      url: ''
    });
    setCourseImage(null);
    setImagePreview(null);
  };

  // Handle incoming data from Career Oracle
  useEffect(() => {
    if (location.state?.fromCareerOracle && location.state?.skillsToDevelop) {
      // Auto-populate the skills input with data from Career Oracle
      setUserSkillsInput(location.state.skillsToDevelop);
      
      // Switch to recommendations tab
      setActiveTab('recommendations');
      
      // Don't auto-trigger recommendations - let user decide when to get them
    }
  }, [location.state]);

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
          {!hasSelectedRole ? (
            <div className="empty-state">
              <div className="empty-state-content">
                <div className="empty-state-icon">👤</div>
                <h2>Select Your Role</h2>
                <p>Choose how you'd like to view the Skills Development section:</p>
                <div className="role-selection">
                  <button 
                    className="role-btn employee-btn"
                    onClick={() => handleRoleSelection(false)}
                  >
                    <span className="role-icon">👨‍💼</span>
                    <span className="role-title">View as Employee</span>
                    <span className="role-description">Track your skills and discover new learning opportunities</span>
                  </button>
                  <button 
                    className="role-btn manager-btn"
                    onClick={() => handleRoleSelection(true)}
                  >
                    <span className="role-icon">👩‍💼</span>
                    <span className="role-title">View as Manager</span>
                    <span className="role-description">Add new courses and get AI recommendations for your team</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Header Section */}
              <div className="skills-header">
                <h2>{isManagerView ? 'Manage Team Skills Development' : 'Develop Your Professional Skills'}</h2>
                <p>{isManagerView ? 'Add new courses and get AI recommendations for your team' : 'Track your progress, discover learning opportunities, and advance your career'}</p>
              </div>

              {/* Tab Navigation */}
              <div className="tab-navigation">
                {isManagerView ? (
                  <>
                    <button 
                      className={`tab-btn ${activeTab === 'skills' ? 'active' : ''}`}
                      onClick={() => setActiveTab('skills')}
                    >
                      Add New Course
                    </button>
                    <button 
                      className={`tab-btn ${activeTab === 'courses' ? 'active' : ''}`}
                      onClick={() => setActiveTab('courses')}
                    >
                      View All Courses
                    </button>
                    <button 
                      className={`tab-btn ${activeTab === 'recommendations' ? 'active' : ''}`}
                      onClick={() => setActiveTab('recommendations')}
                    >
                      AI Recommendations
                    </button>
                  </>
                ) : (
                  <>
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
                  </>
                )}
              </div>

              {/* Skills Tab Content */}
              {activeTab === 'skills' && (
                <>
                  {isManagerView ? (
                    /* Manager View - Add New Course Form */
                    <div className="add-course-form">
                      <div className="form-container">
                        <h4>Add a New Course</h4>
                        <form className="course-form" onSubmit={handleAddCourse}>
                          <div className="form-group">
                            <label>Course Image</label>
                            <div 
                              className="image-upload-container"
                              onDragOver={handleDragOver}
                              onDragLeave={handleDragLeave}
                              onDrop={handleDrop}
                              onClick={() => document.getElementById('course-image-upload').click()}
                            >
                              {imagePreview ? (
                                <div className="uploaded-image-container">
                                  <img src={imagePreview} alt="Course preview" className="image-preview" />
                                  <button 
                                    type="button" 
                                    className="remove-image-btn"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleImageRemove();
                                    }}
                                  >
                                    Remove Image
                                  </button>
                                </div>
                              ) : (
                                <>
                                  <div className="image-upload-icon">📷</div>
                                  <div className="image-upload-text">Click to upload or drag and drop</div>
                                  <div className="image-upload-subtext">PNG, JPG, GIF up to 10MB</div>
                                </>
                              )}
                              <input
                                id="course-image-upload"
                                type="file"
                                accept="image/*"
                                onChange={handleImageUpload}
                                className="image-upload-input"
                              />
                            </div>
                          </div>
                          <div className="form-group">
                            <label>Course Title *</label>
                            <input 
                              type="text" 
                              placeholder="Enter course title..." 
                              value={courseForm.title}
                              onChange={(e) => handleFormInputChange('title', e.target.value)}
                              required
                            />
                          </div>
                          <div className="form-group">
                            <label>Instructor *</label>
                            <input 
                              type="text" 
                              placeholder="Enter instructor name..." 
                              value={courseForm.instructor}
                              onChange={(e) => handleFormInputChange('instructor', e.target.value)}
                              required
                            />
                          </div>
                          <div className="form-group">
                            <label>Description *</label>
                            <textarea 
                              placeholder="Describe the course content..." 
                              rows="4"
                              value={courseForm.description}
                              onChange={(e) => handleFormInputChange('description', e.target.value)}
                              required
                            ></textarea>
                          </div>
                          <div className="form-row">
                            <div className="form-group">
                              <label>Duration</label>
                              <input 
                                type="text" 
                                placeholder="e.g., 10 hours" 
                                value={courseForm.duration}
                                onChange={(e) => handleFormInputChange('duration', e.target.value)}
                              />
                            </div>
                            <div className="form-group">
                              <label>Level</label>
                              <select 
                                value={courseForm.level}
                                onChange={(e) => handleFormInputChange('level', e.target.value)}
                              >
                                <option value="">Select level...</option>
                                <option value="Beginner">Beginner</option>
                                <option value="Intermediate">Intermediate</option>
                                <option value="Advanced">Advanced</option>
                                <option value="All Levels">All Levels</option>
                              </select>
                            </div>
                          </div>
                          <div className="form-group">
                            <label>Skills Covered</label>
                            <input 
                              type="text" 
                              placeholder="Enter skills separated by commas..." 
                              value={courseForm.skills}
                              onChange={(e) => handleFormInputChange('skills', e.target.value)}
                            />
                          </div>
                          <div className="form-group">
                            <label>Course URL</label>
                            <input 
                              type="url" 
                              placeholder="https://..." 
                              value={courseForm.url}
                              onChange={(e) => handleFormInputChange('url', e.target.value)}
                            />
                          </div>
                          <div className="form-actions">
                            <button type="button" className="btn btn-secondary" onClick={handleResetForm}>Reset Form</button>
                            <button type="submit" className="btn btn-primary">Add Course</button>
                          </div>
                        </form>
                      </div>
                    </div>
                  ) : (
                    /* Employee View - My Skills */
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
                          {skill.progress === 100 ? (
                            completedSkills.has(skill.id) ? (
                              <button className="btn btn-success" disabled>
                                Completed
                              </button>
                            ) : (
                              <button 
                                className="btn btn-success"
                                onClick={() => awardSkillCompletionPoints(skill.id, skill.name)}
                              >
                                Complete Course
                              </button>
                            )
                          ) : (
                            <button className="btn btn-primary">Continue Learning</button>
                          )}
                          <button className="btn btn-secondary">View Details</button>
                        </div>
                      </div>
                    ))}
                  </div>
                    </>
                  )}
                </>
              )}

              {/* Courses Tab Content */}
              {activeTab === 'courses' && (
                <div className="courses-section">
                  <div className="courses-header">
                    <h3>{isManagerView ? 'View All Courses' : 'Featured Courses'}</h3>
                    <p>{isManagerView ? 'Browse all available courses for your team' : 'Discover top-rated courses to enhance your skills'}</p>
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
                              {course.skills.slice(0, 3).map((skill, index) => (
                                <span key={index} className="skill-tag">{skill}</span>
                              ))}
                              {course.skills.length > 3 && (
                                <span className="skill-tag more">+{course.skills.length - 3}</span>
                              )}
                            </div>
                            
                            <div className="course-footer">
                              <div className="course-price">{course.price}</div>
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
                    <p>{isManagerView ? 'Get AI recommendations for your team\'s skill development' : 'Get personalized skill recommendations based on your current abilities'}</p>
                  </div>
                  
                  <div className="recommendations-input">
                    {location.state?.fromCareerOracle && (
                      <div className="career-oracle-notice">
                        <div className="notice-icon">🎯</div>
                        <div className="notice-content">
                          <h4>Skills from Career Oracle</h4>
                          <p>These skills were automatically populated from your Career Oracle results. You can modify them below or get AI recommendations.</p>
                        </div>
                      </div>
                    )}
                    {isLoadingRecommendations ? (
                      <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Getting your personalized skill recommendations...</p>
                      </div>
                    ) : (
                      <>
                         <textarea
                           placeholder={isManagerView ? "Describe your team's current skills, project needs, and development goals..." : "Tell us about your current skills, experience, and career goals..."}
                           value={userSkillsInput}
                           onChange={(e) => setUserSkillsInput(e.target.value)}
                           className="skills-input"
                           rows="4"
                         />
                         <div className="recommendations-btn-container">
                           <button 
                             onClick={getSkillRecommendations}
                             className="recommendations-btn"
                             disabled={isLoadingRecommendations}
                           >
                             {isManagerView ? 'Get Team Recommendations' : 'Get Recommendations'}
                           </button>
                         </div>
                      </>
                    )}
                  </div>
                  
                  {recommendations.length > 0 ? (
                    <div className="recommendations-results">
                      <h4>{isManagerView ? 'Recommended Skills for Your Team' : 'Recommended Skills for You'}</h4>
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
            </>
          )}
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
        {showPointsAnimation && (
          <div className="points-animation">
            <div className="points-earned">+{pointsEarned}</div>
          </div>
        )}
      </div>

      {/* Visual Points Notification */}
      {showVisualPointsNotification && (
        <div className="visual-points-notification">
          <div className="visual-points-content">
            <div className="visual-points-icon">🎉</div>
            <div className="visual-points-text">
              <div className="visual-points-message">{visualPointsMessage}</div>
              <div className="visual-points-value">+{visualPointsValue} points!</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Skills;
