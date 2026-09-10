import React, {
  useEffect,
  useState
} from 'react';

import {
  Network,
  Play,
  AlertCircle
} from 'lucide-react';

import GlassCard from '../components/ui/GlassCard';
import Button from '../components/ui/Button';
import Select from '../components/ui/Select';

import caseService from '../services/caseService';
import networkService from '../services/networkService';

export const DisruptionPage = () => {

  const [cases, setCases] =
    useState([]);

  const [caseId, setCaseId] =
    useState('');

  const [entities, setEntities] =
    useState([]);

  const [targetEntity, setTargetEntity] =
    useState('');

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState('');

  useEffect(() => {

    const loadCases =
      async () => {

        try {

          const data =
            await caseService.getCases();

          setCases(data);

          if (data.length) {
            setCaseId(
              String(data[0].id)
            );
          }

        } catch (err) {

          setError(
            err.message ||
            'Unable to load cases.'
          );
        }
      };

    loadCases();

  }, []);

  useEffect(() => {

    const loadNetwork =
      async () => {

        if (!caseId) {
          return;
        }

        try {

          const graph =
            await networkService.getGraph(
              caseId
            );

          const people =
            graph.nodes.filter(
              (node) =>
                node.type === 'Person'
            );

          setEntities(
            people.length
              ? people
              : graph.nodes
          );

          if (
            people.length ||
            graph.nodes.length
          ) {
            setTargetEntity(
              String(
                (
                  people.length
                    ? people
                    : graph.nodes
                )[0].id
              )
            );
          }

        } catch (err) {

          setError(
            err.message ||
            'Unable to load network.'
          );
        }
      };

    loadNetwork();

  }, [caseId]);

  const runSimulation =
    async () => {

      setLoading(true);
      setError('');
      setResult(null);

      try {

        const response =
          await networkService
            .simulateDisruption(
              caseId,
              targetEntity
            );

        setResult(
          response?.data ||
          response
        );

      } catch (err) {

        setError(
          err.message ||
          'Simulation failed.'
        );

      } finally {

        setLoading(false);
      }
    };

  return (

    <div className="space-y-6">

      <div className="border-b border-purple-900/30 pb-4">

        <h1 className="text-2xl font-extrabold text-white font-mono-id">
          NETWORK DISRUPTION SIMULATOR
        </h1>

        <p className="text-xs text-purple-300/70 font-mono-id mt-1">
          Estimate network impact when a selected entity is removed
        </p>

      </div>

      <GlassCard
        hoverEffect={false}
        className="p-6"
      >

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">

          <Select
            label="Case"
            value={caseId}
            onChange={(e) =>
              setCaseId(
                e.target.value
              )
            }
            options={
              cases.map(
                (item) => ({
                  value:
                    String(item.id),

                  label:
                    `${item.case_number} • ${item.title}`
                })
              )
            }
          />

          <Select
            label="Entity to Remove"
            value={targetEntity}
            onChange={(e) =>
              setTargetEntity(
                e.target.value
              )
            }
            options={
              entities.map(
                (entity) => ({
                  value:
                    String(entity.id),

                  label:
                    entity.label ||
                    entity.id
                })
              )
            }
          />

          <Button
            variant="cyan"
            icon={Play}
            disabled={
              loading ||
              !caseId ||
              !targetEntity
            }
            onClick={
              runSimulation
            }
          >
            {loading
              ? 'SIMULATING...'
              : 'RUN SIMULATION'}
          </Button>

        </div>

        {error && (
          <div className="mt-4 p-3 rounded-xl border border-red-500/40 bg-red-950/30 text-red-300 text-xs">

            <AlertCircle className="w-4 h-4 inline mr-2" />

            {error}

          </div>
        )}

      </GlassCard>

      {result && (

        <GlassCard
          hoverEffect={false}
          className="p-6 space-y-6"
        >

          <div className="flex items-center gap-3">

            <Network className="w-7 h-7 text-cyan-400" />

            <div>

              <h2 className="text-lg font-bold text-white">
                Simulation Result
              </h2>

              <p className="text-xs text-purple-300/70">
                Target: {result.targetEntityId}
              </p>

            </div>

          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

            <div className="p-4 rounded-xl border border-purple-900/40 bg-slate-950/60">

              <h3 className="text-cyan-300 font-bold mb-3">
                BEFORE
              </h3>

              <pre className="text-xs text-purple-200 whitespace-pre-wrap">
                {JSON.stringify(
                  result.before,
                  null,
                  2
                )}
              </pre>

            </div>

            <div className="p-4 rounded-xl border border-purple-900/40 bg-slate-950/60">

              <h3 className="text-cyan-300 font-bold mb-3">
                AFTER
              </h3>

              <pre className="text-xs text-purple-200 whitespace-pre-wrap">
                {JSON.stringify(
                  result.after,
                  null,
                  2
                )}
              </pre>

            </div>

          </div>

          <div className="p-4 rounded-xl border border-cyan-500/30 bg-cyan-950/10">

            <h3 className="text-cyan-300 font-bold mb-2">
              IMPACT
            </h3>

            <p className="text-sm text-purple-100">
              {result.impactSummary}
            </p>

          </div>

        </GlassCard>

      )}

    </div>
  );
};

export default DisruptionPage;