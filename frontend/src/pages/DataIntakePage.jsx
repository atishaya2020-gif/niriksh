import React, { useState } from 'react';
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
import { apiUpload } from '../services/api';

export const DataIntakePage = () => {
  const [searchParams] =
    useSearchParams();

  const navigate =
    useNavigate();

  const caseId =
    searchParams.get('caseId');

  const [file, setFile] =
    useState(null);

  const [uploading, setUploading] =
    useState(false);

  const [result, setResult] =
    useState(null);

  const [error, setError] =
    useState('');

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

    if (!caseId) {
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
      const formData =
        new FormData();

      formData.append(
        'file',
        file
      );

      const response =
        await apiUpload(
          `/cases/${Number(caseId)}/upload-csv`,
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

          <div className="text-center">

            <Upload className="w-12 h-12 text-cyan-400 mx-auto mb-4" />

            <h2 className="text-lg font-bold text-white">
              Upload Investigation Data
            </h2>

            <p className="text-xs text-purple-300/70 mt-2">
              Case ID: {caseId || 'Not selected'}
            </p>

          </div>

          <div className="border-2 border-dashed border-purple-700/50 rounded-xl p-8 text-center">

            <FileText className="w-10 h-10 text-purple-300 mx-auto mb-4" />

            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
              className="block w-full text-sm text-purple-200"
            />

            {file && (
              <p className="text-xs text-cyan-300 mt-4">
                Selected file: {file.name}
              </p>
            )}

          </div>

          {error && (
            <div className="p-4 rounded-xl border border-red-500/40 bg-red-950/30 text-red-300 text-xs flex gap-2">

              <AlertCircle className="w-4 h-4" />

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

              <pre className="whitespace-pre-wrap text-purple-200 overflow-auto">
                {JSON.stringify(
                  result,
                  null,
                  2
                )}
              </pre>

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
                !caseId
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
                  caseId
                    ? `/cases/${caseId}`
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