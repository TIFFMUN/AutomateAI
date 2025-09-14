import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext();

// Helper function to extract error message from validation errors
const extractErrorMessage = (errorDetail) => {
  if (typeof errorDetail === 'string') {
    return errorDetail;
  }
  
  if (Array.isArray(errorDetail)) {
    // Handle validation errors array
    return errorDetail.map(err => err.msg || err.message || 'Validation error').join(', ');
  }
  
  if (errorDetail && typeof errorDetail === 'object') {
    return errorDetail.message || errorDetail.msg || 'An error occurred';
  }
  
  return 'An error occurred';
};

// Configure axios defaults
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
axios.defaults.withCredentials = true; // Important for cookies

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is authenticated on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get('/api/auth/me');
      console.log('Auth check response:', response.data);
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      console.log('Not authenticated:', error.response?.status);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/auth/login', credentials);
      
      // Cookies are automatically set by the server
      // Use the user data from response, or fetch it from /me endpoint
      console.log('Login response data:', response.data);
      if (response.data.user) {
        console.log('Using user data from login response:', response.data.user);
        setUser(response.data.user);
      } else {
        // If user data not in response, fetch it from /me endpoint
        console.log('Fetching user data from /me endpoint');
        const meResponse = await axios.get('/api/auth/me');
        console.log('Me endpoint response:', meResponse.data);
        setUser(meResponse.data);
      }
      setIsAuthenticated(true);
      
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = extractErrorMessage(error.response?.data?.detail);
      return {
        success: false,
        error: errorMessage || 'Login failed'
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/auth/register', userData);
      
      // After successful registration, automatically log in
      const loginResponse = await login({
        username: userData.username,
        password: userData.password
      });
      
      return loginResponse;
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = extractErrorMessage(error.response?.data?.detail);
      return {
        success: false,
        error: errorMessage || 'Registration failed'
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await axios.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const refreshToken = useCallback(async () => {
    try {
      const response = await axios.post('/api/auth/refresh', {
        refresh_token: 'dummy' // Server will get refresh token from cookies
      });
      return response.data;
    } catch (error) {
      console.error('Token refresh error:', error);
      // If refresh fails, logout user
      logout();
      return null;
    }
  }, []);

  // Add axios interceptor to handle token refresh
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 && isAuthenticated) {
          // Try to refresh token
          const refreshed = await refreshToken();
          if (refreshed) {
            // Retry the original request
            return axios.request(error.config);
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, [isAuthenticated, refreshToken]);

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
