import React from 'react';
import { useNavigate } from 'react-router-dom';

function Onboarding() {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate('/main');
  };

  return (
    <div className="main-page">
      <div className="container">
        <div className="main-header">
          <h1>Onboarding</h1>
          <button className="btn btn-primary" onClick={handleBack}>
            Back to Main
          </button>
        </div>
        
        <div className="main-content">
          <h2>Welcome to the Onboarding Section</h2>
        </div>
      </div>
    </div>
  );
}

export default Onboarding;
