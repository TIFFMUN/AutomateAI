import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ text = "Loading...", size = "medium", className = "" }) => {
  const sizeClass = size === "small" ? "loading-spinner-small" : 
                   size === "large" ? "loading-spinner-large" : 
                   "loading-spinner";
  
  return (
    <div className={`loading-container ${className}`}>
      <div className={sizeClass}></div>
      {text && <p className="loading-text">{text}</p>}
    </div>
  );
};

export default LoadingSpinner;
