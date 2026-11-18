import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ScanLine, LayoutDashboard, History, Settings, LogOut, User } from 'lucide-react';
import logo from '../assets/logo.png';

export const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-slate-950/75 backdrop-blur-md text-white border-b border-white/10 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Brand Logo & Academic Badge */}
          <div className="flex items-center space-x-3">
            <Link to="/" className="flex items-center space-x-3 group">
              <img
                src={logo}
                alt="NutriScan Logo"
                className="h-9 w-auto object-contain transition-transform group-hover:scale-105"
              />
              <div className="hidden sm:flex flex-col border-l border-white/10 pl-3">
                <div className="flex items-center space-x-1.5">
                  <span className="text-[11px] font-bold tracking-wide uppercase text-slate-200">Audit & Screening</span>
                  <span className="text-[10px] px-1.5 py-0.2 font-semibold bg-emerald-950/80 text-emerald-400 rounded border border-emerald-500/30">v1.0</span>
                </div>
                <span className="text-[10px] text-slate-400 font-medium">
                  Food Safety & Legal Metrology
                </span>
              </div>
            </Link>
          </div>

          {/* Navigation Links */}
          {user ? (
            <div className="flex items-center space-x-1 sm:space-x-3">
              <Link
                to="/dashboard"
                className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
                  isActive('/dashboard') ? 'bg-white/10 text-emerald-400 font-semibold' : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`}
              >
                <LayoutDashboard className="h-4 w-4" />
                <span className="hidden md:inline">Dashboard</span>
              </Link>

              <Link
                to="/scan"
                className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-sm font-semibold transition ${
                  isActive('/scan')
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-900/60'
                }`}
              >
                <ScanLine className="h-4 w-4" />
                <span>New Scan</span>
              </Link>

              <Link
                to="/history"
                className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
                  isActive('/history') ? 'bg-white/10 text-emerald-400 font-semibold' : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`}
              >
                <History className="h-4 w-4" />
                <span className="hidden md:inline">History</span>
              </Link>

              {isAdmin && (
                <Link
                  to="/admin/rules"
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/admin/rules') ? 'bg-blue-950/60 text-blue-400 border border-blue-500/30' : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <Settings className="h-4 w-4 text-blue-400" />
                  <span className="hidden md:inline">Rule Manager</span>
                </Link>
              )}

              {/* User Profile Badge & Logout */}
              <div className="flex items-center space-x-2 pl-3 border-l border-white/10">
                <div className="flex flex-col text-right hidden lg:block">
                  <span className="text-xs font-bold text-slate-200">{user.full_name}</span>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">{user.role}</span>
                </div>
                <button
                  onClick={handleLogout}
                  title="Sign Out"
                  className="p-2 text-slate-400 hover:text-red-400 hover:bg-white/5 rounded-lg transition"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-3">
              <Link
                to="/login"
                className="text-sm font-semibold text-slate-300 hover:text-white px-3 py-2 transition"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold px-4 py-2 rounded-lg shadow-sm transition"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
export default Navbar;
