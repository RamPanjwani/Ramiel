import React, { useState } from 'react';
import { api } from '../api/client';

export const FileUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setStatus(`Ingesting ${file.name}...`);

    try {
      const res = await api.uploadFile(file);
      setStatus(`✓ ${res.filename} ingested: ${res.message}`);
    } catch {
      setStatus(`✗ Failed to upload ${file.name}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-[#161B1E] border border-[#2A3236] rounded-md p-3 font-mono text-xs">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[#8B979B] font-semibold text-[10px] uppercase tracking-wider">
          DOCUMENT / SCAN INGESTION
        </span>
        {uploading && <span className="text-[#D98E2F] animate-pulse">INGESTING...</span>}
      </div>

      <label className="flex flex-col items-center justify-center border border-dashed border-[#2A3236] hover:border-[#D98E2F] rounded p-4 cursor-pointer bg-[#0E1214] transition-colors">
        <span className="text-[#8B979B] text-[11px] mb-1">
          Drop PDF, P&ID drawing, or spreadsheet
        </span>
        <span className="text-[10px] text-[#4A9E6E]">[BROWSE LOCAL FILES]</span>
        <input
          type="file"
          onChange={handleFileChange}
          disabled={uploading}
          className="hidden"
          accept=".pdf,.png,.jpg,.jpeg,.xlsx,.docx,.csv"
        />
      </label>

      {status && (
        <div className="mt-2 text-[10px] text-[#E4E9EA] bg-[#1E2528] p-1.5 rounded border border-[#2A3236]">
          {status}
        </div>
      )}
    </div>
  );
};
