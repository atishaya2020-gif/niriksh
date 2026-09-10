import React from 'react';

export const Timeline = ({ events = [] }) => {
  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-gradient-to-b before:from-purple-500 before:via-cyan-500 before:to-purple-900">
      {events.map((evt, idx) => (
        <div key={idx} className="relative group">
          {/* Glowing node marker */}
          <div className="absolute -left-[30px] top-1 w-3 h-3 rounded-full bg-purple-500 border-2 border-slate-950 shadow-md shadow-purple-500/80 group-hover:scale-125 transition-transform" />

          <div className="bg-slate-950/60 border border-purple-900/40 hover:border-purple-500/40 p-4 rounded-xl transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono-id font-bold text-cyan-400">
                {evt.time}
              </span>
              {evt.badge && (
                <span className="text-[10px] font-mono-id px-2 py-0.5 rounded bg-purple-900/60 text-purple-200 border border-purple-500/30">
                  {evt.badge}
                </span>
              )}
            </div>
            <h5 className="text-sm font-semibold text-purple-100 mt-1">
              {evt.title}
            </h5>
            {evt.description && (
              <p className="text-xs text-purple-300/70 mt-1">
                {evt.description}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default Timeline;
