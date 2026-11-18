import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock, Mail, User, AlertCircle, ArrowRight } from 'lucide-react';
import logo from '../assets/logo.png';
import { AuthBackgroundVisual } from '../components/AuthBackgroundVisual';

export const Register = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register, login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    setLoading(true);
    try {
      await register(email, password, fullName);
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-[#06110E] via-[#081513] to-[#0B1726]">
      {/* Background Visual and 4 Angled 3D Floating Glass Cards */}
      <AuthBackgroundVisual />

      {/* Existing White Register Card Centered Dead-Center with Radial Glow */}
      <div className="relative z-10 flex items-center justify-center min-h-[calc(100vh-72px)] px-4 py-8">
        <div className="w-full max-w-md shadow-[0_0_80px_rgba(16,185,129,0.22)] rounded-3xl">
          <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
            <div className="text-center">
              <div className="flex justify-center mb-5">
                <Link to="/" className="inline-block">
                  <img src={logo} alt="NutriScan Logo" className="h-12 w-auto object-contain hover:opacity-90 transition" />
                </Link>
              </div>
              <h2 className="text-2xl font-black text-slate-900 tracking-tight">Create your account</h2>
              <p className="mt-1 text-xs text-slate-500">
                Sign up to scan and evaluate packaged food labels
              </p>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Alex Johnson"
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Password (Min 8 Characters)
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-4 bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 rounded-xl shadow-sm text-sm flex items-center justify-center space-x-2 transition disabled:opacity-50"
              >
                <span>{loading ? 'Creating Account...' : 'Register'}</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </form>

            <div className="text-center">
              <p className="text-xs text-slate-500">
                Already have an account?{' '}
                <Link to="/login" className="font-bold text-brand-600 hover:text-brand-700">
                  Sign In
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Register;
