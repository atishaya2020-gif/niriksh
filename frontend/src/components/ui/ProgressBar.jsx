import React from 'react';

export const ProgressBar = ({ progress = 0, label, className = '' }) => {
  const clamped = Math.min(100, Math.max(0, progress));

  return (
    <div className={`w-full space-y-1.5 ${className}`}>
      {label && (
        <div className="flex justify-between text-xs font-mono-id">
          <span className="text-purple-300/80 uppercase">{label}</span>
          <span className="text-cyan-400 font-bold">{clamped}%</span>
        </div>
      )}
      <div className="w-full h-2.5 bg-slate-950 rounded-full border border-purple-900/40 overflow-hidden p-0.5 shadow-inner">
        <div
          className="h-full bg-gradient-to-r from-violet-600 via-purple-500 to-cyan-400 rounded-full transition-all duration-300 shadow-md shadow-purple-500/50"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
