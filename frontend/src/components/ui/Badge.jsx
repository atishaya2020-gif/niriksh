import React from 'react';

export const Badge = ({
  children,
  variant = 'purple',
  risk,
  status,
  className = '',
  size = 'md'
}) => {
  let badgeStyle = 'bg-purple-900/40 text-purple-200 border-purple-500/30';

  if (risk) {
    switch (risk.toUpperCase()) {
      case 'CRITICAL':
        badgeStyle = 'bg-red-950/80 text-red-400 border-red-500/50 shadow-sm shadow-red-900/50';
        break;
      case 'HIGH':
        badgeStyle = 'bg-orange-950/80 text-orange-400 border-orange-500/50';
        break;
      case 'MEDIUM':
        badgeStyle = 'bg-yellow-950/80 text-yellow-400 border-yellow-500/50';
        break;
      case 'LOW':
        badgeStyle = 'bg-emerald-950/80 text-emerald-400 border-emerald-500/50';
        break;
      default:
        break;
    }
  } else if (status) {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        badgeStyle = 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40';
        break;
      case 'IN_PROGRESS':
        badgeStyle = 'bg-cyan-950/80 text-cyan-300 border-cyan-500/40';
        break;
      case 'ON_HOLD':
      case 'PENDING':
        badgeStyle = 'bg-amber-950/80 text-amber-300 border-amber-500/40';
        break;
      case 'SUSPENDED':
      case 'BLOCKED':
        badgeStyle = 'bg-red-950/80 text-red-400 border-red-500/40';
        break;
      case 'CLOSED':
      case 'RESOLVED':
        badgeStyle = 'bg-slate-900/80 text-slate-400 border-slate-700';
        break;
      default:
        break;
    }
  } else if (variant === 'cyan') {
    badgeStyle = 'bg-cyan-950/70 text-cyan-300 border-cyan-500/30';
  } else if (variant === 'teal') {
    badgeStyle = 'bg-teal-950/70 text-teal-300 border-teal-500/30';
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm'
  };

  return (
    <span
      className={`inline-flex items-center gap-1 font-mono-id tracking-wider font-semibold rounded-md border uppercase ${sizes[size]} ${badgeStyle} ${className}`}
    >
      {risk && <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />}
      {children || risk || status}
    </span>
  );
};

export default Badge;
