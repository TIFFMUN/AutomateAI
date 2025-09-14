import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './MainPage.css';

function MainPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [hoveredCard, setHoveredCard] = useState(null);
  const [totalPoints, setTotalPoints] = useState(null);
  const [rank, setRank] = useState(null);

  useEffect(() => {
    const loadUserStats = async () => {
      try {
        const userId = user?.id || user?.username;
        if (!userId) return;
        const apiBase = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const [stateRes, rankRes] = await Promise.all([
          fetch(`${apiBase}/api/user/${userId}/state`),
          fetch(`${apiBase}/api/user/${userId}/rank`)
        ]);
        if (stateRes.ok) {
          const data = await stateRes.json();
          if (typeof data.total_points === 'number') setTotalPoints(data.total_points);
        }
        if (rankRes.ok) {
          const r = await rankRes.json();
          if (typeof r.rank === 'number') setRank(r.rank);
        }
      } catch (_) {
        // ignore errors for now
      }
    };
    loadUserStats();
  }, [user?.id, user?.username]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleSectionClick = (section) => {
    switch (section) {
      case 'onboarding':
        navigate('/onboarding');
        break;
      case 'skills':
        navigate('/skills');
        break;
      case 'performance':
        navigate('/performance');
        break;
      case 'career':
        navigate('/career');
        break;
      default:
        break;
    }
  };

  const sections = [
    {
      id: 'onboarding',
      title: 'ONBOARDING',
      subtitle: 'Get Started Right',
      description: 'Complete your onboarding process and set up your profile you',
      icon: '🚀',
      color: '#8E44AD',
      gradient: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)'
    },
    {
      id: 'skills',
      title: 'SKILLS DEVELOPMENT',
      subtitle: 'Level Up',
      description: 'Track your skills and discover learning opportunities',
      icon: '📚',
      color: '#27AE60',
      gradient: 'linear-gradient(135deg, #27AE60 0%, #2ECC71 100%)'
    },
    {
      id: 'performance',
      title: 'PERFORMANCE FEEDBACK',
      subtitle: 'Track Progress',
      description: 'Monitor your performance and receive feedback',
      icon: '📊',
      color: '#E67E22',
      gradient: 'linear-gradient(135deg, #E67E22 0%, #F39C12 100%)'
    },
    {
      id: 'career',
      title: 'CAREER GROWTH',
      subtitle: 'Plan Ahead',
      description: 'Set long-term goals and plan your career path',
      icon: '🎯',
      color: '#E74C3C',
      gradient: 'linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)'
    }
  ];

  return (
    <div className="main-page">
      <div className="container">
        <div className="main-header">
          <div className="header-content">
            <h1>Welcome Back! 👋</h1>
            <p className="header-subtitle">
              Manage your professional development journey
              {totalPoints !== null && (
                <span style={{ marginLeft: 12 }}>
                  • Points: {totalPoints}{rank !== null && ` (Rank #${rank})`}
                </span>
              )}
            </p>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
        
        <div className="main-content">
          <div className="sections-grid">
            {sections.map((section) => (
              <div 
                key={section.id}
                className={`section-card ${section.id}`}
                onClick={() => handleSectionClick(section.id)}
                onMouseEnter={() => setHoveredCard(section.id)}
                onMouseLeave={() => setHoveredCard(null)}
                style={{
                  background: hoveredCard === section.id ? section.gradient : section.color,
                  transform: hoveredCard === section.id ? 'translateY(-8px) scale(1.02)' : 'translateY(0) scale(1)',
                  boxShadow: hoveredCard === section.id 
                    ? `0 20px 40px rgba(0, 0, 0, 0.3)` 
                    : `0 8px 25px rgba(0, 0, 0, 0.15)`
                }}
              >
                <div className="card-header">
                  <div className="card-icon">{section.icon}</div>
                </div>
                
                <div className="card-content">
                  <h2 className="card-title">{section.title}</h2>
                  <h3 className="card-subtitle">{section.subtitle}</h3>
                  <p className="card-description">{section.description}</p>
                </div>
                
                <div className="card-footer">
                  <span className="click-hint">Click to explore →</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MainPage;
