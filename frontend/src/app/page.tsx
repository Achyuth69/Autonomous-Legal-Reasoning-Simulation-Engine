'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Scale, Upload, FileText, BookOpen, Brain, Plus,
  ChevronRight, Clock, CheckCircle, XCircle, Loader2,
} from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import { casesApi, CaseResponse } from '@/lib/api';
import { formatDate } from '@/lib/utils';

function statusBadge(status: string) {
  const map: Record<string, string> = {
    completed: 'badge-success',
    processing: 'badge-brand',
    pending: 'badge-warn',
    failed: 'badge-danger',
  };
  const icons: Record<string, React.ReactNode> = {
    completed: <CheckCircle className="w-3 h-3" />,
    processing: <Loader2 className="w-3 h-3 animate-spin" />,
    pending: <Clock className="w-3 h-3" />,
    failed: <XCircle className="w-3 h-3" />,
  };
  return (
    <span className={`badge ${map[status] || 'badge-neutral'} gap-1`}>
      {icons[status]}
      {status}
    </span>
  );
}

export default function Home() {
  const router = useRouter();
  const [cases, setCases] = useState<CaseResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => { loadCases(); }, []);

  const loadCases = async () => {
    try { setCases(await casesApi.listCases()); }
    catch {}
    finally { setLoading(false); }
  };

  const handleCaseCreated = (caseData: CaseResponse) => {
    setCases(prev => [caseData, ...prev]);
    setShowUpload(false);
    router.push(`/cases/${caseData.id}`);
  };

  return (
    <div className="min-h-screen flex flex-col">

      {/* ── Navbar ──────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-surface-border bg-surface-base/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

          {/* Logo */}
          <a href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-brand/20 border border-brand/30 flex items-center justify-center group-hover:bg-brand/30 transition-colors">
              <Scale className="w-4 h-4 text-brand-light" />
            </div>
            <div className="hidden sm:block">
              <span className="font-semibold text-slate-100 text-sm">LexAI</span>
              <span className="text-slate-500 text-sm"> · Autonomous Legal Engine</span>
            </div>
          </a>

          {/* Nav links */}
          <nav className="hidden md:flex items-center gap-1">
            <a href="/" className="btn-ghost text-slate-300">Dashboard</a>
            <a href="/knowledge-base" className="btn-ghost">Knowledge Base</a>
            <a href="http://localhost:8000/docs" target="_blank" className="btn-ghost">API Docs</a>
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <a href="/knowledge-base" className="btn-outline hidden sm:inline-flex">
              <BookOpen className="w-4 h-4" /> KB
            </a>
            <button onClick={() => setShowUpload(s => !s)} className="btn-primary">
              <Plus className="w-4 h-4" /> New Case
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-10">

        {/* Upload panel */}
        {showUpload && (
          <div className="mb-8 animate-slide-up">
            <FileUpload onCaseCreated={handleCaseCreated} />
          </div>
        )}

        {/* ── Empty state ──────────────────────────────────── */}
        {!loading && cases.length === 0 && !showUpload && (
          <div className="text-center py-20 animate-fade-in">
            {/* Hero icon */}
            <div className="w-20 h-20 rounded-2xl bg-brand/10 border border-brand/20 flex items-center justify-center mx-auto mb-6">
              <Scale className="w-10 h-10 text-brand-light" />
            </div>
            <h2 className="text-3xl font-bold text-slate-100 mb-3">
              Autonomous Legal Reasoning
            </h2>
            <p className="text-slate-400 text-base mb-8 max-w-xl mx-auto leading-relaxed">
              Upload any legal document — complaint, petition, FIR, contract —
              and 19 specialized AI agents will analyse it end-to-end.
              Grounded in your uploaded Constitution and Law books.
            </p>
            <button onClick={() => setShowUpload(true)} className="btn-primary text-base px-8 py-3">
              <Upload className="w-5 h-5" /> Upload First Case
            </button>

            {/* Feature grid */}
            <div className="grid md:grid-cols-3 gap-4 mt-16 max-w-4xl mx-auto">
              {[
                { icon: Brain, title: '19 AI Agents', desc: 'Fact extraction, RAG retrieval, advocacy, debate, judgment — all autonomous.' },
                { icon: BookOpen, title: 'Document-First', desc: 'Every citation sourced from your uploaded Constitution and Law PDFs.' },
                { icon: Scale, title: 'Multi-Model Debate', desc: 'Two Groq LLMs argue the case across rounds before reaching consensus.' },
              ].map(({ icon: Icon, title, desc }) => (
                <div key={title} className="card p-5 text-left">
                  <div className="w-9 h-9 rounded-lg bg-brand/15 border border-brand/20 flex items-center justify-center mb-3">
                    <Icon className="w-4 h-4 text-brand-light" />
                  </div>
                  <h3 className="font-semibold text-slate-200 mb-1">{title}</h3>
                  <p className="text-slate-500 text-sm leading-relaxed">{desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Cases list ───────────────────────────────────── */}
        {cases.length > 0 && (
          <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-slate-200">
                Your Cases <span className="text-slate-500 font-normal text-sm ml-1">({cases.length})</span>
              </h2>
            </div>
            <div className="grid gap-2">
              {cases.map(c => (
                <div key={c.id} onClick={() => router.push(`/cases/${c.id}`)}
                  className="card-hover flex items-center justify-between px-5 py-4">
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="w-9 h-9 rounded-lg bg-surface-overlay border border-surface-border flex items-center justify-center shrink-0">
                      <FileText className="w-4 h-4 text-slate-400" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-slate-200 font-medium truncate">{c.title}</p>
                      <p className="text-slate-500 text-xs mt-0.5">{c.case_number} · {formatDate(c.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0 ml-4">
                    {statusBadge(c.status)}
                    <ChevronRight className="w-4 h-4 text-slate-600" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="w-8 h-8 text-brand animate-spin" />
          </div>
        )}
      </main>

      <footer className="border-t border-surface-border py-5">
        <p className="text-center text-slate-600 text-xs">
          LexAI — For educational purposes only. Not a substitute for professional legal advice.
        </p>
      </footer>
    </div>
  );
}
