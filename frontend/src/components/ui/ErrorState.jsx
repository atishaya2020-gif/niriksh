import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import Button from './Button';

export const ErrorState = ({
  title = 'System Error Detected',
  message = 'An unexpected service response was returned. Please retry.',
  onRetry
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center glass-panel border border-red-500/30 rounded-2xl my-4">
      <div className="p-3 bg-red-950/80 rounded-xl border border-red-500/40 text-red-400 mb-3">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h4 className="text-sm font-semibold text-red-200 font-mono-id">{title}</h4>
      <p className="text-xs text-purple-300/70 max-w-md mt-1 mb-4 font-mono-id">
        {message}
      </p>
      {onRetry && (
        <Button onClick={onRetry} variant="secondary" size="sm" icon={RefreshCw}>
          Retry Connection
        </Button>
      )}
    </div>
  );
};

export default ErrorState;
