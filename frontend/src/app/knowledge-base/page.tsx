'use client';
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import { ArrowLeft, BookOpen, Upload, CheckCircle, AlertCircle, FileText, Search } from 'lucide-react';
import { knowledgeBaseApi } from '@/lib/api';

const DOC_TYPES = [
  { value: 'constitution', label: 'Constitution', color: 'text-yellow-400' },
  { value: 'law', label: 'Law / Statute', color: 'text-blue-400' },
  { value: 'bare_act', label: 'Bare Act', color: 'text-green-400' },
  { value: 'judgment', label: 'Judgment', color: 'text-purple-400' },
  { value: 'notification', label: 'Notification / Circular', color: 'text-orange-400' },
];

export default function KnowledgeBasePage() {
  const router = useRouter();
  const [status, setStatus] = useState<any>(null);
  const [docType, setDocType] = useState('law');
  const [docName, setDocName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => { loadStatus(); }, []);

  const loadStatus = async () => {
    try { setStatus(await knowledgeBaseApi.getStatus()); } catch {}
  };

  const onDrop = useCallback((files: File[]) => {
    if (files[0]) { setSelectedFile(files[0]); setDocName(files[0].name); }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'], 'text/plain': ['.txt'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] }, multiple: false,
  });

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true); setMessage(null);
    try {
      const result = await knowledgeBaseApi.uploadDocument(selectedFile, docType, docName);
      setMessage({ type: 'success', text: `✓ ${result.message}` });
      setSelectedFile(null); setDocName('');
      await loadStatus();
    } catch (e: any) {
      setMessage({ type: 'error', text: e.response?.data?.detail || 'Upload failed' });
    } finally { setUploading(false); }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const r = await knowledgeBaseApi.search(searchQuery, undefined, 8);
      setSearchResults(r.results || []);
    } catch {} finally { setSearching(false); }
  };

  const confidenceColor = (c: string) =>
    c === 'HIGH' ? 'text-green-400' : c === 'MEDIUM' ? 'text-yellow-400' : 'text-red-400';

  return (
    <div className="min-h-screen bg-gradient-to-br from-legal-darker via-legal-dark to-gray-900">
      <header className="border-b border-gray-800 bg-legal-darker/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <button onClick={() => router.push('/')} className="flex items-center gap-2 text-gray-400 hover:text-white">
            <ArrowLeft className="w-5 h-5" /> Back
          </button>
          <div className="flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-legal-gold" />
            <span className="text-white font-semibold">Legal Knowledge Base</span>
            {status?.ready && <span className="px-2 py-0.5 bg-green-900/40 text-green-400 rounded text-xs">● Active</span>}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-5xl space-y-8">
        {/* Status */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Total Documents', value: status?.total_documents ?? '—', color: 'text-blue-400' },
            { label: 'Constitution Indexed', value: status?.has_constitution ? '✓ Yes' : '✗ No', color: status?.has_constitution ? 'text-green-400' : 'text-red-400' },
            { label: 'Laws Indexed', value: status?.has_laws ? '✓ Yes' : '✗ No', color: status?.has_laws ? 'text-green-400' : 'text-red-400' },
          ].map(({ label, value, color }) => (
            <div key={label} className="p-4 bg-gray-800/60 rounded-lg border border-gray-700">
              <p className="text-gray-400 text-sm">{label}</p>
              <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
            </div>
          ))}
        </div>

        {/* Upload */}
        <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5 text-legal-gold" /> Upload Legal Document
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-gray-300 text-sm mb-1">Document Type</label>
              <select value={docType} onChange={e => setDocType(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-legal-gold">
                {DOC_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-gray-300 text-sm mb-1">Document Name</label>
              <input value={docName} onChange={e => setDocName(e.target.value)} placeholder="e.g. Constitution of India"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-legal-gold" />
            </div>
          </div>
          <div {...getRootProps()} className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive ? 'border-legal-gold bg-legal-gold/10' : selectedFile ? 'border-green-500 bg-green-900/10' : 'border-gray-600 hover:border-gray-500'}`}>
            <input {...getInputProps()} />
            {selectedFile ? (
              <div className="flex items-center justify-center gap-3">
                <FileText className="w-8 h-8 text-green-400" />
                <div className="text-left">
                  <p className="text-white font-medium">{selectedFile.name}</p>
                  <p className="text-gray-400 text-sm">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
            ) : (
              <>
                <Upload className="w-10 h-10 text-gray-500 mx-auto mb-2" />
                <p className="text-gray-300">Drop PDF, DOCX, or TXT here</p>
                <p className="text-gray-500 text-sm mt-1">Supports Constitution, Law Books, Judgments, Notifications</p>
              </>
            )}
          </div>
          <button onClick={handleUpload} disabled={!selectedFile || uploading}
            className="mt-4 w-full py-3 bg-legal-gold text-legal-darker font-semibold rounded-lg hover:bg-yellow-400 transition-colors disabled:opacity-50">
            {uploading ? 'Indexing document...' : 'Index into Knowledge Base'}
          </button>
          {message && (
            <div className={`mt-3 p-3 rounded-lg flex items-center gap-2 ${message.type === 'success' ? 'bg-green-900/20 border border-green-800' : 'bg-red-900/20 border border-red-800'}`}>
              {message.type === 'success' ? <CheckCircle className="w-4 h-4 text-green-400" /> : <AlertCircle className="w-4 h-4 text-red-400" />}
              <p className={message.type === 'success' ? 'text-green-300' : 'text-red-300'}>{message.text}</p>
            </div>
          )}
        </div>

        {/* Documents List */}
        {status?.documents?.length > 0 && (
          <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-legal-gold" /> Indexed Documents
            </h2>
            <div className="space-y-2">
              {status.documents.map((doc: any, i: number) => {
                const dt = DOC_TYPES.find(t => t.value === doc.type);
                return (
                  <div key={i} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-gray-400" />
                      <div>
                        <p className="text-white font-medium">{doc.name}</p>
                        <p className={`text-xs ${dt?.color || 'text-gray-400'}`}>{dt?.label || doc.type}</p>
                      </div>
                    </div>
                    <span className="text-gray-400 text-sm">{doc.chunks} chunks</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Search */}
        <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Search className="w-5 h-5 text-legal-gold" /> Search Knowledge Base
          </h2>
          <div className="flex gap-2">
            <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              placeholder="e.g. right to equality, Section 300 IPC, Article 21..."
              className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-legal-gold" />
            <button onClick={handleSearch} disabled={searching}
              className="px-6 py-2 bg-legal-gold text-legal-darker font-semibold rounded-lg hover:bg-yellow-400 transition-colors disabled:opacity-50">
              {searching ? '...' : 'Search'}
            </button>
          </div>
          {searchResults.length > 0 && (
            <div className="mt-4 space-y-3">
              {searchResults.map((r: any, i: number) => (
                <div key={i} className="p-4 bg-gray-700/50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-legal-gold font-medium text-sm">{r.document}</span>
                      {r.article && <span className="text-xs bg-blue-900/40 text-blue-300 px-2 py-0.5 rounded">Art. {r.article}</span>}
                      {r.section && <span className="text-xs bg-purple-900/40 text-purple-300 px-2 py-0.5 rounded">§ {r.section}</span>}
                    </div>
                    <span className={`text-xs font-medium ${confidenceColor(r.confidence)}`}>{r.confidence}</span>
                  </div>
                  <p className="text-gray-300 text-sm leading-relaxed">{r.text.slice(0, 300)}{r.text.length > 300 ? '...' : ''}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
