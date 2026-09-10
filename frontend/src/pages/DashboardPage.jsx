import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FolderKanban, Users, Network, Radio, AlertTriangle, Upload, ArrowUpRight } from 'lucide-react';
import MetricCard from '../components/ui/MetricCard';
import GlassCard from '../components/ui/GlassCard';
import Button from '../components/ui/Button';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import dashboardService from '../services/dashboardService';

export const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, caseData] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getRecentInvestigations()
      ]);
      setStats(statsData);
      setCases(caseData);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDashboard(); }, []);

  if (loading) return <LoadingState message="Loading Command Center Intelligence..." />;
  if (error) return <ErrorState message={error.message} onRetry={loadDashboard} />;
  if (!stats) return <EmptyState title="Dashboard unavailable" message="No dashboard metrics were returned by the backend." />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-purple-900/30 pb-4">
        <div><h1 className="text-2xl sm:text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-purple-100 to-cyan-300 font-mono-id tracking-tight">Investigation Command Center</h1><p className="text-xs sm:text-sm font-mono-id text-purple-300/70 mt-1">Connected intelligence for investigator review</p></div>
        <div className="flex items-center gap-3"><Button variant="cyan" size="sm" icon={Upload} onClick={() => navigate('/data-intake')}>INGEST DATA</Button><Button variant="primary" size="sm" icon={Network} onClick={() => navigate('/network')}>FULL NETWORK</Button></div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard title="Active Cases" value={stats.activeCases} icon={FolderKanban} subtitle="Backend case files" glowColor="purple" />
        <MetricCard title="Total Entities" value={stats.totalEntities} icon={Users} subtitle="Graph nodes" glowColor="cyan" />
        <MetricCard title="Detected Relationships" value={stats.detectedRelationships.toLocaleString()} icon={Network} subtitle="Graph edges" glowColor="purple" />
        <MetricCard title="High-Risk Entities" value={stats.highRiskEntities} icon={AlertTriangle} subtitle="Requires review" glowColor="purple" />
        <MetricCard title="Active Alerts" value={stats.activeAlerts} icon={Radio} subtitle="Open backend alerts" glowColor="cyan" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard hoverEffect={false} className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-purple-900/40"><h3 className="text-sm font-bold font-mono-id uppercase tracking-wider text-purple-100 flex items-center gap-2"><FolderKanban className="w-4 h-4 text-purple-400" />Recent Investigations</h3><Button variant="outline" size="sm" onClick={() => navigate('/cases')}>View All Cases</Button></div>
          {cases.length === 0 ? <EmptyState title="No case files" message="The backend returned no cases." /> : <div className="space-y-3">{cases.slice(0, 4).map((caseData) => <button key={caseData.id} onClick={() => navigate(`/cases/${caseData.id}`)} className="w-full text-left p-3.5 bg-slate-950/60 border border-purple-900/40 hover:border-purple-500/50 rounded-xl flex items-center justify-between"><div className="space-y-1"><div className="flex items-center gap-2"><span className="text-xs font-mono-id font-bold text-cyan-300">{caseData.case_number}</span><h4 className="text-sm font-semibold text-purple-100">{caseData.title}</h4></div><p className="text-xs text-purple-300/70 line-clamp-1 font-mono-id">{caseData.description || 'No description provided'}</p></div><ArrowUpRight className="w-4 h-4 text-purple-400" /></button>)}</div>}
        </GlassCard>
        <GlassCard hoverEffect={false} className="space-y-4"><h3 className="text-xs font-bold font-mono-id uppercase tracking-wider text-purple-300/80 pb-2 border-b border-purple-900/40">Backend Metrics</h3><div className="space-y-2 text-xs font-mono-id"><div className="flex justify-between py-1 border-b border-purple-900/30"><span className="text-purple-400">Total Cases</span><span className="text-purple-100">{stats.totalCases}</span></div><div className="flex justify-between py-1 border-b border-purple-900/30"><span className="text-purple-400">Ingested Records</span><span className="text-purple-100">{stats.totalRecords}</span></div><div className="flex justify-between py-1"><span className="text-purple-400">Investigator Notice</span><span className="text-cyan-300">Human verification required</span></div></div>{stats.riskNote && <p className="text-[10px] text-purple-400/70 font-mono-id">{stats.riskNote}</p>}</GlassCard>
      </div>
    </div>
  );
};

export default DashboardPage;
