import React from 'react';
import { ShieldCheck } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-white border-t border-slate-200 mt-auto py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center sm:flex sm:justify-between sm:items-center">
        <div className="flex items-center justify-center sm:justify-start space-x-2 text-slate-700 text-sm font-medium">
          <ShieldCheck className="h-5 w-5 text-brand-600" />
          <span>NutriScan v1.0 &copy; 2026. Packaged Food Label & Regulatory Compliance Screening</span>
        </div>
        <p className="text-xs text-slate-500 mt-2 sm:mt-0">
          Automated Decision-Support System &bull; Legal Metrology & FSSAI Standards
        </p>
      </div>
    </footer>
  );
};
export default Footer;
