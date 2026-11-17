import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';

export const Disclaimers = () => {
  return (
    <div className="bg-amber-50/80 border border-amber-200 rounded-2xl p-4 my-6 text-xs text-amber-900 leading-relaxed shadow-xs">
      <div className="flex items-center space-x-2 font-bold mb-2 text-amber-950">
        <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
        <span className="uppercase tracking-wide text-[11px]">Academic & Regulatory Disclaimers (SRS Mandate)</span>
      </div>
      <ul className="space-y-1.5 list-disc pl-5 text-amber-800">
        <li>
          <b>Automated Screening Tool (SAF-001, LM-007):</b> NutriScan v1.0 provides automated decision-support screening for educational and inspection evaluation. It does NOT constitute a statutory or legally binding certification under the Legal Metrology Act, 2009 or FSSAI Regulations.
        </li>
        <li>
          <b>Informational Nutritional Assessment (SAF-002):</b> Nutritional indicators, additive flags, and health profile scores represent informational reference estimates derived from label declarations. They do NOT provide medical diagnosis, clinical treatment, or personalized medical advice.
        </li>
        <li>
          <b>Physical Packaging Dimensions (LM-005):</b> Physical properties (e.g. printed font heights in millimeters per Table II of LM-PC Rules 2011) cannot be conclusively certified from digital photographs without physical scale calibration references and are marked for <b>Manual Review</b>.
        </li>
      </ul>
    </div>
  );
};
export default Disclaimers;
