import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('nutriscan_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const savedToken = localStorage.getItem('nutriscan_token');
      if (savedToken) {
        try {
          const res = await apiClient.get('/auth/me');
          setUser(res.data);
        } catch (err) {
          console.error('Session restoration failed:', err);
          logout();
        }
      }
      setLoading(false);
    };
    initializeAuth();
  }, []);

  const login = async (email, password) => {
    const res = await apiClient.post('/auth/login-json', { email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('nutriscan_token', access_token);
    localStorage.setItem('nutriscan_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const register = async (email, password, fullName) => {
    const res = await apiClient.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('nutriscan_token');
    localStorage.removeItem('nutriscan_user');
    setToken(null);
    setUser(null);
  };

  const isAdmin = user && user.role === 'administrator';

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
