import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const DEMO_USER = { email: 'admin@hospital.com', password: 'admin123', name: 'Hospital Admin' };

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem('hr_user');
    if (stored) setUser(JSON.parse(stored));
  }, []);

  const login = (email, password) => {
    if (email === DEMO_USER.email && password === DEMO_USER.password) {
      const u = { email, name: DEMO_USER.name };
      localStorage.setItem('hr_user', JSON.stringify(u));
      setUser(u);
      return true;
    }
    return false;
  };

  const logout = () => {
    localStorage.removeItem('hr_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
