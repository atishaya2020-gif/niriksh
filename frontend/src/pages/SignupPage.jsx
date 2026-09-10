import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, ArrowLeft } from 'lucide-react';
import transparentLogo from '../assets/niriksh-logo.png';
import Button from '../components/ui/Button';

export const SignupPage = () => (
  <div className="min-h-screen bg-[#05040A] text-purple-100 flex items-center justify-center p-4 sm:p-6 cyber-grid relative overflow-hidden">
    <div className="w-full max-w-xl glass-panel border border-purple-500/30 p-6 sm:p-10 rounded-3xl shadow-2xl shadow-purple-950/80 relative z-10 space-y-6 text-center">
      <img src={transparentLogo} alt="NIRIKSH Logo" className="w-16 h-16 object-contain mx-auto" />
      <h1 className="text-2xl font-extrabold text-white font-mono-id">ACCESS REQUEST UNAVAILABLE</h1>
      <p className="text-xs text-purple-300/70 font-mono-id">The current backend does not provide an access-request or registration API. Contact an administrator for credentials.</p>
      <Link to="/login"><Button variant="secondary" icon={ArrowLeft}>Back to Sign In</Button></Link>
      <div className="p-3 bg-slate-950/60 rounded-xl border border-purple-900/30 text-[10px] font-mono-id text-purple-400/60 flex items-center gap-2 text-left"><ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" /><span>No access request has been submitted.</span></div>
    </div>
  </div>
);

export default SignupPage;
