'use client';
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, Loader2 } from 'lucide-react';
import { casesApi, CaseResponse } from '@/lib/api';

interface FileUploadProps {
  onCaseCreated: (caseData: CaseResponse) => void;
}

export default function FileUpload({ onCaseCreated }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setTitle(acceptedFiles[0].name.replace(/\.[^.]+$/, ''));
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: false,
  });

  const handleUpload = async () => {
    if (!selectedFile) { setError('Please select a file'); return; }
    setUploading(true); setError(null);
    try {
      const caseData = await casesApi.uploadCase(selectedFile, title || selectedFile.name);
      onCaseCreated(caseData);
      setSelectedFile(null); setTitle('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally { setUploading(false); }
  };

  return (
    <div className="card p-6 animate-slide-up">
      <h2 className="text-base font-semibold text-slate-200 mb-4">Upload Legal Document</h2>

      {!selectedFile ? (
        <div {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200 ${
            isDragActive
              ? 'border-brand bg-brand/10'
              : 'border-surface-border hover:border-brand/40 hover:bg-surface-overlay'
          }`}>
          <input {...getInputProps()} />
          <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center mx-auto mb-3">
            <Upload className="w-6 h-6 text-brand-light" />
          </div>
          {isDragActive ? (
            <p className="text-brand-light font-medium">Drop it here</p>
          ) : (
            <>
              <p className="text-slate-300 font-medium mb-1">Drag & drop or click to browse</p>
              <p className="text-slate-500 text-sm">PDF, DOCX, TXT — max 10 MB</p>
            </>
          )}
        </div>
      ) : (
        <div>
          <div className="flex items-center gap-3 p-4 bg-surface-overlay border border-surface-border rounded-xl mb-4">
            <div className="w-9 h-9 rounded-lg bg-brand/15 border border-brand/20 flex items-center justify-center shrink-0">
              <FileText className="w-4 h-4 text-brand-light" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-slate-200 font-medium text-sm truncate">{selectedFile.name}</p>
              <p className="text-slate-500 text-xs">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button onClick={() => setSelectedFile(null)}
              className="p-1.5 hover:bg-surface-border rounded-lg transition-colors">
              <X className="w-4 h-4 text-slate-400" />
            </button>
          </div>

          <div className="mb-4">
            <label className="block text-slate-400 text-sm mb-1.5">Case Title</label>
            <input type="text" value={title} onChange={e => setTitle(e.target.value)}
              className="w-full px-3 py-2.5 bg-surface-overlay border border-surface-border rounded-lg text-slate-200 text-sm placeholder-slate-600 focus:border-brand/50"
              placeholder="Enter a title for this case" />
          </div>

          <button onClick={handleUpload} disabled={uploading}
            className="btn-primary w-full justify-center py-3 text-sm disabled:opacity-50">
            {uploading ? <><Loader2 className="w-4 h-4 animate-spin"/>Analysing…</> : <><Upload className="w-4 h-4"/>Start Analysis</>}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-3 p-3 bg-rose-900/15 border border-rose-800/30 rounded-lg">
          <p className="text-rose-400 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
}
