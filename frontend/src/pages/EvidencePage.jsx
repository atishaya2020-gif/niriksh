import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Upload } from 'lucide-react';
import Table from '../components/ui/Table';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Select from '../components/ui/Select';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import evidenceService from '../services/evidenceService';
import caseService from '../services/caseService';

export const EvidencePage = () => {
  const [searchParams] = useSearchParams();
  const [cases, setCases] = useState([]);
  const [caseId, setCaseId] = useState(searchParams.get('caseId') || '');
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadEvidence = async () => {
    if (!caseId) { setEvidence([]); setLoading(false); return; }
    setLoading(true);
    setError(null);
    try {
      setEvidence(await evidenceService.getEvidenceList(caseId));
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadCases = async () => {
      try {
        const caseList = await caseService.getCases();
        setCases(caseList);
        if (!caseId && caseList.length > 0) setCaseId(String(caseList[0].id));
      } catch (requestError) {
        setError(requestError);
        setLoading(false);
      }
    };
    loadCases();
  }, []);

  useEffect(() => { loadEvidence(); }, [caseId]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-purple-900/30 pb-4"><div><h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">EVIDENCE VAULT</h1><p className="text-xs text-purple-300/70 font-mono-id mt-1">Persisted evidence records for the selected backend case</p></div></div>
      <div className="max-w-md"><Select label="Case" value={caseId} onChange={(event) => setCaseId(event.target.value)} options={[{ value: '', label: 'Select a case' }, ...cases.map((caseData) => ({ value: String(caseData.id), label: `${caseData.case_number} — ${caseData.title}` }))]} /></div>
      {loading && <LoadingState message="Loading case evidence..." />}
      {!loading && error && <ErrorState message={error.message} onRetry={loadEvidence} />}
      {!loading && !error && !caseId && <EmptyState title="Select a case" message="Choose a backend case to view its evidence." />}
      {!loading && !error && caseId && evidence.length === 0 && <EmptyState title="No persisted evidence" message="The backend returned no evidence for this case." />}
      {!loading && !error && evidence.length > 0 && <Table headers={['Evidence ID', 'Description', 'Type', 'Source', 'Collected', 'Verification Status']}>{evidence.map((item) => <tr key={item.id} className="hover:bg-purple-900/30 transition-colors"><td className="px-4 py-3.5 font-mono-id font-bold text-cyan-300">{item.id}</td><td className="px-4 py-3.5 font-semibold text-purple-100">{item.description}</td><td className="px-4 py-3.5 text-xs font-mono-id text-purple-200">{item.evidence_type}</td><td className="px-4 py-3.5 text-xs font-mono-id text-purple-300">{item.source}</td><td className="px-4 py-3.5 text-xs font-mono-id text-purple-400/70">{item.created_at ? new Date(item.created_at).toLocaleString() : 'Unavailable'}</td><td className="px-4 py-3.5"><Badge status={item.status} size="sm" /></td></tr>)}</Table>}
    </div>
  );
};

export default EvidencePage;
