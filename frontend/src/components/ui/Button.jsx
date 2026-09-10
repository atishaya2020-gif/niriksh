import React from 'react';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  className = '',
  disabled = false,
  onClick,
  ...props
}) => {
  const variantStyles = {
    primary:
      'bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-lg shadow-purple-900/40 hover:shadow-purple-600/50 border border-purple-400/30',
    secondary:
      'bg-slate-900/80 hover:bg-purple-950/60 text-purple-200 border border-purple-500/30 hover:border-purple-400/60 shadow-md',
    cyan:
      'bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white shadow-lg shadow-cyan-900/40 hover:shadow-cyan-500/50 border border-cyan-400/30',
    danger:
      'bg-gradient-to-r from-red-600 to-rose-700 hover:from-red-500 hover:to-rose-600 text-white shadow-lg shadow-red-900/40 border border-red-400/30',
    outline:
      'bg-transparent border border-purple-500/40 hover:border-purple-400 text-purple-200 hover:bg-purple-900/20'
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs rounded-md',
    md: 'px-4 py-2 text-sm rounded-lg',
    lg: 'px-6 py-3 text-base rounded-xl font-semibold'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center justify-center gap-2 transition-all duration-200 font-medium active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {Icon && <Icon className="w-4 h-4" />}
      {children}
    </button>
  );
};

export default Button;
