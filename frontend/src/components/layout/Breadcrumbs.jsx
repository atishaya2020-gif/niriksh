import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  if (location.pathname === '/' || location.pathname === '/login' || location.pathname === '/signup') {
    return null;
  }

  return (
    <nav className="flex items-center space-x-2 text-xs font-mono-id text-purple-400/60">
      <Link to="/dashboard" className="hover:text-purple-200 transition-colors flex items-center gap-1">
        <Home className="w-3.5 h-3.5" />
        <span>COMMAND</span>
      </Link>
      {pathnames.map((value, index) => {
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;
        const decodedValue = decodeURIComponent(value);

        return (
          <React.Fragment key={to}>
            <ChevronRight className="w-3 h-3 text-purple-600" />
            {isLast ? (
              <span className="text-purple-200 font-bold uppercase tracking-wide">
                {decodedValue}
              </span>
            ) : (
              <Link to={to} className="hover:text-purple-200 transition-colors uppercase">
                {decodedValue}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

export default Breadcrumbs;
