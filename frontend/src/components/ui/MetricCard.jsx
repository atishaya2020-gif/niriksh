import React from 'react';
import GlassCard from './GlassCard';

export const MetricCard = ({
  title,
  value,
  trend,
  icon: Icon,
  trendPositive = true,
  subtitle,
  glowColor = 'purple'
}) => {
  return (
    <GlassCard hoverEffect glow glowColor={glowColor} className="relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-purple-300/70 font-mono-id">
            {title}
          </p>
          <h4 className="text-3xl font-extrabold text-white mt-2 font-mono-id tracking-tight">
            {value}
          </h4>
        </div>
        {Icon && (
          <div className="p-3 bg-purple-900/40 border border-purple-500/30 rounded-xl text-purple-300 shadow-inner">
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between text-xs">
        {trend && (
          <span
            className={`font-semibold font-mono-id px-2 py-0.5 rounded-md border ${
              trendPositive
                ? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/30'
                : 'bg-red-950/60 text-red-400 border-red-500/30'
            }`}
          >
            {trend}
          </span>
        )}
        {subtitle && (
          <span className="text-purple-400/60 font-mono-id text-[11px]">
            {subtitle}
          </span>
        )}
      </div>
    </GlassCard>
  );
};

export default MetricCard;
