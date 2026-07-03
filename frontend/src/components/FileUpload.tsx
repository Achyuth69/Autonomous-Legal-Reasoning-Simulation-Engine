'use client';
import { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, Loader2, AlertCircle } from 'lucide-react';
import { casesApi, CaseResponse } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface Props { onCaseCreated: (c: CaseResponse) => void; }

export default function FileUpload({ onCaseCreated }: Props) {
  const router = useRouter();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [session, setSession] = useState<any>(null);

  useEffect(() => {
    const raw = localStorage.getItem('lexai_session');
    if (raw) {
      try { setSession(JSON.parse(raw)); } catch {}
    }
  }, []);

  const onDrop = useCallback((files: File[]) => {
    if (files[0]) { setFile(files[0]); setTitle(files[0].name.replace(/\.[^.]+$/, '')); setError(null); }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'], 'text/plain': ['.txt'] }, multiple: false,
  });

  const goSetup = () => router.push('/setup');

  const handleUpload = async () => {
    if (!file) { setError('Select a file first'); return; }
    if (!session?.session_id) { setError('Configure your API key first'); return; }
    setUploading(true); setError(null);
    try {
      const data = await casesApi.uploadCase(file, title || file.name, session.session_id);
      onCaseCreated(data);
      setFile(null); setTitle('');
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Upload failed');
    } finally { setUploading(false); }
  };

  // No session configured
  if (!session) {
    return (
      <div className="card p-6 text-center">
        <AlertCircle className="w-10 h-10 text-amber-400 mx-auto mb-3" />
        <h3 className="text-slate-200 font-semibold mb-2">API Key Required</h3>
        <p className="text-slate-400 text-sm mb-4">You need to configure an LLM provider before uploading a case.</p>
        <button onClick={goSetup} className="btn-primary mx-auto">Configure API Key →</button>
      </div>
    );
  }

  return (
    <div className="card p-6 animate-slide-up">
      {/* Provider badge */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-slate-200">Upload Legal Document</h2>
        <div className="flex items-center gap-2">
          <span className="badge badge-success text-xs">
            {session.provider} / {session.model}
          </span>
          <button onClick={goSetup} className="text-slate-500 hover:text-slate-300 text-xs underline">Change</button>
        </div>
      </div>

      {!file ? (
        <div {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${isDragActive ? 'border-brand bg-brand/10' : 'border-surface-border hover:border-brand/40 hover:bg-surface-overlay'}`}>
          <input {...getInputProps()} />
          <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center mx-auto mb-3">
            <Upload className="w-6 h-6 text-brand-light" />
          </div>
          <p className="text-slate-300 font-medium mb-1">Drag & drop or click to browse</p>
          <p className="text-slate-500 text-sm">PDF, DOCX, TXT — max 10 MB</p>
        </div>
      ) : (
        <div>
          <div className="flex items-center gap-3 p-4 bg-surface-overlay border border-surface-border rounded-xl mb-4">
            <div className="w-9 h-9 rounded-lg bg-brand/15 border border-brand/20 flex items-center justify-center shrink-0">
              <FileText className="w-4 h-4 text-brand-light" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-slate-200 font-medium text-sm truncate">{file.name}</p>
              <p className="text-slate-500 text-xs">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button onClick={() => setFile(null)} className="p-1.5 hover:bg-surface-border rounded-lg transition-colors">
              <X className="w-4 h-4 text-slate-400" />
            </button>
          </div>
          <div className="mb-4">
            <label className="block text-slate-400 text-sm mb-1.5">Case Title</label>
            <input value={title} onChange={e => setTitle(e.target.value)}
              className="w-full px-3 py-2.5 bg-surface-overlay border border-surface-border rounded-lg text-slate-200 text-sm placeholder-slate-600 focus:border-brand/50 focus:outline-none"
              placeholder="Enter a title" />
          </div>
          <button onClick={handleUpload} disabled={uploading}
            className="btn-primary w-full justify-center py-3 text-sm disabled:opacity-50">
            {uploading ? <><Loader2 className="w-4 h-4 animate-spin" />Analysing…</> : <><Upload className="w-4 h-4" />Start Analysis</>}
          </button>
        </div>
      )}
      {error && (
        <div className="mt-3 p-3 bg-rose-900/15 border border-rose-800/30 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <p className="text-rose-300 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
}
