import React from 'react';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';

export const Toast = ({ message, type = 'info', onClose }) => {
  const styles = {
    info: 'border-purple-500/50 bg-slate-950/90 text-purple-200',
    success: 'border-emerald-500/50 bg-slate-950/90 text-emerald-300',
    error: 'border-red-500/50 bg-slate-950/90 text-red-300'
  };

  const icons = {
    info: <Info className="w-5 h-5 text-purple-400" />,
    success: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
    error: <AlertCircle className="w-5 h-5 text-red-400" />
  };

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 p-4 rounded-xl border shadow-2xl backdrop-blur-md transition-all ${styles[type]}`}
    >
      {icons[type]}
      <span className="text-sm font-medium pr-2 font-mono-id">{message}</span>
      {onClose && (
        <button onClick={onClose} className="p-1 hover:text-white cursor-pointer">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

export default Toast;
