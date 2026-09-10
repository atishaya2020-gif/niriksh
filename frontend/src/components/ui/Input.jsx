import React from 'react';

export const Input = ({
  label,
  error,
  icon: Icon,
  className = '',
  mono = false,
  ...props
}) => {
  return (
    <div className="w-full space-y-1.5">
      {label && (
        <label className="block text-xs font-semibold uppercase tracking-wider text-purple-300/80">
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        {Icon && (
          <div className="absolute left-3 text-purple-400/60 pointer-events-none">
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          className={`w-full bg-slate-950/70 text-purple-100 placeholder-purple-400/30 border border-purple-500/30 focus:border-purple-400 focus:ring-1 focus:ring-purple-400/50 rounded-lg px-3 py-2 text-sm transition-all outline-none ${
            Icon ? 'pl-9' : ''
          } ${mono ? 'font-mono-id' : ''} ${
            error ? 'border-red-500 focus:ring-red-500' : ''
          } ${className}`}
          {...props}
        />
      </div>
      {error && <p className="text-xs text-red-400 mt-1">{error}</p>}
    </div>
  );
};

export default Input;
