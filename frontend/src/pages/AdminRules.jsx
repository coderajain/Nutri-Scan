import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Settings, PlusCircle, CheckCircle2, Scale, AlertCircle, ShieldAlert } from 'lucide-react';
import { SeverityBadge } from '../components/StatusBadges';

export const AdminRules = () => {
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newVersionTag, setNewVersionTag] = useState('');
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchVersions = async () => {
    try {
      const res = await apiClient.get('/rules/versions');
      setVersions(res.data);
      if (res.data.length > 0) {
        setSelectedVersion(res.data[0]);
      }
    } catch (err) {
      console.error('Failed to load rules:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVersions();
  }, []);

  const handleCreateVersion = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const res = await apiClient.post('/rules/versions', {
        version_tag: newVersionTag,
        title: newTitle,
        description: newDesc,
        is_active: true,
      });
      setSuccess(`Created version ${res.data.version_tag} successfully!`);
      setShowCreateModal(false);
      setNewVersionTag('');
      setNewTitle('');
      setNewDesc('');
      fetchVersions();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create rule version.');
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">Administrator Control</span>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-1">
            Statutory Rules & Version Manager (LM-001, LM-006)
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Historical scans remain permanently linked to their evaluation rule version
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-sm transition"
        >
          <PlusCircle className="h-4 w-4" />
          <span>New Rule Version</span>
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center space-x-2">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center space-x-2">
          <CheckCircle2 className="h-4 w-4" />
          <span>{success}</span>
        </div>
      )}

      {/* Version Selector Tabs */}
      <div className="flex space-x-2 overflow-x-auto pb-2 border-b border-slate-200 mb-6">
        {versions.map((v) => (
          <button
            key={v.id}
            onClick={() => setSelectedVersion(v)}
            className={`px-4 py-2 rounded-xl text-xs font-bold shrink-0 transition flex items-center space-x-2 ${
              selectedVersion?.id === v.id
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            <Scale className="h-4 w-4" />
            <span>{v.version_tag}</span>
            {v.is_active && (
              <span className="text-[10px] bg-emerald-400 text-emerald-950 px-1.5 py-0.2 rounded-full font-extrabold">
                Active
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Rules Table */}
      {selectedVersion && (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-6 bg-slate-50 border-b border-slate-200">
            <h3 className="text-base font-extrabold text-slate-900">{selectedVersion.title}</h3>
            <p className="text-xs text-slate-500 mt-1">{selectedVersion.description}</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 uppercase tracking-wider text-[10px] font-extrabold">
                <tr>
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Rule Title & Statutory Reference</th>
                  <th className="py-3 px-4">Field</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Mandatory</th>
                  <th className="py-3 px-4">Validation Type</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {selectedVersion.rules?.map((rule) => (
                  <tr key={rule.id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-mono font-bold text-blue-700">{rule.rule_code}</td>
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-900">{rule.title}</div>
                      <div className="text-[11px] text-slate-500 italic">{rule.legal_reference}</div>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-600">{rule.field_name}</td>
                    <td className="py-3 px-4">
                      <SeverityBadge severity={rule.severity} />
                    </td>
                    <td className="py-3 px-4">
                      {rule.is_mandatory ? (
                        <span className="text-red-600 font-extrabold">YES</span>
                      ) : (
                        <span className="text-slate-400">NO</span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500">{rule.validation_type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Version Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full border border-slate-200 shadow-xl">
            <h3 className="text-lg font-black text-slate-900">Create New Statutory Rule Version</h3>
            <p className="text-xs text-slate-500 mt-1">
              Adding a new version preserves older scans linked to prior versions (LM-006).
            </p>

            <form onSubmit={handleCreateVersion} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Version Tag</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. LM-PC-2011-v2.0"
                  value={newVersionTag}
                  onChange={(e) => setNewVersionTag(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Legal Metrology Amendment 2026 Ruleset"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Description</label>
                <textarea
                  rows={3}
                  placeholder="Notes on regulatory updates..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition"
                >
                  Create Version
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default AdminRules;
