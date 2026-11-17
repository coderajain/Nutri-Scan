import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Eye, HelpCircle } from 'lucide-react';

export const FindingBadge = ({ type }) => {
  const normType = (type || '').toLowerCase();

  switch (normType) {
    case 'pass':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>PASS</span>
        </span>
      );
    case 'fail':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800">
          <XCircle className="h-3.5 w-3.5" />
          <span>FAIL</span>
        </span>
      );
    case 'manual_review':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
          <Eye className="h-3.5 w-3.5" />
          <span>MANUAL REVIEW</span>
        </span>
      );
    case 'not_found':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-700">
          <HelpCircle className="h-3.5 w-3.5" />
          <span>NOT FOUND</span>
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
          <AlertTriangle className="h-3.5 w-3.5" />
          <span>{type?.toUpperCase() || 'INFO'}</span>
        </span>
      );
  }
};

export const SeverityBadge = ({ severity }) => {
  const norm = (severity || '').toLowerCase();
  switch (norm) {
    case 'critical':
      return <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase bg-red-600 text-white tracking-wider">Critical</span>;
    case 'major':
      return <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase bg-amber-500 text-white tracking-wider">Major</span>;
    case 'minor':
      return <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-slate-200 text-slate-700">Minor</span>;
    default:
      return <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-blue-100 text-blue-700">Notice</span>;
  }
};
