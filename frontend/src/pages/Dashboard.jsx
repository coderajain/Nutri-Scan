import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { ScoreCards } from '../components/ScoreCards';
import { Disclaimers } from '../components/Disclaimers';
import { ScanLine, ArrowUpRight, Scale, HeartPulse, CheckCircle2, AlertTriangle, Layers, Clock } from 'lucide-react';

export const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await apiClient.get('/dashboard/stats');
        setStats(res.data);
      } catch (err) {
        console.error('Failed to load dashboard metrics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-3xl p-6 sm:p-8 text-white shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
        <div>
          <span className="text-xs font-bold text-brand-400 uppercase tracking-wider">Medi-Caps University Project-1</span>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight mt-1">
            Welcome back, {user?.full_name?.split(' ')[0]}!
          </h1>
          <p className="text-sm text-slate-300 mt-1 max-w-xl">
            Automated packaged commodity inspection system powered by computer vision, OCR, and versioned statutory rule engines.
          </p>
        </div>
        <Link
          to="/scan"
          className="bg-brand-500 hover:bg-brand-600 text-white font-bold px-6 py-3 rounded-2xl shadow-sm text-sm flex items-center space-x-2 transition shrink-0"
        >
          <ScanLine className="h-5 w-5" />
          <span>Start New Scan</span>
        </Link>
      </div>

      {/* Aggregate Metrics (DASH-001) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Total Scans</span>
            <Layers className="h-5 w-5 text-brand-600" />
          </div>
          <div className="mt-3 text-3xl font-black text-slate-900">{stats?.total_scans ?? 0}</div>
          <span className="text-[11px] text-slate-400 font-medium">Verified packaged commodities</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Avg Compliance</span>
            <Scale className="h-5 w-5 text-metrology-600" />
          </div>
          <div className="mt-3 text-3xl font-black text-metrology-600">
            {stats?.average_compliance_score !== null ? `${stats?.average_compliance_score}%` : 'N/A'}
          </div>
          <span className="text-[11px] text-slate-400 font-medium">LM-PC Rules, 2011 standard</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Avg Nutrition</span>
            <HeartPulse className="h-5 w-5 text-emerald-600" />
          </div>
          <div className="mt-3 text-3xl font-black text-emerald-600">
            {stats?.average_nutrition_score !== null ? `${stats?.average_nutrition_score}/100` : 'N/A'}
          </div>
          <span className="text-[11px] text-slate-400 font-medium">ICMR & WHO reference guidelines</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Fully Compliant</span>
            <CheckCircle2 className="h-5 w-5 text-emerald-600" />
          </div>
          <div className="mt-3 text-3xl font-black text-slate-900">
            {stats?.compliance_breakdown?.compliant ?? 0}
          </div>
          <span className="text-[11px] text-slate-400 font-medium">Zero critical regulatory defects</span>
        </div>
      </div>

      {/* Compliance & Nutrition Breakdown Cards (DASH-002, DASH-003) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <Scale className="h-4 w-4 text-metrology-600" />
            <span>Legal Metrology Compliance Breakdown</span>
          </h3>
          <div className="grid grid-cols-2 gap-3 mt-4 text-xs">
            <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100">
              <span className="text-emerald-700 font-semibold block">Compliant</span>
              <span className="text-xl font-black text-emerald-800">{stats?.compliance_breakdown?.compliant ?? 0}</span>
            </div>
            <div className="p-3 bg-rose-50 rounded-xl border border-rose-100">
              <span className="text-rose-700 font-semibold block">Non-Compliant</span>
              <span className="text-xl font-black text-rose-800">{stats?.compliance_breakdown?.non_compliant ?? 0}</span>
            </div>
            <div className="p-3 bg-amber-50 rounded-xl border border-amber-100">
              <span className="text-amber-700 font-semibold block">Partial Defect</span>
              <span className="text-xl font-black text-amber-800">{stats?.compliance_breakdown?.partial ?? 0}</span>
            </div>
            <div className="p-3 bg-blue-50 rounded-xl border border-blue-100">
              <span className="text-blue-700 font-semibold block">Manual Review Required</span>
              <span className="text-xl font-black text-blue-800">{stats?.compliance_breakdown?.manual_review_required ?? 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <HeartPulse className="h-4 w-4 text-brand-600" />
            <span>Nutritional Assessment Categories</span>
          </h3>
          <div className="grid grid-cols-3 gap-2 mt-4 text-xs">
            <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-center">
              <span className="text-emerald-700 font-semibold block text-[11px]">Excellent</span>
              <span className="text-lg font-black text-emerald-800">{stats?.nutrition_breakdown?.excellent ?? 0}</span>
            </div>
            <div className="p-3 bg-teal-50 rounded-xl border border-teal-100 text-center">
              <span className="text-teal-700 font-semibold block text-[11px]">Good</span>
              <span className="text-lg font-black text-teal-800">{stats?.nutrition_breakdown?.good ?? 0}</span>
            </div>
            <div className="p-3 bg-amber-50 rounded-xl border border-amber-100 text-center">
              <span className="text-amber-700 font-semibold block text-[11px]">Moderate</span>
              <span className="text-lg font-black text-amber-800">{stats?.nutrition_breakdown?.moderate ?? 0}</span>
            </div>
            <div className="p-3 bg-rose-50 rounded-xl border border-rose-100 text-center">
              <span className="text-rose-700 font-semibold block text-[11px]">High Risk</span>
              <span className="text-lg font-black text-rose-800">{stats?.nutrition_breakdown?.high_risk ?? 0}</span>
            </div>
            <div className="p-3 bg-slate-100 rounded-xl border border-slate-200 text-center col-span-2">
              <span className="text-slate-600 font-semibold block text-[11px]">Insufficient Label Data</span>
              <span className="text-lg font-black text-slate-700">{stats?.nutrition_breakdown?.insufficient_data ?? 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Scans Table (DASH-001) */}
      <div className="bg-white rounded-2xl border border-slate-200 mt-8 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4 text-slate-500" />
            <h2 className="text-sm font-bold text-slate-900">Recent Inspection Activity</h2>
          </div>
          <Link to="/history" className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center space-x-1">
            <span>View All Scans</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {stats?.recent_scans?.length > 0 ? (
          <div className="divide-y divide-slate-100 overflow-x-auto">
            {stats.recent_scans.map((scan) => (
              <div key={scan.id} className="p-4 sm:px-6 flex items-center justify-between hover:bg-slate-50 transition">
                <div className="flex items-center space-x-4">
                  <div className="p-2.5 bg-slate-100 rounded-xl">
                    <ScanLine className="h-5 w-5 text-slate-600" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">
                      {scan.product_name || 'Packaged Commodity (Unlabeled)'}
                    </h4>
                    <p className="text-xs text-slate-500">
                      {new Date(scan.created_at).toLocaleString()} &bull; Duration: {scan.scan_duration_ms ? `${scan.scan_duration_ms}ms` : 'N/A'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <span className="text-xs font-bold text-metrology-600 block">
                      Comp: {scan.compliance_score !== null ? `${scan.compliance_score}%` : 'N/A'}
                    </span>
                    <span className="text-xs font-bold text-emerald-600 block">
                      Nutri: {scan.nutrition_score !== null ? `${scan.nutrition_score}` : 'N/A'}
                    </span>
                  </div>
                  <Link
                    to={`/scan/${scan.id}`}
                    className="px-3 py-1.5 bg-slate-100 hover:bg-brand-50 hover:text-brand-700 text-slate-700 rounded-lg text-xs font-bold transition"
                  >
                    Details
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400 text-sm">
            No scans recorded yet. Click "Start New Scan" to begin.
          </div>
        )}
      </div>

      {/* Mandatory Statutory & Medical Disclaimers */}
      <Disclaimers />
    </div>
  );
};
export default Dashboard;
