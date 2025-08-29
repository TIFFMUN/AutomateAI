import React from 'react';
import { useNavigate } from 'react-router-dom';

function Skills() {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate('/main');
  };

  return (
    <div className="main-page">
      <div className="container">
        <div className="main-header">
          <h1>Skills Development</h1>
          <button className="btn btn-primary" onClick={handleBack}>
            Back to Main
          </button>
        </div>
        
        <div className="main-content">
          <h2>Develop Your Professional Skills</h2>
        </div>
      </div>
    </div>
  );
}

export default Skills;
