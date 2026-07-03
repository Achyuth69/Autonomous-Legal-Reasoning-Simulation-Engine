'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Scale, Upload, FileText, BookOpen, Brain, Plus, ChevronRight, Clock, CheckCircle, XCircle, Loader2, Trash2, Key, Shield, Settings } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import { casesApi, CaseResponse } from '@/lib/api';
import { formatDate } from '@/lib/utils';

const PROVIDER_ICONS: Record<string, string> = { groq:'⚡', openai:'🤖', gemini:'✨', anthropic:'🔮', mistral:'💨', cohere:'🌊', together:'🤝', ollama:'🦙' };

function StatusBadge({ s }: { s: string }) {
  const m: Record<string,string> = { completed:'badge-success', processing:'badge-brand', pending:'badge-warn', failed:'badge-danger' };
  const icons: Record<string,React.ReactNode> = { completed:<CheckCircle className="w-3 h-3"/>, processing:<Loader2 className="w-3 h-3 animate-spin"/>, pending:<Clock className="w-3 h-3"/>, failed:<XCircle className="w-3 h-3"/> };
  return <span className={`badge gap-1 ${m[s]||'badge-neutral'}`}>{icons[s]}{s}</span>;
}

export default function Home() {
  const router = useRouter();
  const [cases, setCases]         = useState<CaseResponse[]>([]);
  const [loading, setLoading]     = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [confirmId, setConfirmId] = useState<string|null>(null);
  const [deleting, setDeleting]   = useState<string|null>(null);
  const [session, setSession]     = useState<any>(null);

  useEffect(() => {
    const raw = localStorage.getItem('lexai_session');
    if (!raw) { router.replace('/setup'); return; }
    try { setSession(JSON.parse(raw)); } catch { router.replace('/setup'); return; }
    loadCases();
  }, []);

  const loadCases = async () => {
    try { setCases(await casesApi.listCases()); }
    catch {} finally { setLoading(false); }
  };

  const handleCreated = (c: CaseResponse) => {
    setCases(p => [c, ...p]); setShowUpload(false);
    router.push(`/cases/${c.id}`);
  };

  const handleDelete = async (id: string) => {
    setDeleting(id);
    try { await casesApi.deleteCase(id); setCases(p => p.filter(c => c.id !== id)); }
    catch {} setDeleting(null); setConfirmId(null);
  };

  const clearSession = () => {
    localStorage.removeItem('lexai_session');
    router.push('/setup');
  };

  const caseToDelete = cases.find(c => c.id === confirmId);

  if (!session && !loading) return null; // redirecting

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b border-surface-border bg-surface-base/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-brand/20 border border-brand/30 flex items-center justify-center group-hover:bg-brand/30 transition-colors">
              <Scale className="w-4 h-4 text-brand-light"/>
            </div>
            <div className="hidden sm:block">
              <span className="font-semibold text-slate-100 text-sm">LexAI</span>
              <span className="text-slate-500 text-sm"> · Legal Engine</span>
            </div>
          </a>

          <nav className="hidden md:flex items-center gap-1">
            <a href="/" className="btn-ghost text-slate-300">Dashboard</a>
            <a href="/knowledge-base" className="btn-ghost">Knowledge Base</a>
            <a href="/admin" className="btn-ghost"><Shield className="w-3.5 h-3.5"/>Admin</a>
            <a href="http://localhost:8000/docs" target="_blank" className="btn-ghost">API Docs</a>
          </nav>

          <div className="flex items-center gap-2">
            {/* Session badge */}
            {session && (
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-surface-overlay border border-surface-border rounded-lg">
                <span className="text-base">{PROVIDER_ICONS[session.provider]||'🤖'}</span>
                <span className="text-slate-300 text-xs font-medium">{session.model}</span>
                <button onClick={clearSession} title="Change provider" className="text-slate-600 hover:text-slate-400 ml-1">
                  <Settings className="w-3 h-3"/>
                </button>
              </div>
            )}
            <a href="/knowledge-base" className="btn-outline hidden sm:inline-flex">
              <BookOpen className="w-4 h-4"/> KB
            </a>
            <button onClick={() => setShowUpload(s=>!s)} className="btn-primary">
              <Plus className="w-4 h-4"/> New Case
            </button>
          </div>
        </div>
      </header>

      {/* Delete modal */}
      {confirmId && caseToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="card p-6 max-w-sm w-full mx-4">
            <h3 className="text-slate-100 font-semibold text-lg mb-2">Delete Case?</h3>
            <p className="text-slate-400 text-sm mb-5">&ldquo;<span className="text-slate-200">{caseToDelete.title}</span>&rdquo; will be permanently removed.</p>
            <div className="flex gap-3">
              <button onClick={() => setConfirmId(null)} className="btn-outline flex-1">Cancel</button>
              <button onClick={() => handleDelete(confirmId)} disabled={!!deleting}
                className="flex-1 py-2.5 rounded-lg font-semibold text-sm bg-rose-600 text-white hover:bg-rose-500 transition-colors disabled:opacity-50">
                {deleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-10">
        {showUpload && (
          <div className="mb-8 animate-slide-up">
            <FileUpload onCaseCreated={handleCreated}/>
          </div>
        )}

        {/* Empty */}
        {!loading && cases.length === 0 && !showUpload && (
          <div className="text-center py-20 animate-fade-in">
            <div className="w-20 h-20 rounded-2xl bg-brand/10 border border-brand/20 flex items-center justify-center mx-auto mb-6">
              <Scale className="w-10 h-10 text-brand-light"/>
            </div>
            <h2 className="text-3xl font-bold text-slate-100 mb-3">Autonomous Legal Reasoning</h2>
            <p className="text-slate-400 text-base mb-2 max-w-xl mx-auto">
              19 AI agents analyse your legal document end-to-end.
            </p>
            {session && (
              <p className="text-slate-500 text-sm mb-8">
                Using <span className="text-brand-light">{session.provider} / {session.model}</span>
              </p>
            )}
            <button onClick={() => setShowUpload(true)} className="btn-primary text-base px-8 py-3">
              <Upload className="w-5 h-5"/> Upload First Case
            </button>
            <div className="grid md:grid-cols-3 gap-4 mt-16 max-w-4xl mx-auto">
              {[
                { icon: Brain, title:'19 AI Agents', desc:'Fact extraction, RAG, advocacy, debate, judgment — fully autonomous.' },
                { icon: BookOpen, title:'Document-First', desc:'Citations sourced from your uploaded Constitution & Law PDFs.' },
                { icon: Key, title:'Your LLM', desc:'Works with Groq, OpenAI, Gemini, Claude, Mistral, Cohere & more.' },
              ].map(({ icon:Icon, title, desc }) => (
                <div key={title} className="card p-5 text-left">
                  <div className="w-9 h-9 rounded-lg bg-brand/15 border border-brand/20 flex items-center justify-center mb-3">
                    <Icon className="w-4 h-4 text-brand-light"/>
                  </div>
                  <h3 className="font-semibold text-slate-200 mb-1">{title}</h3>
                  <p className="text-slate-500 text-sm leading-relaxed">{desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Cases list */}
        {cases.length > 0 && (
          <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-slate-200">
                Your Cases <span className="text-slate-500 font-normal text-sm ml-1">({cases.length})</span>
              </h2>
            </div>
            <div className="grid gap-2">
              {cases.map(c => (
                <div key={c.id} className="card-hover flex items-center justify-between px-5 py-4 group">
                  <div className="flex items-center gap-4 min-w-0 flex-1 cursor-pointer" onClick={() => router.push(`/cases/${c.id}`)}>
                    <div className="w-9 h-9 rounded-lg bg-surface-overlay border border-surface-border flex items-center justify-center shrink-0">
                      <FileText className="w-4 h-4 text-slate-400"/>
                    </div>
                    <div className="min-w-0">
                      <p className="text-slate-200 font-medium truncate">{c.title}</p>
                      <p className="text-slate-500 text-xs mt-0.5">
                        {c.case_number} · {formatDate(c.created_at)}
                        {(c as any).provider && <span className="ml-2">{PROVIDER_ICONS[(c as any).provider]||''} {(c as any).model}</span>}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0 ml-4">
                    <StatusBadge s={c.status}/>
                    <button onClick={e => { e.stopPropagation(); setConfirmId(c.id); }}
                      className="p-1.5 rounded-lg text-slate-600 hover:text-rose-400 hover:bg-rose-900/20 transition-colors opacity-0 group-hover:opacity-100">
                      <Trash2 className="w-4 h-4"/>
                    </button>
                    <ChevronRight className="w-4 h-4 text-slate-600 cursor-pointer" onClick={() => router.push(`/cases/${c.id}`)}/>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="w-8 h-8 text-brand animate-spin"/>
          </div>
        )}
      </main>

      <footer className="border-t border-surface-border py-5">
        <p className="text-center text-slate-600 text-xs">
          LexAI · Educational purposes only · Not a substitute for professional legal advice
        </p>
      </footer>
    </div>
  );
}
