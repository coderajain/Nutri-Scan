import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { ProtectedRoute } from './components/ProtectedRoute';

import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { ScanUpload } from './pages/ScanUpload';
import { ScanResults } from './pages/ScanResults';
import { History } from './pages/History';
import { AdminRules } from './pages/AdminRules';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <AuthProvider>
          <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-200">
            <Navbar />
            <main className="flex-1 flex flex-col">
              <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Protected Routes for Authenticated Users */}
                <Route element={<ProtectedRoute />}>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/scan" element={<ScanUpload />} />
                  <Route path="/scan/:id" element={<ScanResults />} />
                  <Route path="/history" element={<History />} />
                </Route>

                {/* Administrator Only Routes */}
                <Route element={<ProtectedRoute requireAdmin={true} />}>
                  <Route path="/admin/rules" element={<AdminRules />} />
                </Route>

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
