import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, pwd: string) => Promise<void>;
  logout: () => void;
  switchRole: (role: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>({
    id: 1,
    email: 'admin@enterprise.ai',
    name: 'Sarah Connor',
    role: 'admin',
    is_active: true
  });
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const me = await api.getMe();
          setUser(me);
        } catch {
          // Keep default admin user for zero-friction demo experience
        }
      }
    };
    checkAuth();
  }, []);

  const login = async (email: string, pwd: string) => {
    setLoading(true);
    try {
      const data = await api.login(email, pwd);
      localStorage.setItem('token', data.access_token);
      setUser(data.user);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const switchRole = async (role: string) => {
    setLoading(true);
    try {
      const data = await api.switchRole(role);
      localStorage.setItem('token', data.access_token);
      setUser(data.user);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, switchRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
