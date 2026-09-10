import React from 'react';

export const Select = ({
  label,
  options = [],
  value,
  onChange,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full space-y-1.5">
      {label && (
        <label className="block text-xs font-semibold uppercase tracking-wider text-purple-300/80">
          {label}
        </label>
      )}
      <select
        value={value}
        onChange={onChange}
        className={`w-full bg-slate-950/80 text-purple-100 border border-purple-500/30 focus:border-purple-400 focus:ring-1 focus:ring-purple-400/50 rounded-lg px-3 py-2 text-sm transition-all outline-none cursor-pointer ${className}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} className="bg-slate-900 text-purple-100">
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Select;
