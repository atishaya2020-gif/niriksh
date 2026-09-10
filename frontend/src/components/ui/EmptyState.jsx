import React from 'react';
import { Database } from 'lucide-react';
import Button from './Button';

export const EmptyState = ({
  title = 'No Records Found',
  description = 'No matching investigation data available in current scope.',
  actionLabel,
  onAction,
  icon: Icon = Database
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center glass-panel border-dashed border-purple-800/40 rounded-2xl my-4">
      <div className="p-4 bg-purple-950/60 rounded-2xl border border-purple-500/20 text-purple-400 mb-4">
        <Icon className="w-8 h-8" />
      </div>
      <h4 className="text-base font-semibold text-purple-100">{title}</h4>
      <p className="text-xs text-purple-300/60 max-w-sm mt-1 mb-6 font-mono-id">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
