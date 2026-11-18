import React from 'react';
import { ShieldCheck, CheckCircle2, Sparkles, Activity, QrCode } from 'lucide-react';

export const AuthBackgroundVisual = () => {
  return (
    <>
      {/* 1. Ambient Background Layer */}
      {/* Architectural Dot Grid Pattern */}
      <div
        className="absolute inset-0 pointer-events-none opacity-20"
        style={{
          backgroundImage: `radial-gradient(rgba(16, 185, 129, 0.28) 1.2px, transparent 1.2px), radial-gradient(rgba(6, 182, 212, 0.18) 1.2px, transparent 1.2px)`,
          backgroundSize: '36px 36px',
          backgroundPosition: '0 0, 18px 18px',
        }}
      />

      {/* Subtle Structural Grid Overlay */}
      <div
        className="absolute inset-0 pointer-events-none opacity-10"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(16, 185, 129, 0.12) 1px, transparent 1px), linear-gradient(to bottom, rgba(16, 185, 129, 0.12) 1px, transparent 1px)`,
          backgroundSize: '72px 72px',
        }}
      />

      {/* Soft Radial Ambient Glow Orbs */}
      <div className="absolute -top-32 -left-20 w-[550px] h-[550px] bg-emerald-500/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-1/3 -right-24 w-[650px] h-[650px] bg-emerald-400/10 rounded-full blur-[150px] pointer-events-none" />
      <div className="absolute -bottom-32 right-1/4 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[160px] pointer-events-none" />

      {/* 2. Right-Side Decorative Verification & Nutrition Visual (Desktop Only, pointer-events-none) */}
      <div className="hidden lg:flex flex-1 items-center justify-center pr-12 xl:pr-28 relative z-10 pointer-events-none select-none">
        <div className="relative w-full max-w-[420px] xl:max-w-[450px]">
          {/* Top Floating Glassmorphic Pill: Authenticity Verified */}
          <div className="absolute -top-5 -left-8 backdrop-blur-xl bg-slate-900/90 border border-emerald-500/40 rounded-full py-2 px-4 shadow-[0_10px_25px_rgba(0,0,0,0.5)] flex items-center space-x-2.5 text-xs font-bold text-emerald-300 animate-float-slow z-30">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            <span>✓ Authenticity Verified</span>
          </div>

          {/* Bottom Floating Glassmorphic Pill: Verified Nutrition Facts */}
          <div className="absolute -bottom-5 -right-6 backdrop-blur-xl bg-slate-900/90 border border-cyan-500/40 rounded-full py-2 px-4 shadow-[0_10px_25px_rgba(0,0,0,0.5)] flex items-center space-x-2.5 text-xs font-bold text-cyan-300 animate-float-reverse z-30">
            <Sparkles className="h-4 w-4 text-cyan-400 shrink-0" />
            <span>Verified Nutrition Facts</span>
          </div>

          {/* Abstract Product Verification Card */}
          <div className="backdrop-blur-2xl bg-slate-900/70 border border-emerald-500/30 rounded-3xl p-6 xl:p-7 shadow-[0_30px_70px_rgba(0,0,0,0.65)] relative overflow-hidden">
            {/* Ambient Card Holographic Sheen */}
            <div className="absolute -top-28 -right-28 w-56 h-56 bg-gradient-to-br from-emerald-400/20 via-cyan-400/15 to-transparent rounded-full blur-2xl pointer-events-none" />

            {/* Header / Security Badge */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-5">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 shadow-xs">
                  <ShieldCheck className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="text-xs font-black tracking-wider uppercase text-emerald-400 flex items-center space-x-1.5">
                    <span>SECURITY AUDIT PROTOCOL</span>
                  </h4>
                  <p className="text-[10px] text-slate-400 font-mono">
                    CRYPTO-SEAL: #8492-F91A-VERIFIED
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-1 bg-emerald-950/80 border border-emerald-500/30 px-2 py-0.5 rounded-full text-[10px] font-mono text-emerald-400">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>AUDITED</span>
              </div>
            </div>

            {/* Generic Holographic QR / Barcode Security Seal */}
            <div className="relative rounded-2xl p-4 bg-slate-950/85 border border-emerald-500/35 overflow-hidden mb-5">
              {/* Subtle ambient diagonal sheen */}
              <div className="absolute inset-0 bg-gradient-to-tr from-emerald-500/5 via-cyan-500/10 to-transparent pointer-events-none" />

              {/* Scanning Laser Line (5s vertical loop) */}
              <div className="absolute left-3 right-3 h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_14px_#34d399] animate-scan-laser pointer-events-none z-20">
                <div className="h-7 w-full -mt-7 bg-gradient-to-t from-emerald-400/20 to-transparent pointer-events-none" />
              </div>

              {/* Holographic Abstract QR & Barcode Graphics */}
              <div className="flex items-center justify-between space-x-4">
                {/* Abstract Stylized QR Code SVG */}
                <div className="p-2.5 bg-slate-900/90 rounded-xl border border-emerald-500/20 shadow-inner shrink-0">
                  <svg className="w-20 h-20 text-emerald-400" viewBox="0 0 64 64" fill="currentColor">
                    {/* Top-Left Finder Square */}
                    <rect x="4" y="4" width="18" height="18" rx="3" fill="none" stroke="currentColor" strokeWidth="3" />
                    <rect x="8" y="8" width="10" height="10" rx="1.5" />
                    {/* Top-Right Finder Square */}
                    <rect x="42" y="4" width="18" height="18" rx="3" fill="none" stroke="currentColor" strokeWidth="3" />
                    <rect x="46" y="8" width="10" height="10" rx="1.5" />
                    {/* Bottom-Left Finder Square */}
                    <rect x="4" y="42" width="18" height="18" rx="3" fill="none" stroke="currentColor" strokeWidth="3" />
                    <rect x="8" y="46" width="10" height="10" rx="1.5" />
                    {/* Micro data cells */}
                    <rect x="26" y="6" width="4" height="4" rx="0.5" />
                    <rect x="34" y="6" width="4" height="4" rx="0.5" />
                    <rect x="26" y="14" width="4" height="4" rx="0.5" />
                    <rect x="34" y="14" width="4" height="4" rx="0.5" />
                    <rect x="6" y="26" width="4" height="4" rx="0.5" />
                    <rect x="14" y="26" width="4" height="4" rx="0.5" />
                    <rect x="24" y="24" width="6" height="6" rx="1" fill="#06b6d4" />
                    <rect x="34" y="24" width="6" height="6" rx="1" fill="#06b6d4" />
                    <rect x="24" y="34" width="6" height="6" rx="1" fill="#06b6d4" />
                    <rect x="34" y="34" width="6" height="6" rx="1" fill="#06b6d4" />
                    <rect x="44" y="26" width="4" height="4" rx="0.5" />
                    <rect x="52" y="26" width="4" height="4" rx="0.5" />
                    <rect x="44" y="34" width="4" height="4" rx="0.5" />
                    <rect x="52" y="34" width="4" height="4" rx="0.5" />
                    <rect x="26" y="44" width="4" height="4" rx="0.5" />
                    <rect x="34" y="44" width="4" height="4" rx="0.5" />
                    <rect x="26" y="52" width="4" height="4" rx="0.5" />
                    <rect x="34" y="52" width="4" height="4" rx="0.5" />
                    <rect x="44" y="44" width="14" height="4" rx="1" />
                    <rect x="44" y="52" width="14" height="4" rx="1" />
                  </svg>
                </div>

                {/* Abstract Stylized 1D Barcode & Anti-Counterfeit Seal */}
                <div className="flex-1 space-y-2">
                  <div className="h-10 w-full flex items-center justify-between px-1 bg-slate-900/60 rounded-lg border border-slate-800">
                    {/* Barcode bars */}
                    <div className="w-1.5 h-7 bg-emerald-400 rounded-xs" />
                    <div className="w-0.5 h-7 bg-emerald-400/80 rounded-xs" />
                    <div className="w-2.5 h-7 bg-emerald-400 rounded-xs" />
                    <div className="w-1 h-7 bg-emerald-400/60 rounded-xs" />
                    <div className="w-3 h-7 bg-emerald-400 rounded-xs" />
                    <div className="w-0.5 h-7 bg-emerald-400/70 rounded-xs" />
                    <div className="w-2 h-7 bg-cyan-400 rounded-xs" />
                    <div className="w-1.5 h-7 bg-cyan-400 rounded-xs" />
                    <div className="w-0.5 h-7 bg-cyan-400/80 rounded-xs" />
                    <div className="w-2 h-7 bg-cyan-400 rounded-xs" />
                    <div className="w-3 h-7 bg-emerald-400 rounded-xs" />
                    <div className="w-1 h-7 bg-emerald-400/90 rounded-xs" />
                    <div className="w-1.5 h-7 bg-emerald-400 rounded-xs" />
                  </div>
                  <div className="flex items-center justify-between text-[9px] font-mono text-slate-400 px-0.5">
                    <span>GS1 VALIDATED</span>
                    <span className="text-cyan-400">8 901030 492015</span>
                  </div>
                </div>
              </div>

              {/* Tamper Evident Tag */}
              <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span className="text-emerald-400">TAMPER-EVIDENT DIGITAL SEAL</span>
                <span>FSSAI / LM-PC 2011</span>
              </div>
            </div>

            {/* Clean Abstract Nutrition Progress Bars (No product or brand names) */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-[11px] font-bold tracking-wider uppercase">
                <span className="text-slate-300 flex items-center space-x-1.5">
                  <Activity className="h-3.5 w-3.5 text-cyan-400" />
                  <span>Verified Nutritional Breakdown</span>
                </span>
                <span className="text-[9px] text-cyan-400 font-mono">DISCLOSED</span>
              </div>

              {/* Progress Bar 1 */}
              <div>
                <div className="flex justify-between text-[10px] font-medium text-slate-400 mb-1">
                  <span>Macronutrient Distribution Index</span>
                  <span className="text-emerald-400 font-mono font-bold">88%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full"
                    style={{ width: '88%' }}
                  />
                </div>
              </div>

              {/* Progress Bar 2 */}
              <div>
                <div className="flex justify-between text-[10px] font-medium text-slate-400 mb-1">
                  <span>Essential Density Ratio</span>
                  <span className="text-cyan-400 font-mono font-bold">94%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-teal-400 to-cyan-400 rounded-full"
                    style={{ width: '94%' }}
                  />
                </div>
              </div>

              {/* Progress Bar 3 */}
              <div>
                <div className="flex justify-between text-[10px] font-medium text-slate-400 mb-1">
                  <span>Regulatory Standard Alignment</span>
                  <span className="text-emerald-300 font-mono font-bold">100%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-400 to-emerald-400 rounded-full"
                    style={{ width: '100%' }}
                  />
                </div>
              </div>

              {/* Progress Bar 4 */}
              <div>
                <div className="flex justify-between text-[10px] font-medium text-slate-400 mb-1">
                  <span>Purity & Additive Transparency</span>
                  <span className="text-emerald-400 font-mono font-bold">Verified Pure</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full"
                    style={{ width: '82%' }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
