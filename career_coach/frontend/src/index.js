import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';  // <-- make sure this matches the file name
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

