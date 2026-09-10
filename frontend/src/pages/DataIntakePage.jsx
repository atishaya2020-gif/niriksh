import React, { useState, useEffect } from 'react';
import {
  useNavigate,
  useSearchParams
} from 'react-router-dom';

import {
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

import GlassCard from '../components/ui/GlassCard';
import Button from '../components/ui/Button';
import Select from '../components/ui/Select';
import { apiUpload } from '../services/api';
import caseService from '../services/caseService';

export const DataIntakePage = () => {
  const [searchParams, setSearchParams] =
    useSearchParams();

  const navigate =
    useNavigate();

  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(searchParams.get('caseId') || '');

  const [file, setFile] =
    useState(null);

  const [uploading, setUploading] =
    useState(false);

  const [result, setResult] =
    useState(null);

  const [error, setError] =
    useState('');

  useEffect(() => {
    const loadCases = async () => {
      try {
        const caseList = await caseService.getCases();
        setCases(caseList);
        if (!selectedCaseId && caseList.length > 0) {
          setSelectedCaseId(String(caseList[0].id));
        }
      } catch (err) {
        console.error('Failed to load cases for intake:', err);
      }
    };
    loadCases();
  }, []);

  const handleFileChange = (
    event
  ) => {
    const selectedFile =
      event.target.files?.[0] ||
      null;

    setFile(selectedFile);
    setError('');
    setResult(null);

    if (
      selectedFile &&
      !selectedFile.name
        .toLowerCase()
        .endsWith('.csv')
    ) {
      setError(
        'Only CSV files are supported.'
      );

      setFile(null);
    }
  };

  const handleUpload = async (
    event
  ) => {
    event.preventDefault();

    setError('');
    setResult(null);

    if (!selectedCaseId) {
      setError(
        'Please select a case first.'
      );
      return;
    }

    if (!file) {
      setError(
        'Please select a CSV file.'
      );
      return;
    }

    setUploading(true);

    try {
      const numericId = await caseService.resolveCaseId(selectedCaseId);
      const formData =
        new FormData();

      formData.append(
        'file',
        file
      );

      const response =
        await apiUpload(
          `/cases/${numericId}/upload-csv`,
          formData
        );

      setResult(
        response?.data ||
        response
      );

    } catch (err) {
      setError(
        err?.message ||
        'CSV upload failed.'
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">

      <div className="border-b border-purple-900/30 pb-4">

        <h1 className="text-2xl font-extrabold text-white font-mono-id">
          DATA INTAKE
        </h1>

        <p className="text-xs text-purple-300/70 font-mono-id mt-1">
          Secure CSV ingestion for investigation records
        </p>

      </div>

      <GlassCard
        hoverEffect={false}
        className="p-8"
      >

        <form
          onSubmit={handleUpload}
          className="space-y-6"
        >

          <div className="text-center space-y-3">

            <Upload className="w-12 h-12 text-cyan-400 mx-auto mb-2" />

            <h2 className="text-lg font-bold text-white">
              Upload Investigation Data
            </h2>

            <div className="max-w-md mx-auto text-left">
              <Select
                label="Target Investigation Case"
                value={selectedCaseId}
                onChange={(e) => {
                  setSelectedCaseId(e.target.value);
                  setSearchParams({ caseId: e.target.value }, { replace: true });
                }}
                options={[
                  { value: '', label: 'Select a target case' },
                  ...cases.map((c) => ({
                    value: String(c.id),
                    label: `${c.case_number} — ${c.title}`
                  }))
                ]}
              />
            </div>

          </div>

          <div className="border-2 border-dashed border-purple-700/50 rounded-xl p-8 text-center">

            <FileText className="w-10 h-10 text-purple-300 mx-auto mb-4" />

            <input
              id="csv-file-input"
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
              className="block w-full text-sm text-purple-200 cursor-pointer"
            />

            {file && (
              <p className="text-xs text-cyan-300 mt-4">
                Selected file: {file.name}
              </p>
            )}

          </div>

          {error && (
            <div className="p-4 rounded-xl border border-red-500/40 bg-red-950/30 text-red-300 text-xs flex gap-2">

              <AlertCircle className="w-4 h-4 flex-shrink-0" />

              <span>{error}</span>

            </div>
          )}

          {result && (
            <div className="p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/20 text-emerald-300 text-xs">

              <div className="flex items-center gap-2 mb-3">

                <CheckCircle2 className="w-5 h-5" />

                <span className="font-bold">
                  CSV uploaded successfully
                </span>

              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="p-2 bg-slate-900/50 rounded border border-purple-900/30">
                  <p className="text-purple-400 uppercase text-[10px] font-bold">Records Received</p>
                  <p className="text-cyan-300 text-lg font-bold">{result.job?.records_received || result.records_received || 0}</p>
                </div>
                <div className="p-2 bg-slate-900/50 rounded border border-purple-900/30">
                  <p className="text-purple-400 uppercase text-[10px] font-bold">Records Processed</p>
                  <p className="text-emerald-300 text-lg font-bold">{result.job?.records_processed || result.records_imported || 0}</p>
                </div>
                <div className="p-2 bg-slate-900/50 rounded border border-purple-900/30">
                  <p className="text-purple-400 uppercase text-[10px] font-bold">Entities Extracted</p>
                  <p className="text-cyan-300 text-lg font-bold">{result.job?.entities_extracted || result.entities_extracted || 0}</p>
                </div>
                <div className="p-2 bg-slate-900/50 rounded border border-purple-900/30">
                  <p className="text-purple-400 uppercase text-[10px] font-bold">Relationships Detected</p>
                  <p className="text-cyan-300 text-lg font-bold">{result.job?.relationships_detected || result.relationships_detected || 0}</p>
                </div>
              </div>

              <details className="cursor-pointer">
                <summary className="text-[10px] text-purple-400/60 uppercase font-bold hover:text-purple-300">View Full Job Payload</summary>
                <pre className="mt-2 p-2 bg-slate-950 rounded border border-purple-900/40 whitespace-pre-wrap text-[10px] text-purple-300/80 overflow-auto max-h-40">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>

            </div>
          )}

          <div className="flex justify-center gap-3">

            <Button
              type="submit"
              variant="cyan"
              icon={Upload}
              disabled={
                uploading ||
                !file ||
                !selectedCaseId
              }
            >
              {uploading
                ? 'UPLOADING...'
                : 'UPLOAD CSV'}
            </Button>

            <Button
              type="button"
              variant="secondary"
              onClick={() =>
                navigate(
                  selectedCaseId
                    ? `/cases/${selectedCaseId}`
                    : '/cases'
                )
              }
            >
              RETURN TO CASE
            </Button>

          </div>

        </form>

      </GlassCard>

    </div>
  );
};

export default DataIntakePage;
