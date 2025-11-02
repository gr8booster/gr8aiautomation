import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const AuthContext = createContext(null);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const AUTH_REDIRECT_URL = 'https://smarthub-ai-1.preview.emergentagent.com/dashboard';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loggingIn, setLoggingIn] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Check if returning from auth
    const hash = window.location.hash;
    if (hash.includes('session_id=')) {
      const sessionId = hash.split('session_id=')[1].split('&')[0];
      processSessionId(sessionId);
    } else {
      // Check existing session
      checkSession();
    }
  }, []);

  const processSessionId = async (sessionId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/session`, {
        method: 'POST',
        headers: {
          'X-Session-ID': sessionId
        },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        
        // Clean URL
        window.location.hash = '';
        
        // Navigate to dashboard
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Session processing error:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkSession = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/me`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      }
    } catch (error) {
      console.log('Not authenticated');
    } finally {
      setLoading(false);
    }
  };

  const login = () => {
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(AUTH_REDIRECT_URL)}`;
  };

  const demoLogin = async () => {
    console.log('🔵 Demo login started...');
    setLoggingIn(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/demo`, {
        method: 'POST',
        credentials: 'include'
      });

      console.log('🔵 Demo login response:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('🔵 Demo login data received:', data.user?.email);
        setUser(data.user);
        console.log('🔵 Navigating to dashboard...');
        // Use navigate instead of window.location.href to avoid full reload
        navigate('/dashboard');
      } else {
        console.error('❌ Demo login failed:', response.status);
        alert('Demo login failed. Please try again or contact support.');
        setLoggingIn(false);
      }
    } catch (error) {
      console.error('❌ Demo login error:', error);
      alert('Network error. Please check your connection and try again.');
      setLoggingIn(false);
    }
  };

  const logout = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      });
      setUser(null);
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, demoLogin, logout, isAuthenticated: !!user }}>
      {loading ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
