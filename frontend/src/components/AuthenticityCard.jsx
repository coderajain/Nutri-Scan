import React from 'react';
import { ShieldCheck, AlertTriangle, HelpCircle, CheckCircle2, XCircle, Info, Sparkles, Building2, Phone, QrCode, Tag, Award, Hash } from 'lucide-react';

export const AuthenticityCard = ({
  authenticityScore = 0,
  authenticityStatus = 'inconclusive',
  authenticityBreakdown = {},
  productName,
  brandName,
}) => {
  const isAuthentic = authenticityStatus === 'authentic';
  const isSuspicious = authenticityStatus === 'suspicious';

  const pillars = [
    {
      key: 'brand_identity',
      label: 'Brand & Product Identity',
      icon: Award,
      data: authenticityBreakdown?.brand_identity,
    },
    {
      key: 'regulatory_licensing',
      label: 'FSSAI License / Registration',
      icon: ShieldCheck,
      data: authenticityBreakdown?.regulatory_licensing,
    },
    {
      key: 'company_registration',
      label: 'Manufacturer & Company Details',
      icon: Building2,
      data: authenticityBreakdown?.company_registration,
    },
    {
      key: 'consumer_care',
      label: 'Consumer Care & Helpline',
      icon: Phone,
      data: authenticityBreakdown?.consumer_care,
    },
    {
      key: 'traceability',
      label: 'Batch Traceability & Dates',
      icon: Hash,
      data: authenticityBreakdown?.traceability,
    },
    {
      key: 'barcode_identification',
      label: 'Barcode & Supply Chain Code',
      icon: QrCode,
      data: authenticityBreakdown?.barcode_identification,
    },
  ];

  return (
    <div className={`rounded-3xl p-6 sm:p-8 mb-6 border shadow-sm transition-all ${
      isAuthentic
        ? 'bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent border-emerald-500/30 dark:border-emerald-500/20'
        : isSuspicious
        ? 'bg-gradient-to-br from-rose-500/10 via-rose-500/5 to-transparent border-rose-500/30 dark:border-rose-500/20'
        : 'bg-gradient-to-br from-amber-500/10 via-amber-500/5 to-transparent border-amber-500/30 dark:border-amber-500/20'
    }`}>
      {/* Top Header Badge & Verdict */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200/60 dark:border-slate-800/80">
        <div className="flex items-start space-x-4">
          <div className={`p-3.5 rounded-2xl shrink-0 shadow-xs border ${
            isAuthentic
              ? 'bg-emerald-500 text-white border-emerald-400 dark:border-emerald-600 shadow-emerald-500/20'
              : isSuspicious
              ? 'bg-rose-500 text-white border-rose-400 dark:border-rose-600 shadow-rose-500/20'
              : 'bg-amber-500 text-white border-amber-400 dark:border-amber-600 shadow-amber-500/20'
          }`}>
            {isAuthentic ? (
              <ShieldCheck className="h-8 w-8 stroke-[2.2]" />
            ) : isSuspicious ? (
              <AlertTriangle className="h-8 w-8 stroke-[2.2]" />
            ) : (
              <Sparkles className="h-8 w-8 stroke-[2.2]" />
            )}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase ${
                isAuthentic
                  ? 'bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300'
                  : isSuspicious
                  ? 'bg-rose-100 dark:bg-rose-950/80 text-rose-800 dark:text-rose-300'
                  : 'bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300'
              }`}>
                {isAuthentic ? 'Authenticity Screening: PASSED' : isSuspicious ? 'Authenticity Alert: HIGH RISK' : 'Authenticity Screening: PARTIAL'}
              </span>
              <span className="text-xs text-slate-400 dark:text-slate-500">&bull;</span>
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Anti-Counterfeit Check</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-slate-100 tracking-tight mt-1">
              {isAuthentic
                ? 'ORIGINAL / GENUINE PRODUCT'
                : isSuspicious
                ? 'POTENTIALLY COUNTERFEIT / FAKE'
                : 'PARTIALLY VERIFIED PACKAGING'}
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 mt-1 max-w-2xl leading-relaxed">
              {isAuthentic
                ? `Legitimate packaging declarations verified for ${brandName || 'Brand'} ${productName || ''}. Genuine brand identity, statutory FSSAI licensing, company registration, and consumer care channels are legibly printed.`
                : isSuspicious
                ? 'Critical statutory authenticity markers are missing or unregistered. High risk of counterfeit packaging or illicit commodity.'
                : 'Key authenticity markers detected; upload additional packaging faces or closer photos of the batch rim stamp for 100% confirmation.'}
            </p>
          </div>
        </div>

        {/* Authenticity Score Meter */}
        <div className="flex flex-row md:flex-col items-center md:items-end justify-between shrink-0 bg-white dark:bg-slate-900/80 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xs">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Authenticity Index</span>
          <div className="flex items-baseline space-x-1.5 mt-0.5">
            <span className={`text-3xl sm:text-4xl font-black tracking-tight ${
              isAuthentic
                ? 'text-emerald-600 dark:text-emerald-400'
                : isSuspicious
                ? 'text-rose-600 dark:text-rose-400'
                : 'text-amber-600 dark:text-amber-400'
            }`}>
              {authenticityScore}%
            </span>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-semibold">Confidence</span>
          </div>
        </div>
      </div>

      {/* The 6 Core Authenticity Pillars Checklist */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Mandatory Authenticity Pillars Checklist
          </h3>
          <span className="text-[11px] text-slate-400 dark:text-slate-500 font-medium">
            Based on Legal Metrology & FSSAI Standards
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {pillars.map((pillar) => {
            const Icon = pillar.icon;
            const status = pillar.data?.status || 'missing';
            const isVerified = status === 'verified';
            const isPartial = status === 'partial';

            return (
              <div
                key={pillar.key}
                className={`p-4 rounded-2xl border transition-all ${
                  isVerified
                    ? 'bg-emerald-50/60 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/40 text-emerald-900 dark:text-emerald-200'
                    : isPartial
                    ? 'bg-amber-50/60 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800/40 text-amber-900 dark:text-amber-200'
                    : 'bg-slate-50/80 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center space-x-2 min-w-0">
                    <Icon className={`h-4 w-4 shrink-0 ${
                      isVerified ? 'text-emerald-600 dark:text-emerald-400' : isPartial ? 'text-amber-600 dark:text-amber-400' : 'text-slate-400'
                    }`} />
                    <h4 className="text-xs font-bold truncate text-slate-800 dark:text-slate-100">{pillar.label}</h4>
                  </div>
                  {isVerified ? (
                    <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300 shrink-0">
                      <CheckCircle2 className="h-3 w-3" />
                      <span>Verified</span>
                    </span>
                  ) : isPartial ? (
                    <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300 shrink-0">
                      <span>Partial</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 shrink-0">
                      <XCircle className="h-3 w-3" />
                      <span>Missing</span>
                    </span>
                  )}
                </div>

                <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-2 font-mono line-clamp-2 leading-relaxed">
                  {pillar.data?.details || 'Not detected on scanned packaging view'}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Physical Font Size Advisory Callout */}
      <div className="mt-5 p-3.5 rounded-2xl bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400 flex items-start space-x-3">
        <Info className="h-4 w-4 text-slate-400 shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="text-slate-700 dark:text-slate-300">Notice on Font Dimensions:</strong> Printed numeral height in millimeters is an advisory laboratory metric under Table II of LM-PC Rules. It cannot be conclusively verified from a smartphone photo without physical scale calibration and <strong className="text-slate-700 dark:text-slate-300">does not affect this product's authentic status</strong>.
        </p>
      </div>
    </div>
  );
};
