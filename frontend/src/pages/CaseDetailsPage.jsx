import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Network, Upload, Radio, Sparkles } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import Tabs from '../components/ui/Tabs';
import Timeline from '../components/ui/Timeline';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import caseService from '../services/caseService';

export const CaseDetailsPage = () => {
  const { caseId } = useParams();
  const [caseData, setCaseData] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overview, timelineResponse] = await Promise.all([
        caseService.getCase(caseId),
        caseService.getTimeline(caseId)
      ]);
      setCaseData(overview);
      setTimeline(timelineResponse.items || []);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [caseId]);

  if (loading) return <LoadingState message="Fetching investigation file dossier..." />;
  if (error) return <ErrorState message={error.message} onRetry={loadData} />;
  if (!caseData) return <EmptyState title="Case unavailable" message="The requested backend case could not be found." />;

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'entities', label: `Entities (${caseData.entities_count})` },
    { id: 'network', label: 'Network' },
    { id: 'evidence', label: 'Evidence' },
    { id: 'alerts', label: `Alerts (${caseData.alerts_count})` },
    { id: 'timeline', label: 'Timeline' },
    { id: 'notes', label: 'Notes' },
    { id: 'reports', label: 'Reports' }
  ];

  const timelineEvents = timeline.map((event) => ({
    time: event.timestamp ? new Date(event.timestamp).toLocaleString() : 'Unknown time',
    title: event.event_type,
    description: event.description,
    badge: event.source || event.event_type
  }));

  return (
    <div className="space-y-6">
      <GlassCard hoverEffect={false} glow glowColor="purple" className="space-y-4">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 border-b border-purple-900/40 pb-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-xl font-extrabold font-mono-id text-cyan-300">{caseData.case_number}</span>
              <h1 className="text-2xl font-extrabold text-white">{caseData.title}</h1>
              {caseData.risk && <Badge risk={caseData.risk} />}
              {caseData.status && <Badge status={caseData.status} />}
            </div>
            <p className="text-xs text-purple-300/80 font-mono-id">{caseData.description || 'No description provided.'}</p>
          </div>
          <div className="flex items-center gap-2.5 flex-wrap">
            <Button variant="cyan" size="sm" icon={Network} onClick={() => navigate(`/network?caseId=${caseData.id}`)}>Open Network</Button>
            <Button variant="primary" size="sm" icon={Upload} onClick={() => navigate(`/data-intake?caseId=${caseData.id}`)}>Upload CSV</Button>
            <Button variant="secondary" size="sm" icon={Radio} onClick={() => navigate('/alerts')}>Review Alerts</Button>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono-id">
          <div><span className="text-purple-400/60 block uppercase text-[10px]">Database Case ID</span><span className="text-cyan-300 font-bold">{caseData.id}</span></div>
          <div><span className="text-purple-400/60 block uppercase text-[10px]">Entities</span><span className="text-purple-100 font-bold">{caseData.entities_count}</span></div>
          <div><span className="text-purple-400/60 block uppercase text-[10px]">Relationships</span><span className="text-purple-100 font-bold">{caseData.relationships_count}</span></div>
          <div><span className="text-purple-400/60 block uppercase text-[10px]">Last Updated</span><span className="text-purple-200">{caseData.last_updated}</span></div>
        </div>
      </GlassCard>

      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <GlassCard hoverEffect={false} className="lg:col-span-2">
            <h3 className="text-xs font-bold font-mono-id uppercase tracking-wider text-purple-300/80 mb-3">Key Entities</h3>
            {caseData.key_entities.length === 0 ? <EmptyState title="No key entities" message="The backend returned no key entities for this case." /> : (
              <div className="space-y-2.5">
                {caseData.key_entities.map((entity) => (
                  <button key={entity.entity_id} onClick={() => navigate(`/entities/${encodeURIComponent(entity.entity_id)}`)} className="w-full text-left p-3 bg-slate-950/60 border border-purple-900/40 hover:border-purple-500/40 rounded-xl flex items-start gap-3">
                    <Sparkles className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <span className="text-xs text-purple-200 font-mono-id">{entity.label} · {entity.entity_type} · {entity.connections} connections</span>
                  </button>
                ))}
              </div>
            )}
          </GlassCard>
          <GlassCard hoverEffect={false} className="space-y-4">
            <h3 className="text-xs font-bold font-mono-id uppercase tracking-wider text-purple-300/80">Case Intelligence Summary</h3>
            <div className="space-y-2 text-xs font-mono-id">
              <div className="flex justify-between py-1 border-b border-purple-900/30"><span className="text-purple-400">Entities:</span><span className="font-bold text-purple-100">{caseData.entities_count}</span></div>
              <div className="flex justify-between py-1 border-b border-purple-900/30"><span className="text-purple-400">Relationships:</span><span className="font-bold text-cyan-400">{caseData.relationships_count}</span></div>
              <div className="flex justify-between py-1"><span className="text-purple-400">Active Alerts:</span><span className="font-bold text-red-400">{caseData.alerts_count}</span></div>
            </div>
          </GlassCard>
        </div>
      )}

      {activeTab === 'entities' && (
        <div className="space-y-3">
          {caseData.key_entities.length === 0 ? <EmptyState title="No entities available" message="The backend returned no key entities for this case." /> : caseData.key_entities.map((entity) => (
            <button key={entity.entity_id} onClick={() => navigate(`/entities/${encodeURIComponent(entity.entity_id)}`)} className="w-full text-left p-4 bg-slate-950/60 border border-purple-900/40 hover:border-purple-500/50 rounded-xl flex items-center justify-between">
              <div><span className="text-sm font-bold text-purple-100">{entity.label}</span><span className="ml-2 text-xs font-mono-id text-cyan-400">({entity.entity_type})</span><p className="text-xs text-purple-300/60 font-mono-id mt-0.5">Connections: {entity.connections}</p></div>
            </button>
          ))}
        </div>
      )}

      {activeTab === 'network' && <GlassCard hoverEffect={false} className="p-8 text-center space-y-4"><Network className="w-12 h-12 text-cyan-400 mx-auto" /><h3 className="text-lg font-bold text-white font-mono-id">Network Analysis Ready</h3><p className="text-xs text-purple-300/70 font-mono-id max-w-md mx-auto">Explore {caseData.relationships_count} backend relationships and {caseData.entities_count} backend entities.</p><Button variant="cyan" icon={Network} onClick={() => navigate(`/network?caseId=${caseData.id}`)}>Launch Cytoscape Network Workspace</Button></GlassCard>}

      {activeTab === 'timeline' && <GlassCard hoverEffect={false}>{timelineEvents.length === 0 ? <EmptyState title="No persisted timeline events" message="The backend returned no timeline events for this case." /> : <Timeline events={timelineEvents} />}</GlassCard>}

      {activeTab === 'alerts' && <div className="space-y-3">{caseData.alerts.length === 0 ? <EmptyState title="No active alerts" message="The backend returned no active alerts for this case." /> : caseData.alerts.map((alert) => <div key={alert.id} className="p-4 bg-slate-950/60 border border-purple-900/40 rounded-xl flex items-center justify-between"><div><span className="text-xs font-mono-id font-bold text-red-400">{alert.alert_type}</span><h4 className="text-sm font-semibold text-purple-100">{alert.entity_id}</h4><p className="text-xs text-purple-300/60 font-mono-id">{alert.reason}</p></div><Badge risk={alert.risk_level} /></div>)}</div>}

      {activeTab === 'evidence' && <GlassCard hoverEffect={false} className="p-6 text-center text-xs font-mono-id text-purple-300/70 space-y-3"><p>Evidence is stored by backend case ID.</p><Button variant="secondary" size="sm" onClick={() => navigate(`/evidence?caseId=${caseData.id}`)}>View Case Evidence</Button></GlassCard>}
      {(activeTab === 'notes' || activeTab === 'reports') && <GlassCard hoverEffect={false} className="p-6 text-center text-xs font-mono-id text-purple-300/70"><p>This feature has no backend endpoint yet.</p></GlassCard>}
    </div>
  );
};

export default CaseDetailsPage;
