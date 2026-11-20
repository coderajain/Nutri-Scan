import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { ScanLine, LayoutDashboard, History, Settings, LogOut, User, Sun, Moon } from 'lucide-react';
import logo from '../assets/logo.png';

export const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md text-slate-800 dark:text-slate-100 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50 shadow-xs transition-colors duration-200">
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
              <div className="hidden sm:flex flex-col border-l border-slate-200 dark:border-slate-700 pl-3">
                <div className="flex items-center space-x-1.5">
                  <span className="text-[11px] font-bold tracking-wide uppercase text-slate-700 dark:text-slate-200">Audit & Screening</span>
                  <span className="text-[10px] px-1.5 py-0.2 font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 rounded border border-emerald-200 dark:border-emerald-800">v1.0</span>
                </div>
                <span className="text-[10px] text-slate-400 dark:text-slate-500 font-medium">
                  Food Safety & Legal Metrology
                </span>
              </div>
            </Link>
          </div>

          {/* Navigation Links & Theme Controls */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {user ? (
              <>
                <Link
                  to="/dashboard"
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/dashboard')
                      ? 'bg-slate-100 dark:bg-slate-800 text-brand-700 dark:text-brand-400 font-semibold'
                      : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
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
                      : 'bg-brand-50 dark:bg-emerald-950/60 text-brand-700 dark:text-brand-400 hover:bg-brand-100 dark:hover:bg-emerald-900/60'
                  }`}
                >
                  <ScanLine className="h-4 w-4" />
                  <span>New Scan</span>
                </Link>

                <Link
                  to="/history"
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
                    isActive('/history')
                      ? 'bg-slate-100 dark:bg-slate-800 text-brand-700 dark:text-brand-400 font-semibold'
                      : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <History className="h-4 w-4" />
                  <span className="hidden md:inline">History</span>
                </Link>

                {isAdmin && (
                  <Link
                    to="/admin/rules"
                    className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
                      isActive('/admin/rules')
                        ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 font-semibold'
                        : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    <Settings className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    <span className="hidden md:inline">Rule Manager</span>
                  </Link>
                )}

                {/* User Profile Badge & Logout */}
                <div className="flex items-center space-x-2 pl-2 sm:pl-3 border-l border-slate-200 dark:border-slate-700">
                  <div className="flex flex-col text-right hidden lg:block">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{user.full_name}</span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold">{user.role}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    title="Sign Out"
                    className="p-2 text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/50 rounded-lg transition"
                  >
                    <LogOut className="h-4 w-4" />
                  </button>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  to="/login"
                  className="text-sm font-semibold text-slate-700 dark:text-slate-200 hover:text-brand-600 dark:hover:text-brand-400 px-3 py-2 transition"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="bg-brand-600 hover:bg-brand-700 text-white text-sm font-semibold px-4 py-2 rounded-lg shadow-sm transition"
                >
                  Register
                </Link>
              </div>
            )}

            {/* Dark / Light Mode Toggle Button with Clear Label */}
            <button
              type="button"
              onClick={toggleTheme}
              aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border shadow-xs select-none
                bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-amber-300 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {isDark ? (
                <>
                  <Sun className="h-4 w-4 text-amber-400 shrink-0" />
                  <span className="hidden sm:inline">Light Mode</span>
                </>
              ) : (
                <>
                  <Moon className="h-4 w-4 text-slate-700 shrink-0" />
                  <span className="hidden sm:inline">Dark Mode</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
export default Navbar;
