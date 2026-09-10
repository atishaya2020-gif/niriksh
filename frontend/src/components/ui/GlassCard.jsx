import React from 'react';

export const GlassCard = ({
  children,
  className = '',
  hoverEffect = true,
  glow = false,
  glowColor = 'purple',
  onClick,
  ...props
}) => {
  const baseClasses = hoverEffect ? 'glass-panel-interactive' : 'glass-panel';
  const glowClasses = glow
    ? glowColor === 'cyan'
      ? 'glass-glow-cyan'
      : 'glass-glow-purple'
    : '';

  return (
    <div
      className={`${baseClasses} ${glowClasses} p-5 ${className}`}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

export default GlassCard;
