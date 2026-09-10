import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, Lock, User, KeyRound, ArrowLeft, AlertCircle } from 'lucide-react';
import transparentLogo from '../assets/niriksh-logo.png';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import authService from '../services/authService';

export const LoginPage = () => {
  const [credential, setCredential] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const res = await authService.login(credential, password);
    setLoading(false);

    if (res.success) {
      navigate('/dashboard');
    } else {
      setError(res.message);
    }
  };

  return (
    <div className="min-h-screen bg-[#05040A] text-purple-100 flex items-center justify-center p-4 sm:p-6 cyber-grid relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/3 left-1/4 w-[500px] h-[500px] bg-purple-600/15 blur-[120px] rounded-full pointer-events-none" />

      <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-2 gap-8 glass-panel border border-purple-500/30 p-6 sm:p-10 rounded-3xl shadow-2xl shadow-purple-950/80 relative z-10">
        {/* LEFT: Branding Visual */}
        <div className="flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-purple-900/40 pb-6 lg:pb-0 lg:pr-8">
          <div>
            <Link to="/" className="inline-flex items-center gap-2 text-xs font-mono-id text-purple-400/80 hover:text-purple-200 transition-colors mb-6">
              <ArrowLeft className="w-4 h-4" /> BACK TO ENTRY
            </Link>

            <div className="space-y-4">
              <img
                src={transparentLogo}
                alt="NIRIKSH Logo"
                className="w-20 h-20 object-contain drop-shadow-[0_0_15px_rgba(139,92,246,0.7)]"
              />
              <h2 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-purple-300 font-mono-id">
                NIRIKSH
              </h2>
              <p className="text-sm text-purple-300/80 font-mono-id font-medium">
                AI-Powered Criminal Network Analysis System
              </p>
              <p className="text-xs text-purple-400/60 font-mono-id">
                Secure Investigation Intelligence Platform
              </p>
            </div>
          </div>

          <div className="mt-8 p-4 bg-purple-950/40 border border-purple-500/30 rounded-2xl space-y-2">
            <span className="text-[10px] font-mono-id font-bold uppercase tracking-widest text-cyan-400 block">
               DEMO BACKEND CREDENTIALS
            </span>
            <div className="text-xs font-mono-id text-purple-200 space-y-1">
               <p><span className="text-purple-400">Username:</span> admin</p>
              <p><span className="text-purple-400">Password:</span> admin123</p>
            </div>
          </div>
        </div>

        {/* RIGHT: Glass Authentication Form */}
        <div className="flex flex-col justify-center space-y-6">
          <div>
            <h3 className="text-2xl font-extrabold text-purple-100">Welcome back</h3>
            <p className="text-xs text-purple-300/70 font-mono-id mt-1">
              Sign in with your authorized official credentials
            </p>
          </div>

          {error && (
            <div className="p-3 bg-red-950/80 border border-red-500/50 rounded-xl text-xs text-red-300 flex items-start gap-2 font-mono-id">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <Input
               label="Username"
               placeholder="e.g. admin"
              value={credential}
              onChange={(e) => setCredential(e.target.value)}
              icon={User}
              mono
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              icon={KeyRound}
              mono
              required
            />

            <Button
              type="submit"
              size="lg"
              variant="primary"
              disabled={loading}
              className="w-full mt-2 shadow-lg shadow-purple-600/40"
            >
              {loading ? 'AUTHENTICATING...' : 'SIGN IN'}
            </Button>
          </form>

          <div className="pt-4 border-t border-purple-900/40 flex items-center justify-between text-xs font-mono-id">
            <span className="text-purple-400/60">New Officer?</span>
            <Link to="/signup" className="text-cyan-400 hover:underline font-bold">
              REQUEST ACCESS →
            </Link>
          </div>

          <div className="p-3 bg-slate-950/60 rounded-xl border border-purple-900/30 text-[10px] font-mono-id text-purple-400/60 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>AUTHORIZED PERSONNEL ONLY • All authentication attempts are logged for audit controls.</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
