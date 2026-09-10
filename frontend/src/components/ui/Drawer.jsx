import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export const Drawer = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  width = 'w-96 sm:w-[480px]',
  className = ''
}) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end overflow-hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Drawer Panel */}
      <div
        className={`relative z-10 h-full ${width} glass-panel border-l border-purple-500/40 shadow-2xl shadow-purple-950/80 p-6 flex flex-col transition-all duration-300 transform translate-x-0 ${className}`}
      >
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-purple-900/40 mb-4">
          <div>
            {title && (
              <h3 className="text-lg font-bold text-purple-100 tracking-wide">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-xs text-purple-300/70 font-mono-id mt-0.5">
                {subtitle}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-purple-400 hover:text-purple-100 hover:bg-purple-900/40 rounded-lg transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto pr-1">{children}</div>
      </div>
    </div>
  );
};

export default Drawer;
