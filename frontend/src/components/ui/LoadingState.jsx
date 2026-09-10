import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingState = ({ message = 'Synchronizing intelligence records...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-4 min-h-[300px]">
      <div className="relative flex items-center justify-center">
        <div className="w-12 h-12 rounded-full border-2 border-purple-500/20 border-t-purple-500 animate-spin" />
        <Loader2 className="w-6 h-6 text-purple-400 absolute animate-pulse" />
      </div>
      <p className="text-sm font-mono-id text-purple-300/70 animate-pulse tracking-wide">
        {message}
      </p>
    </div>
  );
};

export default LoadingState;
