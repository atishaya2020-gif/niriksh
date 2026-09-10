import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Network, ZoomIn, ZoomOut, Maximize2, RefreshCw } from 'lucide-react';
import cytoscape from 'cytoscape';
import GlassCard from '../components/ui/GlassCard';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Drawer from '../components/ui/Drawer';
import SearchInput from '../components/ui/SearchInput';
import Select from '../components/ui/Select';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import caseService from '../services/caseService';
import networkService from '../services/networkService';
import { getNodeColor } from '../utils/graphTransform';

export const NetworkPage = () => {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [cases, setCases] = useState([]);
  const [caseId, setCaseId] = useState(searchParams.get('caseId') || '');
  const [network, setNetwork] = useState(null);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [edgeDrawerOpen, setEdgeDrawerOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadCases = async () => {
      try {
        const caseList = await caseService.getCases();
        setCases(caseList);
        if (!caseId && caseList.length > 0) setCaseId(String(caseList[0].id));
      } catch (requestError) {
        setError(requestError);
      } finally {
        setLoading(false);
      }
    };
    loadCases();
  }, []);

  const loadNetwork = async () => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    try {
      console.log('Loading network for case:', caseId);
      const graph = await networkService.getGraph(caseId);
      console.log('Network loaded:', graph);
      setNetwork(graph);
      setSearchParams({ caseId: String(caseId) }, { replace: true });
    } catch (requestError) {
      console.error('Network load error:', requestError);
      setError(requestError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) loadNetwork();
  }, [caseId]);

  useEffect(() => {
    if (!containerRef.current || !network || !network.nodes || network.nodes.length === 0) return;
    try {
      const graphElements = [
        ...network.nodes.map((node) => ({ data: { ...node, id: node.id, label: node.label || node.name || node.id, type: (node.type || 'UNKNOWN').toUpperCase() } })),
        ...network.edges.map((edge) => ({ data: { ...edge, type: (edge.type || edge.relationship_type || 'CONNECTED_TO').toUpperCase() } }))
      ];
      if (cyRef.current) cyRef.current.destroy();
      const cy = cytoscape({
        container: containerRef.current,
        elements: graphElements,
        style: [
          { selector: 'node', style: { label: 'data(label)', color: '#F5F3FF', 'font-size': '11px', 'font-family': 'JetBrains Mono', 'text-valign': 'bottom', 'text-margin-y': 6, 'background-color': (ele) => getNodeColor(ele.data('type'), ele.data('risk')), width: (ele) => (['HIGH', 'CRITICAL'].includes(ele.data('risk')) ? 40 : 28), height: (ele) => (['HIGH', 'CRITICAL'].includes(ele.data('risk')) ? 40 : 28), 'border-width': 3, 'border-color': 'rgba(168, 85, 247, 0.6)' } },
          { selector: 'edge', style: { width: 2, 'line-color': 'rgba(139, 92, 246, 0.4)', 'target-arrow-color': 'rgba(139, 92, 246, 0.6)', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', label: 'data(label)', 'font-size': '8px', color: '#9189A3', 'text-rotation': 'autorotate' } }
        ],
        layout: { name: 'cose', animate: false, padding: 40 }
      });
      cy.on('tap', 'node', (event) => { setSelectedEntity(event.target.data()); setDrawerOpen(true); });
      cy.on('tap', 'edge', (event) => { setSelectedEdge(event.target.data()); setEdgeDrawerOpen(true); });
      cyRef.current = cy;
      return () => {
        try {
          if (cyRef.current) cyRef.current.destroy();
        } catch (e) {}
      };
    } catch (cytoscapeError) {
      console.error('Cytoscape render error:', cytoscapeError);
    }
  }, [network]);

  useEffect(() => {
    if (!cyRef.current) return;
    cyRef.current.nodes().forEach((node) => {
      const data = node.data();
      const visible = (!searchQuery || data.label.toLowerCase().includes(searchQuery.toLowerCase())) && (typeFilter === 'ALL' || data.type === typeFilter) && (riskFilter === 'ALL' || data.risk === riskFilter);
      node.style('display', visible ? 'element' : 'none');
    });
  }, [searchQuery, typeFilter, riskFilter]);

  if (loading && !network) return <LoadingState message="Loading investigation network..." />;
  if (error) return <ErrorState message={error.message} onRetry={loadNetwork} />;
  if (!network) return <LoadingState message="Loading investigation network..." />;

  return (
    <div className="h-[84vh] flex flex-col space-y-4 relative overflow-hidden">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-purple-900/30 pb-3">
        <div><h1 className="text-xl font-extrabold text-white font-mono-id tracking-tight flex items-center gap-2"><Network className="w-5 h-5 text-cyan-400" />NETWORK COMMAND CENTER • TOPOLOGY VISUALIZER</h1><p className="text-xs text-purple-300/70 font-mono-id">Interactive graph data from the selected backend case</p></div>
        <Select value={caseId} onChange={(event) => setCaseId(event.target.value)} options={[{ value: '', label: 'Select a case' }, ...cases.map((caseData) => ({ value: String(caseData.id), label: `${caseData.case_number} — ${caseData.title}` }))]} />
      </div>
      {!caseId ? <EmptyState title="Select a case" message="Choose a backend case to load its graph network." /> : <div className="flex-1 relative rounded-2xl border border-purple-500/30 overflow-hidden bg-[#05040A] flex">
        <div className="absolute top-4 left-4 z-20 space-y-3 max-w-xs"><GlassCard hoverEffect={false} className="p-3 space-y-3 bg-slate-950/80 backdrop-blur-xl"><SearchInput value={searchQuery} onChange={setSearchQuery} placeholder="Search graph nodes..." /><div className="grid grid-cols-2 gap-2"><Select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)} options={[{ value: 'ALL', label: 'All Types' }, { value: 'PERSON', label: 'Person' }, { value: 'PHONE', label: 'Telecom' }, { value: 'LOCATION', label: 'Location' }, { value: 'VEHICLE', label: 'Vehicle' }, { value: 'FINANCIAL_ACCOUNT', label: 'Financial' }, { value: 'ORGANIZATION', label: 'Organization' }]} /><Select value={riskFilter} onChange={(event) => setRiskFilter(event.target.value)} options={[{ value: 'ALL', label: 'All Risks' }, { value: 'CRITICAL', label: 'Critical' }, { value: 'HIGH', label: 'High' }, { value: 'MEDIUM', label: 'Medium' }, { value: 'LOW', label: 'Low' }]} /></div><div className="flex gap-1"><button onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)} className="p-1.5 bg-purple-900/40 rounded-lg text-purple-200"><ZoomIn className="w-4 h-4" /></button><button onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)} className="p-1.5 bg-purple-900/40 rounded-lg text-purple-200"><ZoomOut className="w-4 h-4" /></button><button onClick={() => cyRef.current?.fit()} className="p-1.5 bg-purple-900/40 rounded-lg text-purple-200"><Maximize2 className="w-4 h-4" /></button><button onClick={() => cyRef.current?.reset()} className="p-1.5 bg-purple-900/40 rounded-lg text-purple-200"><RefreshCw className="w-4 h-4" /></button></div></GlassCard></div>
        {!network?.nodes || network.nodes.length === 0 ? <div className="w-full"><EmptyState title="No graph elements" message="The backend returned no network nodes for this case." /></div> : <div ref={containerRef} className="w-full h-full" />}
        <div className="absolute bottom-4 left-4 right-4 z-20 glass-panel p-2.5 flex justify-between text-[11px] font-mono-id"><span className="text-purple-400 font-bold uppercase">Backend graph</span><span className="text-purple-400/60">{network?.nodes?.length || 0} nodes · {network?.edges?.length || 0} edges</span></div>
      </div>}
      {selectedEntity && <Drawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} title={selectedEntity.label} subtitle={`Entity Type: ${selectedEntity.type}`}><div className="space-y-4 font-mono-id text-xs"><div className="flex items-center justify-between p-3 bg-purple-950/40 rounded-xl border border-purple-500/30"><span className="text-purple-300">Risk Assessment:</span><Badge risk={selectedEntity.risk} /></div><p className="text-purple-200">{selectedEntity.metadata ? JSON.stringify(selectedEntity.metadata) : 'No additional metadata returned.'}</p><Button variant="cyan" size="sm" onClick={() => navigate(`/entities/${encodeURIComponent(selectedEntity.id)}`)}>View Full Entity Profile</Button></div></Drawer>}
      {selectedEdge && <Drawer isOpen={edgeDrawerOpen} onClose={() => setEdgeDrawerOpen(false)} title="DETECTED CONNECTION DETAILS" subtitle={`Relationship: ${selectedEdge.type}`}><div className="space-y-4 font-mono-id text-xs"><p className="text-purple-100">{selectedEdge.why_detected || selectedEdge.reason || 'No relationship explanation returned.'}</p><div className="flex justify-between p-3 bg-slate-950/80 rounded-xl border border-purple-900/40"><span className="text-purple-400">Confidence Score:</span><span className="text-cyan-400 font-bold">{Math.round((selectedEdge.confidence || 0) * 100)}%</span></div></div></Drawer>}
    </div>
  );
};

export default NetworkPage;
