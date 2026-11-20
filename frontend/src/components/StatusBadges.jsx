import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Eye, HelpCircle, ShieldCheck } from 'lucide-react';

export const AuthenticityBadge = ({ status, score }) => {
  const norm = (status || '').toLowerCase();
  switch (norm) {
    case 'authentic':
      return (
        <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-black bg-emerald-100 dark:bg-emerald-950/90 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700/60 shadow-xs">
          <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
          <span>ORIGINAL / AUTHENTIC</span>
          {score !== undefined && score !== null && <span className="opacity-80 font-mono text-[11px]">({score}%)</span>}
        </span>
      );
    case 'suspicious':
      return (
        <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-black bg-rose-100 dark:bg-rose-950/90 text-rose-800 dark:text-rose-300 border border-rose-300 dark:border-rose-700/60 shadow-xs">
          <AlertTriangle className="h-4 w-4 text-rose-600 dark:text-rose-400" />
          <span>POTENTIAL FAKE / SUSPICIOUS</span>
          {score !== undefined && score !== null && <span className="opacity-80 font-mono text-[11px]">({score}%)</span>}
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-black bg-amber-100 dark:bg-amber-950/90 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700/60 shadow-xs">
          <CheckCircle2 className="h-4 w-4 text-amber-600 dark:text-amber-400" />
          <span>PARTIALLY VERIFIED</span>
          {score !== undefined && score !== null && <span className="opacity-80 font-mono text-[11px]">({score}%)</span>}
        </span>
      );
  }
};

export const FindingBadge = ({ type }) => {
  const normType = (type || '').toLowerCase();

  switch (normType) {
    case 'pass':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border border-transparent dark:border-emerald-800/50">
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>PASS</span>
        </span>
      );
    case 'fail':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 dark:bg-rose-950/80 text-rose-800 dark:text-rose-300 border border-transparent dark:border-rose-800/50">
          <XCircle className="h-3.5 w-3.5" />
          <span>FAIL</span>
        </span>
      );
    case 'manual_review':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border border-transparent dark:border-amber-800/50">
          <Eye className="h-3.5 w-3.5" />
          <span>MANUAL REVIEW</span>
        </span>
      );
    case 'not_found':
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-transparent dark:border-slate-700">
          <HelpCircle className="h-3.5 w-3.5" />
          <span>NOT FOUND</span>
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 dark:bg-blue-950/80 text-blue-800 dark:text-blue-300 border border-transparent dark:border-blue-800/50">
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
      return <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200">Minor</span>;
    default:
      return <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-transparent dark:border-blue-800">Notice</span>;
  }
};
