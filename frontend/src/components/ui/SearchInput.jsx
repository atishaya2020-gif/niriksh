import React from 'react';
import { Search, X } from 'lucide-react';

export const SearchInput = ({
  value,
  onChange,
  placeholder = 'Search entities, cases, alerts...',
  className = ''
}) => {
  return (
    <div className={`relative flex items-center w-full ${className}`}>
      <Search className="absolute left-3.5 w-4 h-4 text-purple-400/60 pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-slate-950/80 text-purple-100 placeholder-purple-400/30 border border-purple-500/30 focus:border-purple-400 focus:ring-1 focus:ring-purple-400/50 rounded-xl pl-10 pr-9 py-2 text-sm transition-all outline-none"
      />
      {value && (
        <button
          onClick={() => onChange('')}
          className="absolute right-3 p-0.5 text-purple-400/60 hover:text-purple-200 cursor-pointer"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};

export default SearchInput;
