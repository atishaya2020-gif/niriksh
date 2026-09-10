import React from 'react';

export const StatusIndicator = ({ status = 'ACTIVE', label }) => {
  const getDotStyle = () => {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
      case 'ONLINE':
      case 'SUCCESS':
        return 'bg-emerald-400 shadow-emerald-500/80';
      case 'PENDING':
      case 'PROCESSING':
      case 'IN_PROGRESS':
        return 'bg-amber-400 shadow-amber-500/80';
      case 'CRITICAL':
      case 'HIGH':
      case 'FAILED':
      case 'BLOCKED':
        return 'bg-red-400 shadow-red-500/80';
      default:
        return 'bg-slate-400 shadow-slate-500/50';
    }
  };

  return (
    <div className="inline-flex items-center gap-2 font-mono-id text-xs text-purple-200">
      <span className="relative flex h-2.5 w-2.5">
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${getDotStyle()}`} />
        <span className={`relative inline-flex rounded-full h-2.5 w-2.5 shadow-sm ${getDotStyle()}`} />
      </span>
      {label || status}
    </div>
  );
};

export default StatusIndicator;
