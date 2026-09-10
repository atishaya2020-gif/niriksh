import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Network, ArrowLeft, AlertTriangle } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import entityService from '../services/entityService';

export const EntityDetailsPage = () => {
  const { entityId } = useParams();
  const [entity, setEntity] = useState(null);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const loadEntity = async () => {
    setLoading(true);
    setError(null);
    try {
      const decoded = decodeURIComponent(entityId);
      const [entityData, connectionData] = await Promise.all([
        entityService.getEntity(decoded),
        entityService.getConnections(decoded)
      ]);
      setEntity(entityData);
      setConnections(connectionData);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadEntity(); }, [entityId]);

  if (loading) return <LoadingState message="Resolving entity dossier footprint..." />;
  if (error) return <ErrorState message={error.message} onRetry={loadEntity} />;
  if (!entity) return <EmptyState title="Entity unavailable" message="The requested backend entity could not be found." />;

  const profile = entity._raw || {};
  const risk = profile.risk || {};
  const cases = profile.cases?.items || [];
  const timeline = profile.timeline?.items || [];
  const alerts = profile.alerts?.items || [];

  return (
    <div className="space-y-6">
      <GlassCard hoverEffect={false} glow glowColor="purple" className="space-y-4">
        <button onClick={() => navigate('/entities')} className="inline-flex items-center gap-1.5 text-xs font-mono-id text-purple-400 hover:text-purple-200"><ArrowLeft className="w-3.5 h-3.5" />Back to Entity Registry</button>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-purple-900/40 pb-4"><div><div className="flex items-center gap-3 flex-wrap"><h1 className="text-2xl sm:text-3xl font-extrabold text-white font-mono-id">{entity.name}</h1><span className="text-xs font-mono-id px-2.5 py-1 rounded-md bg-purple-900/60 text-cyan-300 border border-purple-500/30">{entity.type}</span><Badge risk={entity.risk} /></div><p className="text-xs text-purple-300/70 font-mono-id mt-1">Risk score: {risk.score ?? 'Unavailable'} · Confidence: {risk.confidence != null ? `${Math.round(risk.confidence * 100)}%` : 'Unavailable'}</p></div><Button variant="cyan" size="sm" icon={Network} onClick={() => navigate('/network')}>Open Network</Button></div>
        <p className="text-xs text-purple-300/80 font-mono-id">{profile.investigative_note || 'Requires human verification.'}</p>
      </GlassCard>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard hoverEffect={false}><h3 className="text-sm font-bold font-mono-id uppercase tracking-wider text-purple-100 pb-2 border-b border-purple-900/40">Detected Connections ({connections.length})</h3>{connections.length === 0 ? <EmptyState title="No connections" message="The backend returned no connections for this entity." /> : <div className="space-y-3 mt-4">{connections.map((connection) => <button key={connection.id} onClick={() => navigate(`/entities/${encodeURIComponent(connection.target)}`)} className="w-full text-left p-3.5 bg-slate-950/60 border border-purple-900/40 hover:border-purple-500/40 rounded-xl flex items-center justify-between font-mono-id text-xs"><div><span className="text-cyan-400 font-bold">{connection.type}</span><span className="ml-3 text-purple-200">{connection._raw?.label || connection.target}</span><p className="text-purple-400/60 text-[10px] mt-0.5">{connection.why_detected}</p></div><span className="text-emerald-400 font-bold">{Math.round(connection.confidence * 100)}%</span></button>)}</div>}</GlassCard>
        <GlassCard hoverEffect={false}><h3 className="text-sm font-bold font-mono-id uppercase tracking-wider text-purple-100 pb-2 border-b border-purple-900/40">Associated Cases</h3>{cases.length === 0 ? <EmptyState title="No associated cases" message="No case associations were returned." /> : <div className="space-y-3 mt-4">{cases.map((caseData) => <button key={caseData.id} onClick={() => navigate(`/cases/${caseData.id}`)} className="w-full text-left p-3 bg-slate-950/60 border border-purple-900/40 rounded-xl"><span className="text-cyan-400 font-bold text-xs">{caseData.case_number}</span><p className="text-purple-100 text-sm">{caseData.title}</p></button>)}</div>}</GlassCard>
      </div>
      <GlassCard hoverEffect={false}><h3 className="text-sm font-bold font-mono-id uppercase tracking-wider text-purple-100 pb-2 border-b border-purple-900/40">Entity Timeline</h3>{timeline.length === 0 ? <EmptyState title="No timeline events" message="The backend returned no entity timeline events." /> : <div className="space-y-2 mt-4">{timeline.map((event, index) => <div key={index} className="p-3 bg-slate-950/60 border border-purple-900/40 rounded-xl text-xs font-mono-id"><span className="text-cyan-400">{event.incident_datetime ? new Date(event.incident_datetime).toLocaleString() : 'Unknown time'}</span><span className="ml-2 text-purple-100">{event.category} · {event.record_id}</span></div>)}</div>}</GlassCard>
      <div className="p-4 bg-purple-950/40 rounded-2xl border border-purple-500/30 text-xs font-mono-id text-purple-300/80 flex items-start gap-3"><AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" /><div><p className="font-bold text-amber-300 uppercase">Investigative Lead Disclaimer</p><p className="mt-0.5">Entity associations and risk indicators are analytical signals only. They require human verification and do not establish identity, guilt, or criminal responsibility.</p></div></div>
    </div>
  );
};

export default EntityDetailsPage;
