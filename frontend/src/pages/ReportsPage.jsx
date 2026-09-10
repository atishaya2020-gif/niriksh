import React, {
  useEffect,
  useState
} from 'react';

import {
  Sparkles,
  AlertCircle,
  Download
} from 'lucide-react';

import GlassCard from '../components/ui/GlassCard';
import Button from '../components/ui/Button';
import Select from '../components/ui/Select';

import reportService from '../services/reportService';
import caseService from '../services/caseService';

export const ReportsPage = () => {

  const [cases, setCases] =
    useState([]);

  const [caseId, setCaseId] =
    useState('');

  const [reportType, setReportType] =
    useState(
      'Network Analysis Report'
    );

  const [activeReport, setActiveReport] =
    useState(null);

  const [generating, setGenerating] =
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

          if (data.length > 0) {
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

  const handleGenerate =
    async () => {

      if (!caseId) {
        setError(
          'Please select a case.'
        );
        return;
      }

      setGenerating(true);
      setError('');

      try {

        const report =
          await reportService.generateReport(
            reportType,
            caseId
          );

        setActiveReport(report);

      } catch (err) {

        setError(
          err.message ||
          'Unable to generate report.'
        );

      } finally {

        setGenerating(false);
      }
    };

  const downloadReport =
    () => {

      if (!activeReport) {
        return;
      }

      const text = [
        activeReport.title,
        '',
        activeReport.summary,
        '',
        ...activeReport.sections.map(
          (section) =>
            `${section.heading}\n${section.content}\n`
        ),
        '',
        activeReport.disclaimer
      ].join('\n');

      const blob =
        new Blob(
          [text],
          {
            type:
              'text/plain'
          }
        );

      const url =
        URL.createObjectURL(
          blob
        );

      const anchor =
        document.createElement(
          'a'
        );

      anchor.href = url;

      anchor.download =
        `${activeReport.id}.txt`;

      anchor.click();

      URL.revokeObjectURL(
        url
      );
    };

  return (

    <div className="space-y-6">

      <div className="border-b border-purple-900/30 pb-4">

        <h1 className="text-2xl font-extrabold text-white font-mono-id">
          INTELLIGENCE DOSSIER REPORT GENERATOR
        </h1>

        <p className="text-xs text-purple-300/70 font-mono-id mt-1">
          Generate investigation reports from live case data
        </p>

      </div>

      <GlassCard
        hoverEffect={false}
        className="p-4 space-y-4"
      >

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">

          <Select
            label="Report Type"
            value={reportType}
            onChange={(e) =>
              setReportType(
                e.target.value
              )
            }
            options={[
              {
                value:
                  'Case Summary',
                label:
                  'Case Summary'
              },
              {
                value:
                  'Network Analysis Report',
                label:
                  'Network Analysis'
              },
              {
                value:
                  'Entity Relationship Report',
                label:
                  'Entity Relationship'
              },
              {
                value:
                  'Alert Summary',
                label:
                  'Alert Summary'
              }
            ]}
          />

          <Select
            label="Target Case"
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

          <Button
            variant="cyan"
            icon={Sparkles}
            disabled={
              generating ||
              !caseId
            }
            onClick={
              handleGenerate
            }
          >
            {generating
              ? 'GENERATING...'
              : 'GENERATE REPORT'}
          </Button>

        </div>

        {error && (
          <div className="p-3 rounded-xl border border-red-500/40 bg-red-950/30 text-red-300 text-xs flex gap-2">

            <AlertCircle className="w-4 h-4" />

            {error}

          </div>
        )}

      </GlassCard>

      {activeReport && (

        <GlassCard
          hoverEffect={false}
          className="p-6 sm:p-8 space-y-6"
        >

          <div className="flex items-start justify-between border-b border-purple-900/40 pb-4">

            <div>

              <span className="text-xs font-mono-id font-bold text-cyan-400">
                {activeReport.report_type}
              </span>

              <h2 className="text-xl font-extrabold text-white mt-1">
                {activeReport.title}
              </h2>

              <p className="text-xs text-purple-300/70 mt-1">
                Generated: {activeReport.generated_date}
              </p>

            </div>

            <Button
              variant="secondary"
              size="sm"
              icon={Download}
              onClick={
                downloadReport
              }
            >
              DOWNLOAD REPORT
            </Button>

          </div>

          <div className="p-3 bg-purple-950/60 rounded-xl border border-purple-500/30 text-xs text-purple-200">

            <AlertCircle className="w-4 h-4 text-cyan-400 inline mr-2" />

            {activeReport.disclaimer}

          </div>

          <div className="space-y-4 font-mono-id text-xs">

            {activeReport.sections.map(
              (section, index) => (

                <div
                  key={index}
                  className="p-4 bg-slate-950/60 rounded-xl border border-purple-900/30"
                >

                  <h4 className="text-xs font-bold text-cyan-300 mb-2">
                    {section.heading}
                  </h4>

                  <p className="text-purple-200 leading-relaxed">
                    {section.content}
                  </p>

                </div>

              )
            )}

          </div>

        </GlassCard>

      )}

    </div>
  );
};

export default ReportsPage;