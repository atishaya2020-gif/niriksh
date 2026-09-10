import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, FolderKanban, Users, Radio, Network, ArrowRight } from 'lucide-react';
import Modal from '../ui/Modal';
import { searchService } from '../../services/searchService';

export const GlobalSearchModal = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const navigate = useNavigate();

  const handleSearch = useCallback(async (searchQuery) => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setResults(null);
      return;
    }

    setSearching(true);
    try {
      const searchResults = await searchService.search(searchQuery, 20);
      setResults(searchResults);
    } catch (error) {
      console.error('Search failed:', error);
      setResults({ results: [], count: 0 });
    } finally {
      setSearching(false);
    }
  }, []);

  const handleSelect = (path) => {
    onClose();
    navigate(path);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} maxWidth="max-w-xl">
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3.5 top-3.5 w-4 h-4 text-purple-400/60" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              handleSearch(e.target.value);
            }}
            placeholder="Global search: Type 'Raj Kumar', 'DEMO-SIH', 'Wire Transfer'..."
            className="w-full bg-slate-950 text-purple-100 placeholder-purple-400/40 border border-purple-500/40 rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 font-mono-id"
          />
        </div>

        {!query && (
          <div className="py-8 text-center text-xs text-purple-300/50 font-mono-id space-y-1">
            <p>TYPE TO SEARCH ACROSS SYSTEM INTELLIGENCE</p>
            <p className="text-[10px] text-purple-400/40">Entities • Cases • Alerts</p>
          </div>
        )}

        {searching && (
          <div className="py-4 text-center text-xs text-purple-300/50 font-mono-id">
            Searching backend...
          </div>
        )}

        {results && !searching && (
          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-1">
            {results.results.length === 0 && (
              <p className="py-6 text-center text-xs text-purple-300/50 font-mono-id">
                No intelligence records match query "{query}"
              </p>
            )}

            {results.results.length > 0 && (
              <div className="space-y-1.5">
                {results.results.map((r, idx) => (
                  <div
                    key={idx}
                    onClick={() => {
                      if (r.entity_type === 'CASE' || r.entity_type === 'case') {
                        handleSelect(`/cases/${r.case_ids?.[0] || ''}`);
                      } else {
                        handleSelect(`/entities/${encodeURIComponent(r.entity_id || r.label || idx)}`);
                      }
                    }}
                    className="p-2.5 bg-slate-900/60 border border-purple-900/40 hover:border-purple-500/40 rounded-xl flex items-center justify-between cursor-pointer transition-colors"
                  >
                    <div>
                      <span className="text-xs font-bold text-purple-100">{r.label || r.name}</span>
                      <span className="ml-2 text-[10px] font-mono-id px-1.5 py-0.5 rounded bg-purple-900/40 text-purple-300">
                        {r.entity_type || r.type}
                      </span>
                      {r.risk && (
                        <span className="ml-2 text-[10px] font-mono-id text-red-400">
                          {r.risk}
                        </span>
                      )}
                      {r.cross_case && (
                        <span className="ml-2 text-[10px] font-mono-id text-cyan-400">
                          Cross-Case
                        </span>
                      )}
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-purple-400/60" />
                  </div>
                ))}
              </div>
            )}

            {results.count > results.results.length && (
              <p className="text-center text-[10px] text-purple-400/50 font-mono-id">
                Showing {results.results.length} of {results.count} results
              </p>
            )}
          </div>
        )}
      </div>
    </Modal>
  );
};

export default GlobalSearchModal;