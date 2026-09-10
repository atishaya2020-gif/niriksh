import React from 'react';

export const Table = ({ headers = [], children, className = '' }) => {
  return (
    <div className={`w-full overflow-x-auto rounded-xl border border-purple-500/20 glass-panel ${className}`}>
      <table className="w-full text-left text-sm border-collapse">
        <thead className="bg-purple-950/60 border-b border-purple-800/40 text-xs font-semibold uppercase tracking-wider text-purple-300">
          <tr>
            {headers.map((h, i) => (
              <th key={i} className="px-4 py-3.5">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-purple-900/30 text-purple-200">
          {children}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
