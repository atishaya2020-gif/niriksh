import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Network } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import Button from '../components/ui/Button';

export const DisruptionPage = () => {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <div className="border-b border-purple-900/30 pb-4"><h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">NETWORK DISRUPTION SIMULATOR</h1><p className="text-xs text-purple-300/70 font-mono-id mt-1">This feature requires a dedicated backend simulation endpoint.</p></div>
      <GlassCard hoverEffect={false} className="p-8 text-center space-y-4"><Network className="w-12 h-12 text-cyan-400 mx-auto" /><h2 className="text-lg font-bold text-white">Simulation Not Available</h2><p className="text-xs text-purple-300/70 font-mono-id max-w-lg mx-auto">No backend endpoint currently provides disruption calculations. No entity selection, graph mutation, or analytical result has been simulated.</p><Button variant="secondary" onClick={() => navigate('/network')}>Return to Network</Button></GlassCard>
    </div>
  );
};

export default DisruptionPage;
