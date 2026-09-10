import React from 'react';
import { ShieldCheck } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import authService from '../services/authService';

export const ProfilePage = () => {
  const user = authService.getCurrentUser();
  return (
    <div className="max-w-3xl space-y-6">
      <div className="border-b border-purple-900/30 pb-4"><h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">USER PROFILE</h1><p className="text-xs text-purple-300/70 font-mono-id mt-1">Authenticated account details returned by the backend</p></div>
      <GlassCard hoverEffect={false} glow glowColor="purple" className="p-8 space-y-6"><div className="flex items-center gap-6 pb-6 border-b border-purple-900/40"><div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-purple-600 to-cyan-400 flex items-center justify-center font-mono-id text-white font-extrabold text-2xl shadow-xl shadow-purple-900/50">{user?.id ?? '?'}</div><div><h2 className="text-2xl font-bold text-white">{user?.username || 'Unavailable'}</h2><p className="text-xs font-mono-id text-cyan-300 mt-1">{user?.role || 'No role returned'}</p></div></div><div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono-id text-xs"><div className="p-3.5 bg-slate-950/60 rounded-xl border border-purple-900/30"><span className="text-purple-400 block text-[10px] uppercase">User ID</span><span className="text-purple-100 font-bold text-sm">{user?.id ?? 'Unavailable'}</span></div><div className="p-3.5 bg-slate-950/60 rounded-xl border border-purple-900/30"><span className="text-purple-400 block text-[10px] uppercase">Backend Role</span><span className="text-yellow-400 font-bold text-sm">{user?.role || 'Unavailable'}</span></div></div><div className="p-4 bg-purple-950/40 rounded-xl border border-purple-500/30 text-xs font-mono-id text-purple-300/80 flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" /><span>Authentication is validated through the Niriksh backend.</span></div></GlassCard>
    </div>
  );
};

export default ProfilePage;
