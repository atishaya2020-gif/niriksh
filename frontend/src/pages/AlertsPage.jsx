import React, { useEffect, useState } from 'react';
import { Radio, Sparkles, CheckCircle2, HelpCircle } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import Drawer from '../components/ui/Drawer';
import Select from '../components/ui/Select';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import alertService from '../services/alertService';

export const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [explainDrawerOpen, setExplainDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [severityFilter, setSeverityFilter] = useState('ALL');

  const loadAlerts = async () => {
    setLoading(true);
    setError(null);
    try {
      setAlerts(await alertService.getAlerts({ severity: severityFilter }));
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAlerts(); }, [severityFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-purple-900/30 pb-4"><div><h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight flex items-center gap-2"><Radio className="w-6 h-6 text-red-400" />AI EXPLAINABLE RISK ALERTS</h1><p className="text-xs text-purple-300/70 font-mono-id mt-1">Analytical signals for human review. They do not establish identity, guilt, or criminal responsibility.</p></div><div className="w-48"><Select value={severityFilter} onChange={(event) => setSeverityFilter(event.target.value)} options={[{ value: 'ALL', label: 'All Severities' }, { value: 'CRITICAL', label: 'Critical' }, { value: 'HIGH', label: 'High' }, { value: 'MEDIUM', label: 'Medium' }, { value: 'LOW', label: 'Low' }]} /></div></div>
      {loading && <LoadingState message="Loading backend alerts..." />}
      {!loading && error && <ErrorState message={error.message} onRetry={loadAlerts} />}
      {!loading && !error && alerts.length === 0 && <EmptyState title="No alerts found" message="The backend returned no alerts for the selected filter." />}
      {!loading && !error && alerts.length > 0 && <div className="grid grid-cols-1 md:grid-cols-2 gap-6">{alerts.map((alert) => <GlassCard key={alert.id} hoverEffect glow={alert.severity === 'CRITICAL'} glowColor="purple" className="space-y-4"><div className="flex items-start justify-between border-b border-purple-900/40 pb-3"><div className="space-y-1"><span className="text-xs font-mono-id font-bold text-cyan-400">{alert.id}</span><h3 className="text-sm font-bold text-purple-100">{alert.title}</h3></div><Badge risk={alert.severity} /></div><p className="text-xs text-purple-200 font-mono-id leading-relaxed">{alert.reason}</p><div className="p-3 bg-slate-950/60 rounded-xl border border-purple-900/40 text-xs font-mono-id space-y-1"><div className="flex justify-between text-[11px]"><span className="text-purple-400">Entity:</span><span className="font-bold text-yellow-300">{alert.entity_id}</span></div><div className="flex justify-between text-[11px]"><span className="text-purple-400">Risk Score:</span><span className="font-bold text-cyan-300">{alert.risk_score}</span></div><div className="flex justify-between text-[11px]"><span className="text-purple-400">Confidence:</span><span className="font-bold text-cyan-300">{Math.round(alert.confidence * 100)}%</span></div><div className="flex justify-between text-[11px]"><span className="text-purple-400">Status:</span><span className="font-bold text-purple-100">{alert.status}</span></div></div><div className="flex items-center justify-between pt-2"><span className="text-[10px] font-mono-id text-purple-400/60">{alert.timestamp}</span><Button variant="cyan" size="sm" icon={HelpCircle} onClick={() => { setSelectedAlert(alert); setExplainDrawerOpen(true); }}>WHY WAS THIS FLAGGED?</Button></div></GlassCard>)}</div>}
      {selectedAlert && <Drawer isOpen={explainDrawerOpen} onClose={() => setExplainDrawerOpen(false)} title="WHY WAS THIS FLAGGED?" subtitle={`Alert ${selectedAlert.id}`} width="w-full sm:w-[540px]"><div className="space-y-6 font-mono-id text-xs"><div className="p-4 bg-purple-950/50 rounded-2xl border border-purple-500/40 space-y-2"><div className="flex items-center justify-between"><Badge risk={selectedAlert.severity} /><span className="text-xs font-bold text-emerald-400">{Math.round(selectedAlert.confidence * 100)}% CONFIDENCE</span></div><p className="text-sm font-bold text-purple-100">{selectedAlert.title}</p><span className="inline-block text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/30">REQUIRES HUMAN VERIFICATION</span></div><div className="space-y-3"><h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5"><Sparkles className="w-4 h-4" />Backend Explanation</h4><div className="p-3 bg-slate-950/80 rounded-xl border border-purple-900/40 flex items-start gap-2.5 text-purple-200"><CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" /><span>{selectedAlert.reason || 'No explanation was returned.'}</span></div></div><div className="p-3 bg-slate-950 rounded-xl border border-purple-900/30 text-[10px] text-purple-400/60">ANALYTICAL OUTPUT · REQUIRES HUMAN VERIFICATION</div></div></Drawer>}
    </div>
  );
};

export default AlertsPage;
