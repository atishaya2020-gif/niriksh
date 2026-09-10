import React, { useState } from 'react';
import { Settings, Shield, Bell, Monitor, KeyRound } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import Button from '../components/ui/Button';
import Toast from '../components/ui/Toast';

export const SettingsPage = () => {
  const [toast, setToast] = useState('');

  return (
    <div className="max-w-4xl space-y-6">
      <div className="border-b border-purple-900/30 pb-4">
        <h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">
          PLATFORM PREFERENCES & SETTINGS
        </h1>
        <p className="text-xs text-purple-300/70 font-mono-id mt-1">
          Configure intelligence command center display, notification thresholds, and security rules
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-mono-id text-xs">
        <GlassCard hoverEffect={false} className="space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
            <Monitor className="w-4 h-4" /> Visual Command Interface
          </h3>
          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 bg-slate-950/60 rounded-xl border border-purple-900/30 cursor-pointer">
              <span>Dark Cyber Holographic Atmosphere</span>
              <input type="checkbox" defaultChecked className="rounded text-purple-600 focus:ring-purple-500" />
            </label>
            <label className="flex items-center justify-between p-3 bg-slate-950/60 rounded-xl border border-purple-900/30 cursor-pointer">
              <span>Cytoscape Glowing Outlines</span>
              <input type="checkbox" defaultChecked className="rounded text-purple-600 focus:ring-purple-500" />
            </label>
          </div>
        </GlassCard>

        <GlassCard hoverEffect={false} className="space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
            <Bell className="w-4 h-4" /> Alert Thresholds
          </h3>
          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 bg-slate-950/60 rounded-xl border border-purple-900/30 cursor-pointer">
              <span>Notify on High-Risk Cross-Case Matches</span>
              <input type="checkbox" defaultChecked className="rounded text-purple-600 focus:ring-purple-500" />
            </label>
            <label className="flex items-center justify-between p-3 bg-slate-950/60 rounded-xl border border-purple-900/30 cursor-pointer">
              <span>Notify on High Velocity Wire Transfers</span>
              <input type="checkbox" defaultChecked className="rounded text-purple-600 focus:ring-purple-500" />
            </label>
          </div>
        </GlassCard>
      </div>

      <Button variant="cyan" onClick={() => setToast('Platform settings saved successfully.')}>
        Save Settings
      </Button>

      {toast && <Toast type="success" message={toast} onClose={() => setToast('')} />}
    </div>
  );
};

export default SettingsPage;
