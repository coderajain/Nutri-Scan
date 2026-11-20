import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock, Mail, AlertCircle, ArrowRight } from 'lucide-react';
import logo from '../assets/logo.png';
import { AuthBackgroundVisual } from '../components/AuthBackgroundVisual';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (type) => {
    if (type === 'admin') {
      setEmail('admin@nutriscan.local');
      setPassword('AdminPassword@2026!');
    } else {
      setEmail('demo@nutriscan.local');
      setPassword('DemoPassword@2026!');
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-100 via-emerald-50/50 to-teal-50/40 dark:from-[#06110E] dark:via-[#081513] dark:to-[#0B1726] transition-colors duration-300">
      {/* Background Visual and 4 Angled 3D Floating Glass Cards */}
      <AuthBackgroundVisual />

      {/* Existing White/Dark Login Card Centered Dead-Center with Radial Glow */}
      <div className="relative z-10 flex items-center justify-center min-h-[calc(100vh-72px)] px-4 py-8">
        <div className="w-full max-w-md shadow-xl dark:shadow-[0_0_80px_rgba(16,185,129,0.22)] rounded-3xl transition-shadow">
          <div className="max-w-md w-full space-y-8 bg-white dark:bg-slate-900/95 dark:backdrop-blur-md p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
            {/* Header */}
            <div className="text-center">
              <div className="flex justify-center mb-5">
                <Link to="/" className="inline-block">
                  <img src={logo} alt="NutriScan Logo" className="h-12 w-auto object-contain hover:opacity-90 transition" />
                </Link>
              </div>
              <h2 className="text-2xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Sign in to your account</h2>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                Packaged Food Regulatory & Nutritional Audit System
              </p>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900/60 text-red-700 dark:text-red-300 text-xs flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-400 dark:text-slate-500" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white dark:focus:bg-slate-800 transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-3 h-4 w-4 text-slate-400 dark:text-slate-500" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white dark:focus:bg-slate-800 transition"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-4 bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 rounded-xl shadow-sm text-sm flex items-center justify-center space-x-2 transition disabled:opacity-50"
              >
                <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </form>

            {/* Demo User Fast Fill */}
            <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
              <p className="text-center text-xs font-semibold text-slate-400 dark:text-slate-500 mb-2">Academic Demo Fast Login:</p>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => fillCredentials('demo')}
                  className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-medium transition"
                >
                  Demo Evaluator
                </button>
                <button
                  type="button"
                  onClick={() => fillCredentials('admin')}
                  className="px-3 py-1.5 bg-blue-50 dark:bg-blue-950/60 hover:bg-blue-100 dark:hover:bg-blue-900/60 text-blue-700 dark:text-blue-300 rounded-lg text-xs font-medium transition"
                >
                  Administrator
                </button>
              </div>
            </div>

            <div className="text-center">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Don't have an account?{' '}
                <Link to="/register" className="font-bold text-brand-600 dark:text-brand-400 hover:text-brand-700">
                  Create an account
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Login;
