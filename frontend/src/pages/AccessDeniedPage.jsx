import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import authService from '../services/authService';
import Button from '../components/ui/Button';

export const AccessDeniedPage = () => {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-6">
      <div className="max-w-md w-full glass-panel border border-red-500/40 p-8 rounded-3xl text-center space-y-6 shadow-2xl shadow-red-950/50 relative overflow-hidden">
        <div className="p-4 bg-red-950/80 rounded-2xl border border-red-500/40 text-red-400 inline-block">
          <ShieldAlert className="w-10 h-10" />
        </div>

        <div>
          <h2 className="text-2xl font-extrabold text-white font-mono-id tracking-wider">
            ACCESS RESTRICTED
          </h2>
          <p className="text-xs text-purple-300/80 mt-2 font-mono-id">
            You do not have the required authorization to access this security resource.
          </p>
        </div>

        <div className="p-4 bg-slate-950/80 rounded-xl border border-purple-900/30 text-xs font-mono-id text-left space-y-2">
          <div className="flex justify-between">
            <span className="text-purple-400">Current Role:</span>
            <span className="font-bold text-yellow-400">{user?.role || 'ANALYST'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-purple-400">Officer ID:</span>
            <span className="text-purple-200">{user?.employee_id || 'EMP001'}</span>
          </div>
          <div className="flex justify-between border-t border-purple-900/40 pt-2">
            <span className="text-purple-400">Required Permission:</span>
            <span className="font-bold text-red-400">ADMIN_AUTHORIZATION</span>
          </div>
        </div>

        <Button
          onClick={() => navigate('/dashboard')}
          variant="primary"
          icon={ArrowLeft}
          className="w-full"
        >
          RETURN TO DASHBOARD
        </Button>
      </div>
    </div>
  );
};

export default AccessDeniedPage;
