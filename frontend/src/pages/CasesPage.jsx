import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import Table from '../components/ui/Table';
import Button from '../components/ui/Button';
import SearchInput from '../components/ui/SearchInput';
import GlassCard from '../components/ui/GlassCard';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import caseService from '../services/caseService';

export const CasesPage = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const loadCases = async () => {
    setLoading(true);
    setError(null);
    try {
      setCases(await caseService.getCases({ search }));
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(loadCases, 200);
    return () => clearTimeout(timer);
  }, [search]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-purple-900/30 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">Case Investigations Registry</h1>
          <p className="text-xs text-purple-300/70 font-mono-id mt-1">Backend case files available to the authenticated investigator</p>
        </div>
      </div>

      <GlassCard hoverEffect={false} className="p-4">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search by case number, title, or description..."
        />
      </GlassCard>

      {loading && <LoadingState message="Fetching investigation files..." />}
      {!loading && error && <ErrorState message={error.message} onRetry={loadCases} />}
      {!loading && !error && cases.length === 0 && <EmptyState title="No cases found" message="No backend case files match the current search." />}
      {!loading && !error && cases.length > 0 && (
        <Table headers={['Case Number', 'Case Title', 'Description', 'Created', 'Action']}>
          {cases.map((caseData) => (
            <tr
              key={caseData.id}
              onClick={() => navigate(`/cases/${caseData.id}`)}
              className="hover:bg-purple-900/30 transition-colors cursor-pointer"
            >
              <td className="px-4 py-3.5 font-mono-id font-bold text-cyan-300">{caseData.case_number}</td>
              <td className="px-4 py-3.5 font-semibold text-purple-100">{caseData.title}</td>
              <td className="px-4 py-3.5 text-xs text-purple-300 font-mono-id">{caseData.description || 'No description provided'}</td>
              <td className="px-4 py-3.5 text-xs font-mono-id text-purple-400/70">{caseData.last_updated}</td>
              <td className="px-4 py-3.5"><Button variant="outline" size="sm" icon={ChevronRight}>Open</Button></td>
            </tr>
          ))}
        </Table>
      )}
    </div>
  );
};

export default CasesPage;
