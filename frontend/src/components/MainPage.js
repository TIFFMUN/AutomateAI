import React from 'react';
import { useNavigate } from 'react-router-dom';

function MainPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    console.log('User logged out');
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

  return (
    <div className="main-page">
      <div className="container">
        <div className="main-header">
          <h1>Dashboard</h1>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
        
        <div className="main-content">
          <div className="sections-grid">
            <div 
              className="section-card onboarding"
              onClick={() => handleSectionClick('onboarding')}
            >
              <h2>ONBOARDING</h2>
            </div>
            
            <div 
              className="section-card skills"
              onClick={() => handleSectionClick('skills')}
            >
              <h2>SKILLS DEVELOPMENT</h2>
            </div>
            
            <div 
              className="section-card performance"
              onClick={() => handleSectionClick('performance')}
            >
              <h2>PERFORMANCE FEEDBACK</h2>
            </div>
            
            <div 
              className="section-card career"
              onClick={() => handleSectionClick('career')}
            >
              <h2>LONG TERM CAREER GROWTH</h2>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MainPage;
