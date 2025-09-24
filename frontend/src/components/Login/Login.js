import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../LoadingSpinner';
import './Login.css';
import { Player } from '@lottiefiles/react-lottie-player';
import WaitingPigeon from '../../animations/WaitingPigeon.json';

// Icons (using Unicode symbols for simplicity)
const UserIcon = () => <span style={{ fontSize: '20px', marginRight: '8px' }}>👤</span>;
const EmailIcon = () => <span style={{ fontSize: '20px', marginRight: '8px' }}>📧</span>;
const LockIcon = () => <span style={{ fontSize: '20px', marginRight: '8px' }}>🔒</span>;
const NameIcon = () => <span style={{ fontSize: '20px', marginRight: '8px' }}>👨‍💼</span>;

// Password strength indicator component
const PasswordStrength = ({ password }) => {
  const getStrength = (pwd) => {
    if (!pwd) return { score: 0, label: '', color: '' };
    
    let score = 0;
    if (pwd.length >= 8) score++;
    if (pwd.length >= 12) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[a-z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;
    
    if (score <= 2) return { score, label: 'Weak', color: '#e53e3e' };
    if (score <= 4) return { score, label: 'Medium', color: '#d69e2e' };
    return { score, label: 'Strong', color: '#38a169' };
  };
  
  const strength = getStrength(password);
  
  if (!password) return null;
  
  return (
    <div style={{ marginTop: '8px', fontSize: '12px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ 
          flex: 1, 
          height: '4px', 
          backgroundColor: '#e2e8f0', 
          borderRadius: '2px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${(strength.score / 6) * 100}%`,
            height: '100%',
            backgroundColor: strength.color,
            transition: 'all 0.3s ease'
          }} />
        </div>
        <span style={{ color: strength.color, fontWeight: '600' }}>
          {strength.label}
        </span>
      </div>
    </div>
  );
};

function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [registerData, setRegisterData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register, isAuthenticated, loading } = useAuth();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !loading) {
      const from = location.state?.from?.pathname || '/main';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, loading, navigate, location]);

  const handleChange = (e) => {
    if (isLogin) {
      setFormData({
        ...formData,
        [e.target.name]: e.target.value
      });
    } else {
      setRegisterData({
        ...registerData,
        [e.target.name]: e.target.value
      });
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    if (formData.username.trim() === '' || formData.password.trim() === '') {
      setError('Please fill in all fields');
      setIsSubmitting(false);
      return;
    }

    const result = await login(formData);
    if (result.success) {
      const from = location.state?.from?.pathname || '/main';
      navigate(from, { replace: true });
    } else {
      setError(result.error);
    }
    setIsSubmitting(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    if (registerData.password !== registerData.confirmPassword) {
      setError('Passwords do not match');
      setIsSubmitting(false);
      return;
    }

    if (registerData.username.trim() === '' || registerData.email.trim() === '' || 
        registerData.password.trim() === '') {
      setError('Please fill in all required fields');
      setIsSubmitting(false);
      return;
    }

    if (registerData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      setIsSubmitting(false);
      return;
    }

    const result = await register({
      username: registerData.username,
      email: registerData.email,
      password: registerData.password,
      full_name: registerData.fullName || null
    });

    if (result.success) {
      const from = location.state?.from?.pathname || '/main';
      navigate(from, { replace: true });
    } else {
      setError(result.error);
    }
    setIsSubmitting(false);
  };

  if (loading) {
    return (
      <div className="login-container">
        <LoadingSpinner text="please be patient with me as i load" size="large" className="full-page" />
      </div>
    );
  }

  return (
    <div className="login-container">
      <div className={`login-card ${isLogin ? 'sign-in' : 'sign-up'}`}>
        <div className="card-pigeon" aria-hidden="true">
          <Player autoplay loop src={WaitingPigeon} style={{ width: 120, height: 120 }} />
        </div>
        <h1 className="login-title">
          {isLogin ? 'Welcome Back' : 'Join AutomateAI'}
        </h1>
        <p style={{ 
          textAlign: 'center', 
          color: '#718096', 
          marginBottom: '30px',
          fontSize: '16px'
        }}>
          {isLogin ? 'Sign in to your account' : 'Create your account to get started'}
        </p>
        
        {/* Toggle between Login and Register */}
        <div className="auth-toggle">
          <button 
            className={`toggle-btn ${isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(true);
              setError('');
            }}
          >
            Sign In
          </button>
          <button 
            className={`toggle-btn ${!isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(false);
              setError('');
            }}
          >
            Sign Up
          </button>
        </div>

        {isLogin ? (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="username">
                <UserIcon />
                Username
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Enter your username"
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="password">
                <LockIcon />
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                required
              />
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <button 
              type="submit" 
              className="btn btn-primary" 
              style={{ width: '100%' }}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <LoadingSpinner text="please be patient with me as i load" size="small" />
              ) : 'Sign In'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label htmlFor="reg-username">
                <UserIcon />
                Username *
              </label>
              <input
                type="text"
                id="reg-username"
                name="username"
                value={registerData.username}
                onChange={handleChange}
                placeholder="Choose a username"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="reg-email">
                <EmailIcon />
                Email *
              </label>
              <input
                type="email"
                id="reg-email"
                name="email"
                value={registerData.email}
                onChange={handleChange}
                placeholder="Enter your email"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="reg-fullName">
                <NameIcon />
                Full Name
              </label>
              <input
                type="text"
                id="reg-fullName"
                name="fullName"
                value={registerData.fullName}
                onChange={handleChange}
                placeholder="Enter your full name (optional)"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="reg-password">
                <LockIcon />
                Password *
              </label>
              <input
                type="password"
                id="reg-password"
                name="password"
                value={registerData.password}
                onChange={handleChange}
                placeholder="Create a password"
                required
              />
              <PasswordStrength password={registerData.password} />
            </div>

            <div className="form-group">
              <label htmlFor="reg-confirmPassword">
                <LockIcon />
                Confirm Password *
              </label>
              <input
                type="password"
                id="reg-confirmPassword"
                name="confirmPassword"
                value={registerData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm your password"
                required
              />
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <button 
              type="submit" 
              className="btn btn-primary" 
              style={{ width: '100%' }}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <LoadingSpinner text="Creating Account..." size="small" />
              ) : 'Create Account'}
            </button>
          </form>
        )}
        
        <div style={{ 
          marginTop: '30px', 
          fontSize: '14px', 
          color: '#718096', 
          textAlign: 'center',
          padding: '20px 0',
          borderTop: '1px solid #e2e8f0'
        }}>
          <p style={{ margin: 0 }}>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button 
              type="button"
              className="link-btn"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
              }}
            >
              {isLogin ? 'Sign up here' : 'Sign in here'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
