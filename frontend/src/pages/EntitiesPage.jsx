import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import Table from '../components/ui/Table';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import SearchInput from '../components/ui/SearchInput';
import Select from '../components/ui/Select';
import GlassCard from '../components/ui/GlassCard';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import entityService from '../services/entityService';

export const EntitiesPage = () => {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const navigate = useNavigate();

  const loadEntities = async () => {
    setLoading(true);
    setError(null);
    try {
      setEntities(await entityService.getEntities({ search, type: typeFilter }));
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(loadEntities, 200);
    return () => clearTimeout(timer);
  }, [search, typeFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-purple-900/30 pb-4"><div><h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">Extracted Entity Registry</h1><p className="text-xs text-purple-300/70 font-mono-id mt-1">Graph entities returned by the backend</p></div></div>
      <GlassCard hoverEffect={false} className="p-4"><div className="grid grid-cols-1 sm:grid-cols-2 gap-4"><SearchInput value={search} onChange={setSearch} placeholder="Search entity label, phone, account, or ID..." /><Select label="Entity Type" value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)} options={[{ value: 'ALL', label: 'All Entity Types' }, { value: 'PERSON', label: 'Person' }, { value: 'PHONE', label: 'Phone / Telecom' }, { value: 'LOCATION', label: 'Location' }, { value: 'VEHICLE', label: 'Vehicle' }, { value: 'FINANCIAL_ACCOUNT', label: 'Financial Account' }, { value: 'ORGANIZATION', label: 'Organization' }, { value: 'EVENT', label: 'Event' }, { value: 'TRANSACTION', label: 'Transaction' }]} /></div></GlassCard>
      {loading && <LoadingState message="Searching entity resolution graph..." />}
      {!loading && error && <ErrorState message={error.message} onRetry={loadEntities} />}
      {!loading && !error && entities.length === 0 && <EmptyState title="No entities found" message="The backend returned no entities for the current filters." />}
      {!loading && !error && entities.length > 0 && <Table headers={['Entity Name / ID', 'Type', 'Risk Rating', 'Source', 'Action']}>{entities.map((entity) => <tr key={entity.id} onClick={() => navigate(`/entities/${encodeURIComponent(entity.id)}`)} className="hover:bg-purple-900/30 transition-colors cursor-pointer"><td className="px-4 py-3.5 font-semibold text-purple-100">{entity.name}</td><td className="px-4 py-3.5 text-xs font-mono-id text-cyan-300">{entity.type}</td><td className="px-4 py-3.5"><Badge risk={entity.risk} size="sm" /></td><td className="px-4 py-3.5 text-xs font-mono-id text-purple-400/80">{entity.source}</td><td className="px-4 py-3.5"><Button variant="outline" size="sm" icon={ChevronRight}>Profile</Button></td></tr>)}</Table>}
    </div>
  );
};

export default EntitiesPage;
