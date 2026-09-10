import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, LogIn, UserPlus, Lock } from 'lucide-react';
import transparentLogo from '../assets/niriksh-logo.png';
import Button from '../components/ui/Button';

export const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen relative bg-[#05040A] text-purple-100 flex flex-col items-center justify-center p-6 overflow-hidden cyber-grid">
      {/* Background Radial Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/15 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-[400px] h-[400px] bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none" />

      {/* Atmospheric Center Hero Glass Box */}
      <div className="relative z-10 max-w-3xl w-full text-center space-y-8 glass-panel border border-purple-500/30 p-8 sm:p-14 rounded-3xl shadow-2xl shadow-purple-950/70 glass-glow-purple">
        {/* Transparent Logo */}
        <div className="flex justify-center">
          <div className="relative group">
            <div className="absolute -inset-4 bg-gradient-to-r from-purple-600 to-cyan-400 rounded-full blur-lg opacity-40 group-hover:opacity-75 transition duration-500" />
            <img
              src={transparentLogo}
              alt="NIRIKSH Logo"
              className="relative w-28 h-28 sm:w-36 sm:h-36 object-contain drop-shadow-[0_0_20px_rgba(139,92,246,0.8)]"
            />
          </div>
        </div>

        {/* Brand Text */}
        <div className="space-y-3">
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-purple-200 to-cyan-300 font-mono-id">
            NIRIKSH
          </h1>
          <h2 className="text-lg sm:text-2xl font-semibold text-purple-200 tracking-wide">
            AI-Powered Criminal Network Analysis System
          </h2>
          <p className="text-xs sm:text-sm font-mono-id text-cyan-400 uppercase tracking-widest font-bold">
            Secure Investigation Intelligence Platform
          </p>
        </div>

        {/* Security Alert Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-950/60 border border-purple-500/30 rounded-full text-xs text-purple-300 font-mono-id">
          <Lock className="w-3.5 h-3.5 text-cyan-400" />
          <span>Restricted access. Authorized personnel only.</span>
        </div>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Button
            size="lg"
            variant="primary"
            icon={LogIn}
            onClick={() => navigate('/login')}
            className="w-full sm:w-48 shadow-lg shadow-purple-600/40"
          >
            SIGN IN
          </Button>
          <Button
            size="lg"
            variant="secondary"
            icon={UserPlus}
            onClick={() => navigate('/signup')}
            className="w-full sm:w-48"
          >
            REQUEST ACCESS
          </Button>
        </div>
      </div>

      {/* Footer Info */}
      <footer className="absolute bottom-6 text-center text-xs font-mono-id text-purple-400/50 space-y-1">
        <p>SMART INDIA HACKATHON 2026 PROTOTYPE • SYNTHETIC DEMONSTRATION PLATFORM</p>
        <p className="text-[10px] text-purple-500/40">
          This system uses simulated data. Production deployment requires backend JWT authentication and identity verification.
        </p>
      </footer>
    </div>
  );
};

export default LandingPage;
