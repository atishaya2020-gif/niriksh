import React from 'react';

export const Tabs = ({ tabs = [], activeTab, onChange, className = '' }) => {
  return (
    <div className={`flex items-center gap-2 p-1 bg-slate-950/70 border border-purple-900/40 rounded-xl overflow-x-auto ${className}`}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all whitespace-nowrap cursor-pointer ${
              isActive
                ? 'bg-purple-600 text-white shadow-md shadow-purple-900/50 border border-purple-400/40'
                : 'text-purple-300/70 hover:text-purple-100 hover:bg-purple-900/30'
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
};

export default Tabs;
