import React from 'react';
import { ShieldCheck, CheckCircle2, Activity, QrCode, Check, Sparkles } from 'lucide-react';

export const AuthBackgroundVisual = () => {
  return (
    <>
      {/* 1. Ambient Background Grid & Centered Radial Glow Aura */}
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

      {/* Large Soft Radial Emerald & Cyan Aura Centered Directly Behind the Login Card */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-gradient-to-r from-emerald-500/20 via-teal-500/15 to-cyan-500/20 rounded-full blur-[140px] pointer-events-none z-0" />

      {/* Ambient Corner Glow Orbs */}
      <div className="absolute -top-32 -left-20 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[140px] pointer-events-none z-0" />
      <div className="absolute -bottom-32 -right-20 w-[550px] h-[550px] bg-cyan-500/10 rounded-full blur-[150px] pointer-events-none z-0" />

      {/* 2. Four Angled 3D Floating Glass Cards in Perspective Container (hidden lg:block pointer-events-none) */}
      <div
        className="hidden lg:block absolute inset-0 pointer-events-none select-none overflow-hidden z-0"
        style={{ perspective: '1100px' }}
      >
        {/* --- LEFT SIDE CARDS (rotateY(16deg)) --- */}

        {/* 1. TOP-LEFT CARD: ✓ BATCH & SEAL VERIFIED */}
        <div
          className="absolute top-[8%] left-[2%] xl:left-[5%] w-[310px] xl:w-[340px] animate-float-3d-lt"
          style={{ transformStyle: 'preserve-3d' }}
        >
          <div className="bg-slate-900/60 backdrop-blur-md border border-emerald-400/20 rounded-2xl shadow-2xl p-5">
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-emerald-500/20 mb-3.5">
              <div className="flex items-center space-x-2">
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-xs font-black tracking-wider uppercase text-emerald-400 flex items-center space-x-1">
                  <span>✓ BATCH &amp; SEAL VERIFIED</span>
                </span>
              </div>
              <span className="text-[10px] font-mono text-emerald-400/80 bg-emerald-950/70 border border-emerald-500/30 px-1.5 py-0.5 rounded">
                SEC-ID #8920
              </span>
            </div>

            {/* Vector Barcode & QR Security Seal Container */}
            <div className="relative rounded-xl p-3 bg-slate-950/85 border border-emerald-500/30 overflow-hidden mb-3">
              {/* Sweeping Laser Line with Beam Effect */}
              <div className="absolute left-2 right-2 h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_12px_#34d399] animate-laser-sweep pointer-events-none z-10">
                <div className="h-6 w-full -mt-6 bg-gradient-to-t from-emerald-400/20 to-transparent pointer-events-none" />
              </div>

              <div className="flex items-center justify-between space-x-3">
                {/* Clean Vector QR Code */}
                <div className="p-1.5 bg-slate-900/90 rounded-lg border border-emerald-500/25 shrink-0">
                  <svg className="w-14 h-14 text-emerald-400" viewBox="0 0 48 48" fill="currentColor">
                    {/* Top-Left Finder */}
                    <rect x="2" y="2" width="14" height="14" rx="2" fill="none" stroke="currentColor" strokeWidth="2.5" />
                    <rect x="5" y="5" width="8" height="8" rx="1" />
                    {/* Top-Right Finder */}
                    <rect x="32" y="2" width="14" height="14" rx="2" fill="none" stroke="currentColor" strokeWidth="2.5" />
                    <rect x="35" y="5" width="8" height="8" rx="1" />
                    {/* Bottom-Left Finder */}
                    <rect x="2" y="32" width="14" height="14" rx="2" fill="none" stroke="currentColor" strokeWidth="2.5" />
                    <rect x="5" y="35" width="8" height="8" rx="1" />
                    {/* Data Cells */}
                    <rect x="20" y="4" width="3" height="3" />
                    <rect x="26" y="4" width="3" height="3" />
                    <rect x="20" y="10" width="3" height="3" />
                    <rect x="26" y="10" width="3" height="3" />
                    <rect x="18" y="18" width="5" height="5" fill="#06b6d4" rx="1" />
                    <rect x="26" y="18" width="5" height="5" fill="#06b6d4" rx="1" />
                    <rect x="18" y="26" width="5" height="5" fill="#06b6d4" rx="1" />
                    <rect x="26" y="26" width="5" height="5" fill="#06b6d4" rx="1" />
                    <rect x="34" y="20" width="3" height="3" />
                    <rect x="40" y="20" width="3" height="3" />
                    <rect x="34" y="26" width="3" height="3" />
                    <rect x="40" y="26" width="3" height="3" />
                    <rect x="20" y="34" width="3" height="3" />
                    <rect x="26" y="34" width="3" height="3" />
                    <rect x="20" y="40" width="3" height="3" />
                    <rect x="26" y="40" width="3" height="3" />
                    <rect x="34" y="34" width="10" height="3" />
                    <rect x="34" y="40" width="10" height="3" />
                  </svg>
                </div>

                {/* Vector Barcode Lines */}
                <div className="flex-1 space-y-1.5">
                  <div className="h-8 w-full flex items-center justify-between px-1 bg-slate-900/60 rounded border border-slate-800">
                    <div className="w-1.5 h-6 bg-emerald-400 rounded-xs" />
                    <div className="w-0.5 h-6 bg-emerald-400/80 rounded-xs" />
                    <div className="w-2.5 h-6 bg-emerald-400 rounded-xs" />
                    <div className="w-1 h-6 bg-emerald-400/60 rounded-xs" />
                    <div className="w-2 h-6 bg-cyan-400 rounded-xs" />
                    <div className="w-0.5 h-6 bg-cyan-400/70 rounded-xs" />
                    <div className="w-1.5 h-6 bg-cyan-400 rounded-xs" />
                    <div className="w-2.5 h-6 bg-emerald-400 rounded-xs" />
                    <div className="w-1 h-6 bg-emerald-400/80 rounded-xs" />
                    <div className="w-1.5 h-6 bg-emerald-400 rounded-xs" />
                  </div>
                  <div className="flex justify-between text-[8px] font-mono text-slate-400 px-0.5">
                    <span>GS1 VALIDATED</span>
                    <span className="text-cyan-400 font-bold">8901030 492015</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between text-[9px] font-mono text-slate-400">
              <span className="text-emerald-400">HOLOGRAPHIC SEAL: INTACT</span>
              <span>LM-PC 2011</span>
            </div>
          </div>
        </div>

        {/* 2. BOTTOM-LEFT CARD: Security Audit Protocol */}
        <div
          className="absolute bottom-[8%] left-[2%] xl:left-[5%] w-[310px] xl:w-[340px] animate-float-3d-lb"
          style={{ transformStyle: 'preserve-3d' }}
        >
          <div className="bg-slate-900/60 backdrop-blur-md border border-emerald-400/20 rounded-2xl shadow-2xl p-5">
            {/* Header */}
            <div className="flex items-center justify-between pb-2.5 border-b border-emerald-500/20 mb-3">
              <div className="flex items-center space-x-2">
                <div className="p-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400">
                  <ShieldCheck className="h-4 w-4" />
                </div>
                <div>
                  <h5 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
                    Security Audit Protocol
                  </h5>
                  <p className="text-[9px] text-slate-400 font-mono">INTEGRITY VERIFICATION</p>
                </div>
              </div>
              <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-500/30 px-2 py-0.5 rounded-full font-bold">
                GENUINE
              </span>
            </div>

            {/* Authenticity Big Stat */}
            <div className="flex items-baseline justify-between mb-3 bg-slate-950/50 p-2.5 rounded-xl border border-emerald-500/15">
              <div>
                <span className="text-[10px] text-slate-400 font-mono block">AUDITED SCORE</span>
                <span className="text-base font-black text-emerald-400 font-mono tracking-tight">
                  AUTHENTICITY: 99.8%
                </span>
              </div>
              <span className="text-[10px] text-emerald-400 font-mono">0 Flags</span>
            </div>

            {/* Animated Vertical Emerald Telemetry Bars */}
            <div>
              <div className="flex items-center justify-between text-[9px] font-mono text-slate-400 mb-1.5">
                <span>SPECTRAL FREQUENCY TELEMETRY</span>
                <span className="text-emerald-400">ACTIVE</span>
              </div>
              <div className="h-9 w-full flex items-end justify-between gap-1 px-1 py-1 bg-slate-950/80 rounded-lg border border-slate-800">
                <div className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-xs transition-all duration-300" style={{ height: '45%', animation: 'barPulse1 2.2s ease-in-out infinite' }} />
                <div className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-xs transition-all duration-300" style={{ height: '80%', animation: 'barPulse2 2.6s ease-in-out infinite 0.2s' }} />
                <div className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-xs transition-all duration-300" style={{ height: '60%', animation: 'barPulse3 2.1s ease-in-out infinite 0.4s' }} />
                <div className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-xs transition-all duration-300" style={{ height: '95%', animation: 'barPulse1 2.8s ease-in-out infinite 0.1s' }} />
                <div className="w-full bg-gradient-to-t from-teal-500 to-cyan-400 rounded-xs transition-all duration-300" style={{ height: '70%', animation: 'barPulse2 2.4s ease-in-out infinite 0.3s' }} />
                <div className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-xs transition-all duration-300" style={{ height: '90%', animation: 'barPulse3 2.7s ease-in-out infinite 0.5s' }} />
                <div className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-xs transition-all duration-300" style={{ height: '50%', animation: 'barPulse1 2.3s ease-in-out infinite 0.2s' }} />
                <div className="w-full bg-gradient-to-t from-teal-500 to-cyan-400 rounded-xs transition-all duration-300" style={{ height: '85%', animation: 'barPulse2 2.9s ease-in-out infinite 0.6s' }} />
                <div className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-xs transition-all duration-300" style={{ height: '65%', animation: 'barPulse3 2.5s ease-in-out infinite 0.1s' }} />
                <div className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-xs transition-all duration-300" style={{ height: '92%', animation: 'barPulse1 2.1s ease-in-out infinite 0.4s' }} />
              </div>
            </div>
          </div>
        </div>

        {/* --- RIGHT SIDE CARDS (rotateY(-16deg)) --- */}

        {/* 3. TOP-RIGHT CARD: VERIFIED NUTRITIONAL BREAKDOWN */}
        <div
          className="absolute top-[8%] right-[2%] xl:right-[5%] w-[310px] xl:w-[340px] animate-float-3d-rt"
          style={{ transformStyle: 'preserve-3d' }}
        >
          <div className="bg-slate-900/60 backdrop-blur-md border border-emerald-400/20 rounded-2xl shadow-2xl p-5">
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-cyan-500/20 mb-3.5">
              <div className="flex items-center space-x-2">
                <Activity className="h-4 w-4 text-cyan-400" />
                <span className="text-xs font-black tracking-wider uppercase text-cyan-300">
                  VERIFIED NUTRITIONAL BREAKDOWN
                </span>
              </div>
              <span className="text-[9px] font-mono text-cyan-400 bg-cyan-950/70 border border-cyan-500/30 px-1.5 py-0.5 rounded">
                LAB-GRADE
              </span>
            </div>

            {/* 3 Abstract Circular Macro Rings */}
            <div className="grid grid-cols-3 gap-2 text-center py-1 mb-3.5 bg-slate-950/40 rounded-xl border border-slate-800/80 p-2">
              {/* Ring 1 */}
              <div className="flex flex-col items-center">
                <div className="relative w-12 h-12 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="14" fill="none" stroke="#1e293b" strokeWidth="3" />
                    <circle
                      cx="18"
                      cy="18"
                      r="14"
                      fill="none"
                      stroke="#10b981"
                      strokeWidth="3"
                      strokeDasharray="88, 100"
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className="absolute text-[10px] font-black text-emerald-400 font-mono">88%</span>
                </div>
                <span className="text-[8px] font-medium text-slate-400 mt-1 uppercase tracking-tight">Macro Bal</span>
              </div>

              {/* Ring 2 */}
              <div className="flex flex-col items-center">
                <div className="relative w-12 h-12 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="14" fill="none" stroke="#1e293b" strokeWidth="3" />
                    <circle
                      cx="18"
                      cy="18"
                      r="14"
                      fill="none"
                      stroke="#06b6d4"
                      strokeWidth="3"
                      strokeDasharray="94, 100"
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className="absolute text-[10px] font-black text-cyan-400 font-mono">94%</span>
                </div>
                <span className="text-[8px] font-medium text-slate-400 mt-1 uppercase tracking-tight">Density</span>
              </div>

              {/* Ring 3 */}
              <div className="flex flex-col items-center">
                <div className="relative w-12 h-12 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="14" fill="none" stroke="#1e293b" strokeWidth="3" />
                    <circle
                      cx="18"
                      cy="18"
                      r="14"
                      fill="none"
                      stroke="#14b8a6"
                      strokeWidth="3"
                      strokeDasharray="76, 100"
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className="absolute text-[10px] font-black text-teal-400 font-mono">76%</span>
                </div>
                <span className="text-[8px] font-medium text-slate-400 mt-1 uppercase tracking-tight">Spectrum</span>
              </div>
            </div>

            {/* Clean Multi-Color Horizontal Bar Charts (No product or food names) */}
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-[9px] font-medium text-slate-400 mb-0.5">
                  <span>Essential Nutrient Index</span>
                  <span className="text-emerald-400 font-mono">92%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full w-[92%]" />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-[9px] font-medium text-slate-400 mb-0.5">
                  <span>Transparency Ratio</span>
                  <span className="text-cyan-400 font-mono">100%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-teal-400 to-cyan-400 rounded-full w-[100%]" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 4. BOTTOM-RIGHT CARD: Ingredients: Pure & Approved */}
        <div
          className="absolute bottom-[8%] right-[2%] xl:right-[5%] w-[310px] xl:w-[340px] animate-float-3d-rb"
          style={{ transformStyle: 'preserve-3d' }}
        >
          <div className="bg-slate-900/60 backdrop-blur-md border border-emerald-400/20 rounded-2xl shadow-2xl p-5">
            {/* Header */}
            <div className="flex items-center justify-between pb-2.5 border-b border-emerald-500/20 mb-3">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <h5 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
                  Ingredients: Pure &amp; Approved
                </h5>
              </div>
              <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-500/30 px-1.5 py-0.5 rounded">
                VERIFIED
              </span>
            </div>

            {/* Clean Abstract Ingredient Verification Lines */}
            <div className="space-y-2 mb-3.5">
              <div className="flex items-center justify-between text-[10px] bg-slate-950/50 px-2.5 py-1.5 rounded-lg border border-slate-800">
                <span className="text-slate-300">Synthetic Additives</span>
                <span className="text-[9px] font-mono font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-500/30 px-1.5 py-0.2 rounded">
                  0.0% DETECTED
                </span>
              </div>
              <div className="flex items-center justify-between text-[10px] bg-slate-950/50 px-2.5 py-1.5 rounded-lg border border-slate-800">
                <span className="text-slate-300">Preservative Limit</span>
                <span className="text-[9px] font-mono font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-500/30 px-1.5 py-0.2 rounded">
                  PASSED SPEC
                </span>
              </div>
              <div className="flex items-center justify-between text-[10px] bg-slate-950/50 px-2.5 py-1.5 rounded-lg border border-slate-800">
                <span className="text-slate-300">Declaration Compliance</span>
                <span className="text-[9px] font-mono font-bold text-cyan-400 bg-cyan-950/80 border border-cyan-500/30 px-1.5 py-0.2 rounded">
                  100% DISCLOSED
                </span>
              </div>
            </div>

            {/* Cyan-to-Emerald Pill Badge: Quality Score: 98% */}
            <div className="w-full bg-gradient-to-r from-cyan-500/20 to-emerald-500/20 border border-emerald-400/40 text-emerald-300 font-bold px-3 py-2 rounded-full text-xs flex items-center justify-between shadow-sm">
              <div className="flex items-center space-x-1.5">
                <Sparkles className="h-3.5 w-3.5 text-cyan-300" />
                <span>Statutory Safety Standard</span>
              </div>
              <span className="text-xs font-black font-mono text-emerald-300 bg-emerald-950/90 border border-emerald-400/50 px-2 py-0.5 rounded-full">
                Quality Score: 98%
              </span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
