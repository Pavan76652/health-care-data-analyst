import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/patients', label: 'Patient Analytics' },
  { to: '/predict', label: 'Prediction Tool' },
  { to: '/reports', label: 'Reports' },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-shell d-flex">
      <aside className="sidebar d-flex flex-column">
        <div className="sidebar-brand">
          🏥 Readmission Analytics
        </div>
        <nav className="sidebar-nav nav flex-column flex-grow-1 py-2">
          {links.map(({ to, label }) => (
            <NavLink key={to} to={to} className="nav-link">
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-top border-secondary border-opacity-25">
          <small className="d-block text-white-50 mb-2">{user?.name}</small>
          <button type="button" className="btn btn-outline-light btn-sm w-100" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>
      <main className="main-content flex-grow-1">{children}</main>
    </div>
  );
}
