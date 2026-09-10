import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Upload } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import Button from '../components/ui/Button';

export const DataIntakePage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const caseId = searchParams.get('caseId');

  return (
    <div className="space-y-6">
      <div className="border-b border-purple-900/30 pb-4"><h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">DATA INTAKE</h1><p className="text-xs text-purple-300/70 font-mono-id mt-1">Backend CSV ingestion is not exposed through this frontend workflow yet.</p></div>
      <GlassCard hoverEffect={false} className="p-8 text-center space-y-4"><Upload className="w-12 h-12 text-cyan-400 mx-auto" /><h2 className="text-lg font-bold text-white">CSV Upload UI Unavailable</h2><p className="text-xs text-purple-300/70 font-mono-id max-w-lg mx-auto">The backend supports CSV ingestion through its case-scoped upload API. This screen does not submit files until a real upload form and backend result mapping are implemented, so no simulated records, matches, or relationships are displayed.</p>{caseId && <p className="text-xs text-cyan-300 font-mono-id">Selected database case ID: {caseId}</p>}<Button variant="secondary" onClick={() => navigate(caseId ? `/cases/${caseId}` : '/cases')}>Return to Cases</Button></GlassCard>
    </div>
  );
};

export default DataIntakePage;
