/**
 * Authentication context for managing user session.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if we have a session ID in localStorage or URL params
    const checkAuth = async () => {
      try {
        // First check URL params (from OAuth callback)
        const urlParams = new URLSearchParams(window.location.search);
        const urlSessionId = urlParams.get('session_id');
        const urlError = urlParams.get('error');

        if (urlError) {
          setError(urlParams.get('message') || 'Authentication failed');
          setLoading(false);
          return;
        }

        if (urlSessionId) {
          // Store in localStorage
          localStorage.setItem('sessionId', urlSessionId);
          localStorage.setItem('email', urlParams.get('email'));
          localStorage.setItem('name', urlParams.get('name'));

          // Clean up URL
          window.history.replaceState({}, document.title, window.location.pathname);

          setSessionId(urlSessionId);

          const sessionInfo = await authAPI.getSessionInfo(urlSessionId);
          setUser(sessionInfo.user);
          setLoading(false);
          return;
        }

        // Check localStorage
        const storedSessionId = localStorage.getItem('sessionId');
        if (storedSessionId) {
          try {
            const sessionInfo = await authAPI.getSessionInfo(storedSessionId);
            setSessionId(storedSessionId);
            setUser(sessionInfo.user);
          } catch (err) {
            // Session expired or invalid
            localStorage.removeItem('sessionId');
            localStorage.removeItem('email');
            localStorage.removeItem('name');
            setError('Session expired. Please login again.');
          }
        }
      } catch (err) {
        console.error('Auth check failed:', err);
        setError('Failed to verify authentication');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const logout = async () => {
    try {
      if (sessionId) {
        await authAPI.logout(sessionId);
      }
    } catch (err) {
      console.error('Logout failed:', err);
    } finally {
      // Clear local state regardless
      setUser(null);
      setSessionId(null);
      localStorage.removeItem('sessionId');
      localStorage.removeItem('email');
      localStorage.removeItem('name');
      window.location.href = '/';
    }
  };

  const value = {
    user,
    sessionId,
    loading,
    error,
    logout,
    isAuthenticated: !!user && !!sessionId,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
