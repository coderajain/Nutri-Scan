import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { Search, Filter, History as HistoryIcon, ArrowRight, ChevronLeft, ChevronRight, FileText } from 'lucide-react';

export const History = () => {
  const [scans, setScans] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [complianceFilter, setComplianceFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        per_page: 10,
      };
      if (search) params.product_name = search;
      if (complianceFilter) params.compliance_status = complianceFilter;

      const res = await apiClient.get('/history', { params });
      setScans(res.data.items);
      setTotal(res.data.total);
      setTotalPages(res.data.total_pages);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, complianceFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <span className="text-xs font-bold text-brand-600 uppercase tracking-wider">Repository</span>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-1">
            Inspection History & Audit Trail
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Browse, filter, and inspect previously scanned packaged food commodities
          </p>
        </div>

        <Link
          to="/scan"
          className="bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-sm transition"
        >
          New Scan
        </Link>
      </div>

      {/* Filter and Search Bar (HIS-002) */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs mb-6 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <form onSubmit={handleSearchSubmit} className="sm:col-span-2 relative">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by product name or brand..."
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-brand-500 focus:outline-none focus:bg-white"
          />
        </form>

        <div>
          <select
            value={complianceFilter}
            onChange={(e) => {
              setComplianceFilter(e.target.value);
              setPage(1);
            }}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold focus:ring-2 focus:ring-brand-500 focus:outline-none focus:bg-white text-slate-700"
          >
            <option value="">All Compliance Statuses</option>
            <option value="compliant">Compliant</option>
            <option value="non_compliant">Non-Compliant</option>
            <option value="partial">Partial</option>
            <option value="manual_review_required">Manual Review</option>
          </select>
        </div>
      </div>

      {/* Paginated Results Table (HIS-004, NFR-PERF-006) */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
        {loading ? (
          <div className="py-20 flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600"></div>
          </div>
        ) : scans.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider text-[10px] font-extrabold">
                <tr>
                  <th className="py-3 px-6">Product / Brand</th>
                  <th className="py-3 px-6">Compliance Score</th>
                  <th className="py-3 px-6">Nutritional Score</th>
                  <th className="py-3 px-6">Timestamp</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {scans.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-4 px-6">
                      <div className="font-bold text-slate-900 text-sm">
                        {s.product_name || 'Packaged Commodity (Unlabeled)'}
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono">ID: {s.id.substring(0, 8)}</div>
                    </td>
                    <td className="py-4 px-6">
                      <span className={`inline-block font-extrabold px-2.5 py-1 rounded-lg text-xs ${
                        s.compliance_score >= 90
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : s.compliance_score >= 60
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-rose-50 text-rose-700 border border-rose-200'
                      }`}>
                        {s.compliance_score !== null ? `${s.compliance_score}%` : 'N/A'}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <span className="font-bold text-slate-700">
                        {s.nutrition_score !== null ? `${s.nutrition_score} / 100` : <span className="text-slate-400 font-normal">Insufficient Data</span>}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-slate-500">
                      {new Date(s.created_at).toLocaleDateString()} &bull; {new Date(s.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-4 px-6 text-right">
                      <Link
                        to={`/scan/${s.id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 bg-slate-100 hover:bg-brand-50 hover:text-brand-700 text-slate-700 font-bold rounded-lg transition"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center text-slate-400 text-sm">
            No historical inspection records match your filters.
          </div>
        )}

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-between items-center text-xs">
            <span className="text-slate-500">
              Showing page <b>{page}</b> of <b>{totalPages}</b> ({total} total scans)
            </span>
            <div className="flex space-x-1">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 transition"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 transition"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
export default History;
