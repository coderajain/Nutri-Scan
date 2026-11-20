import React from 'react';
import { Scale, HeartPulse, AlertCircle, CheckCircle2 } from 'lucide-react';

export const ScoreCards = ({
  complianceScore,
  complianceStatus,
  nutritionScore,
  nutritionStatus,
  isDataInsufficient,
  hasFontSizeFlags,
}) => {
  // Score 1: Legal Metrology Compliance Score (SCORE-001)
  const getCompColor = (score) => {
    if (score >= 90) return { bg: 'bg-emerald-50 dark:bg-emerald-950/30', text: 'text-emerald-700 dark:text-emerald-400', border: 'border-emerald-200 dark:border-emerald-800/60', ring: 'ring-emerald-600' };
    if (score >= 60) return { bg: 'bg-amber-50 dark:bg-amber-950/30', text: 'text-amber-700 dark:text-amber-400', border: 'border-amber-200 dark:border-amber-800/60', ring: 'ring-amber-500' };
    return { bg: 'bg-rose-50 dark:bg-rose-950/30', text: 'text-rose-700 dark:text-rose-400', border: 'border-rose-200 dark:border-rose-800/60', ring: 'ring-rose-600' };
  };

  // Score 2: Nutritional Profile Score (SCORE-002)
  const getNutriColor = (score) => {
    if (score === null || score === undefined) return { bg: 'bg-slate-50 dark:bg-slate-900', text: 'text-slate-600 dark:text-slate-400', border: 'border-slate-200 dark:border-slate-800', ring: 'ring-slate-400' };
    if (score >= 70) return { bg: 'bg-emerald-50 dark:bg-emerald-950/30', text: 'text-emerald-700 dark:text-emerald-400', border: 'border-emerald-200 dark:border-emerald-800/60', ring: 'ring-emerald-600' };
    if (score >= 50) return { bg: 'bg-amber-50 dark:bg-amber-950/30', text: 'text-amber-700 dark:text-amber-400', border: 'border-amber-200 dark:border-amber-800/60', ring: 'ring-amber-500' };
    return { bg: 'bg-rose-50 dark:bg-rose-950/30', text: 'text-rose-700 dark:text-rose-400', border: 'border-rose-200 dark:border-rose-800/60', ring: 'ring-rose-600' };
  };

  const compStyle = getCompColor(complianceScore ?? 0);
  const nutriStyle = getNutriColor(nutritionScore);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-6">
      {/* CARD 1: Legal Metrology Compliance (Packaged Commodities) Rules, 2011 */}
      <div className={`p-6 rounded-2xl border ${compStyle.border} ${compStyle.bg} shadow-sm relative overflow-hidden transition-colors`}>
        <div className="flex justify-between items-start">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-white dark:bg-slate-800 rounded-xl shadow-xs border border-slate-100 dark:border-slate-700">
              <Scale className="h-6 w-6 text-metrology-600 dark:text-metrology-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Legal Metrology Compliance</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">LM-PC Rules, 2011 & FSSAI Mandatory Declarations</p>
            </div>
          </div>
          <span className="text-xs uppercase font-extrabold px-2.5 py-1 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-full border border-slate-200 dark:border-slate-700 shadow-2xs">
            {complianceStatus?.replace('_', ' ')}
          </span>
        </div>

        <div className="mt-5 flex items-baseline space-x-2">
          <span className={`text-4xl font-black tracking-tight ${compStyle.text}`}>
            {complianceScore !== null ? `${complianceScore}%` : 'N/A'}
          </span>
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Statutory Score</span>
        </div>

        <div className="mt-4 pt-4 border-t border-slate-200/60 dark:border-slate-700/60 text-xs text-slate-600 dark:text-slate-400 space-y-1">
          <div className="flex items-center justify-between">
            <span>Assessment Model:</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200">LM-PC-2011 v1.0 Standard</span>
          </div>
          {hasFontSizeFlags && (
            <div className="flex items-center space-x-1.5 text-amber-700 dark:text-amber-400 font-medium pt-1">
              <AlertCircle className="h-3.5 w-3.5 shrink-0" />
              <span>Physical font height flagged for Manual Review (LM-005)</span>
            </div>
          )}
        </div>
      </div>

      {/* CARD 2: Nutritional Profile Assessment (ICMR & WHO Reference) */}
      <div className={`p-6 rounded-2xl border ${nutriStyle.border} ${nutriStyle.bg} shadow-sm relative overflow-hidden transition-colors`}>
        <div className="flex justify-between items-start">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-white dark:bg-slate-800 rounded-xl shadow-xs border border-slate-100 dark:border-slate-700">
              <HeartPulse className="h-6 w-6 text-brand-600 dark:text-brand-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Nutritional Profile Score</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">ICMR-NIN & WHO Dietary Guidelines Assessment</p>
            </div>
          </div>
          <span className="text-xs uppercase font-extrabold px-2.5 py-1 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-full border border-slate-200 dark:border-slate-700 shadow-2xs">
            {nutritionStatus?.replace('_', ' ')}
          </span>
        </div>

        <div className="mt-5 flex items-baseline space-x-2">
          {isDataInsufficient || nutritionScore === null ? (
            <span className="text-2xl font-black text-slate-500 dark:text-slate-400">Insufficient Data</span>
          ) : (
            <span className={`text-4xl font-black tracking-tight ${nutriStyle.text}`}>
              {nutritionScore} <span className="text-xl font-medium text-slate-400 dark:text-slate-500">/ 100</span>
            </span>
          )}
        </div>

        <div className="mt-4 pt-4 border-t border-slate-200/60 dark:border-slate-700/60 text-xs text-slate-600 dark:text-slate-400 space-y-1">
          <div className="flex items-center justify-between">
            <span>Scientific Basis:</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200">Nutrient profiling (Sugar/Fat/Sodium)</span>
          </div>
          {isDataInsufficient ? (
            <div className="flex items-center space-x-1.5 text-slate-500 dark:text-slate-400 font-medium pt-1">
              <AlertCircle className="h-3.5 w-3.5 shrink-0" />
              <span>Fewer than 3 mandatory nutrients were declared on label</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 text-brand-700 dark:text-brand-400 font-medium pt-1">
              <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
              <span>Evaluated per 100g/ml standard reference</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default ScoreCards;
