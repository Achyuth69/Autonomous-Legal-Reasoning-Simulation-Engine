'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft, Scale, FileText, Users, BookOpen, Gavel,
  Shield, TrendingUp, CheckCircle, AlertCircle,
  Database, Brain, MessageSquare, Loader2, Trash2
} from 'lucide-react';
import { casesApi, CaseDetails } from '@/lib/api';
import { formatDate } from '@/lib/utils';

/* ═══════════════════════════════════════════════════════
   SAFE HELPERS — prevent every possible crash
══════════════════════════════════════════════════════════ */

/** Convert ANY value safely to a display string */
function s(val: any): string {
  if (val === null || val === undefined) return 'N/A';
  if (typeof val === 'string') return val.trim() || 'N/A';
  if (typeof val === 'number' || typeof val === 'boolean') return String(val);
  if (Array.isArray(val)) {
    const parts = val.map(s).filter(v => v !== 'N/A');
    return parts.join(', ') || 'N/A';
  }
  if (typeof val === 'object') {
    const parts = Object.values(val)
      .filter((v: any) => v && typeof v === 'string' && v.trim())
      .map(String);
    return parts.join(', ') || JSON.stringify(val);
  }
  return String(val);
}

/** Confidence label → badge color */
function confBadgeColor(label: string | undefined): string {
  if (!label) return 'badge-neutral';
  if (label === 'HIGH') return 'badge-success';
  if (label.includes('MEDIUM')) return 'badge-warn';
  return 'badge-danger';
}

function IR({ label, value }: { label: string; value: any }) {
  return (
    <div className="info-row">
      <span className="text-slate-500 text-sm shrink-0">{label}</span>
      <span className="text-slate-200 text-sm font-medium text-right ml-4 break-words max-w-xs">{s(value)}</span>
    </div>
  );
}

function Pill({ text, cls = 'badge-neutral' }: { text: any; cls?: string }) {
  return <span className={`badge ${cls}`}>{s(text)}</span>;
}

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return <div><h3 className="section-title">{title}</h3>{children}</div>;
}

/* ═══════════════════════════════════════════════════════
   PAGE
══════════════════════════════════════════════════════════ */
export default function CasePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [caseData, setCaseData]     = useState<CaseDetails | null>(null);
  const [loading, setLoading]       = useState(true);
  const [activeTab, setActiveTab]   = useState('overview');
  const [polling, setPolling]       = useState(false);
  const [deleting, setDeleting]     = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => { loadCase(); }, [params.id]);

  useEffect(() => {
    if (caseData?.status === 'processing') {
      setPolling(true);
      const iv = setInterval(() => loadCase(true), 3000);
      return () => clearInterval(iv);
    }
    setPolling(false);
  }, [caseData?.status]);

  const loadCase = async (silent = false) => {
    if (!silent) setLoading(true);
    try { setCaseData(await casesApi.getCase(params.id)); }
    catch {}
    finally { if (!silent) setLoading(false); }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await casesApi.deleteCase(params.id);
      router.push('/');
    } catch { setDeleting(false); setShowConfirm(false); }
  };

  if (loading) return (
    <div className="min-h-screen bg-surface-base flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-12 h-12 text-brand animate-spin mx-auto mb-3"/>
        <p className="text-slate-400">Loading case…</p>
      </div>
    </div>
  );

  if (!caseData) return (
    <div className="min-h-screen bg-surface-base flex items-center justify-center">
      <div className="text-center">
        <AlertCircle className="w-16 h-16 text-rose-500 mx-auto mb-4"/>
        <h2 className="text-2xl font-bold text-slate-100 mb-4">Case Not Found</h2>
        <button onClick={() => router.push('/')} className="btn-primary">Go Home</button>
      </div>
    </div>
  );

  const tabs = [
    { id: 'overview',  label: 'Overview',       icon: FileText },
    { id: 'evidence',  label: 'Evidence',        icon: Database },
    { id: 'facts',     label: 'Facts & Issues',  icon: BookOpen },
    { id: 'reasoning', label: 'Reasoning',       icon: Brain },
    { id: 'arguments', label: 'Arguments',       icon: Users },
    { id: 'judgment',  label: 'Judgment',        icon: Gavel },
    { id: 'analysis',  label: 'Risk Analysis',   icon: TrendingUp },
    { id: 'debate',    label: 'AI Debate',       icon: MessageSquare },
    { id: 'agents',    label: 'Agent Logs',      icon: Shield },
  ];

  const statusCls = (st: string) =>
    st === 'completed' ? 'badge-success' :
    st === 'processing' ? 'badge-brand' :
    st === 'failed' ? 'badge-danger' : 'badge-warn';

  return (
    <div className="min-h-screen bg-surface-base flex flex-col">

      {/* ── Header ── */}
      <header className="sticky top-0 z-50 border-b border-surface-border bg-surface-base/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <button onClick={() => router.push('/')} className="btn-ghost -ml-2 text-slate-400">
            <ArrowLeft className="w-4 h-4"/> Back
          </button>
          <div className="flex items-center gap-3">
            <span className="text-slate-400 text-sm font-mono hidden sm:block">{caseData.case_number}</span>
            <span className={`badge ${statusCls(caseData.status)}`}>
              {caseData.status === 'processing' && <Loader2 className="w-3 h-3 animate-spin"/>}
              {caseData.status}
            </span>
            {caseData.has_legal_kb && <span className="badge badge-accent">KB</span>}
            <button onClick={() => setShowConfirm(true)}
              className="btn-ghost text-rose-400 hover:text-rose-300 hover:bg-rose-900/20 px-2">
              <Trash2 className="w-4 h-4"/>
            </button>
          </div>
        </div>
      </header>

      {/* Delete confirm modal */}
      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="card p-6 max-w-sm w-full mx-4">
            <h3 className="text-slate-100 font-semibold text-lg mb-2">Delete Case?</h3>
            <p className="text-slate-400 text-sm mb-5">
              "<span className="text-slate-200">{caseData.title}</span>" will be permanently deleted.
            </p>
            <div className="flex gap-3">
              <button onClick={() => setShowConfirm(false)} className="btn-outline flex-1">Cancel</button>
              <button onClick={handleDelete} disabled={deleting}
                className="flex-1 py-2.5 rounded-lg font-semibold text-sm bg-rose-600 text-white hover:bg-rose-500 transition-colors disabled:opacity-50">
                {deleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto w-full px-6 py-8 flex-1">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-100 mb-1">{caseData.title}</h1>
          <p className="text-slate-500 text-sm">{formatDate(caseData.created_at)}</p>
          {polling && (
            <p className="text-brand-light text-xs mt-1 flex items-center gap-1">
              <Loader2 className="w-3 h-3 animate-spin"/> AI agents processing…
            </p>
          )}
          {!caseData.has_legal_kb && caseData.status === 'completed' && (
            <div className="mt-3 inline-flex items-center gap-2 px-3 py-2 bg-amber-900/15 border border-amber-800/40 rounded-lg">
              <span className="text-amber-400 text-xs">⚠ No KB indexed.</span>
              <a href="/knowledge-base" className="text-amber-300 text-xs underline">Upload Constitution / Laws →</a>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 overflow-x-auto pb-1 border-b border-surface-border">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setActiveTab(id)}
              className={activeTab === id ? 'tab-active' : 'tab'}>
              <Icon className="w-3.5 h-3.5"/>{label}
            </button>
          ))}
        </div>

        <div className="animate-fade-in">
          {activeTab === 'overview'  && <OverviewTab  c={caseData}/>}
          {activeTab === 'evidence'  && <EvidenceTab  c={caseData}/>}
          {activeTab === 'facts'     && <FactsTab     c={caseData}/>}
          {activeTab === 'reasoning' && <ReasoningTab c={caseData}/>}
          {activeTab === 'arguments' && <ArgumentsTab c={caseData}/>}
          {activeTab === 'judgment'  && <JudgmentTab  c={caseData}/>}
          {activeTab === 'analysis'  && <AnalysisTab  c={caseData}/>}
          {activeTab === 'debate'    && <DebateTab    c={caseData}/>}
          {activeTab === 'agents'    && <AgentsTab    c={caseData}/>}
        </div>
      </main>
    </div>
  );
}

/* ── OverviewTab ── */
function OverviewTab({ c }: { c: CaseDetails }) {
  const conf = c.confidence_assessment ?? {};
  const label = conf.confidence_label ?? '';
  const score = typeof conf.overall_confidence === 'number' ? conf.overall_confidence : 0;
  return (
    <div className="space-y-5">
      <div className="grid md:grid-cols-2 gap-5">
        <div className="card p-5">
          <h3 className="section-title">Case Information</h3>
          <IR label="Jurisdiction" value={c.jurisdiction}/>
          <IR label="Case Type"    value={c.case_type}/>
          <IR label="Verdict"      value={c.verdict ?? 'Pending'}/>
          {label && <IR label="AI Confidence" value={`${label} (${(score*100).toFixed(0)}%)`}/>}
        </div>
        <div className="card p-5">
          <h3 className="section-title">Parties</h3>
          {c.parties && Object.keys(c.parties).length > 0
            ? Object.entries(c.parties).map(([r, n]) => <IR key={r} label={r} value={n}/>)
            : <p className="text-slate-500 text-sm">No parties info</p>}
        </div>
      </div>

      {label && (
        <div className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <h4 className="section-title mb-0">Confidence Assessment</h4>
            <Pill text={label} cls={confBadgeColor(label)}/>
          </div>
          <div className="w-full bg-surface-border rounded-full h-1.5 mb-3">
            <div className="bg-brand h-1.5 rounded-full" style={{ width: `${score*100}%` }}/>
          </div>
          {(conf.limitations ?? []).map((l: string, i: number) => (
            <p key={i} className="text-amber-400 text-xs">⚠ {l}</p>
          ))}
        </div>
      )}

      {c.status === 'processing' && (
        <div className="p-4 bg-brand/10 border border-brand/20 rounded-lg">
          <p className="text-brand-light text-sm">AI agents are analysing this case…</p>
        </div>
      )}
      {c.error && (
        <div className="p-4 bg-rose-900/15 border border-rose-800/40 rounded-lg">
          <p className="text-rose-400 text-sm">Error: {c.error}</p>
        </div>
      )}
    </div>
  );
}

/* ── EvidenceTab ── */
function EvidenceTab({ c }: { c: CaseDetails }) {
  const evidence = c.ranked_evidence ?? [];
  const constitutional = c.constitutional_provisions ?? [];
  const statutory = c.statutory_provisions ?? [];
  return (
    <div className="space-y-6">
      {!c.has_legal_kb && (
        <div className="p-4 bg-amber-900/10 border border-amber-800/30 rounded-lg">
          <p className="text-amber-300 text-sm">No legal KB. <a href="/knowledge-base" className="underline">Upload Constitution / Laws</a> to enable document retrieval.</p>
        </div>
      )}
      {c.evidence_summary && (
        <div className="card p-4">
          <h4 className="section-title">Evidence Summary</h4>
          <p className="text-slate-400 text-sm">{c.evidence_summary}</p>
        </div>
      )}
      {constitutional.length > 0 && (
        <Block title={`Constitutional Provisions (${constitutional.length})`}>
          <div className="space-y-3">
            {constitutional.map((p: any, i: number) => (
              <div key={i} className="p-3 border-l-4 border-amber-500 bg-amber-900/10 rounded-r-lg">
                <div className="flex gap-2 flex-wrap mb-1">
                  {p.article    && <Pill text={`Article ${p.article}`}  cls="bg-amber-900/40 text-amber-300"/>}
                  {p.section    && <Pill text={`§ ${p.section}`}        cls="bg-blue-900/40 text-blue-300"/>}
                  {p.confidence && <Pill text={p.confidence}            cls={p.confidence==='HIGH'?'badge-success':'badge-neutral'}/>}
                </div>
                <p className="text-slate-300 text-sm">{s(p.excerpt ?? p.text ?? p.applicability)}</p>
                {p.document && <p className="text-slate-500 text-xs mt-1">📄 {p.document}</p>}
              </div>
            ))}
          </div>
        </Block>
      )}
      {statutory.length > 0 && (
        <Block title={`Statutory Provisions (${statutory.length})`}>
          <div className="space-y-3">
            {statutory.map((p: any, i: number) => (
              <div key={i} className="p-3 border-l-4 border-blue-500 bg-blue-900/10 rounded-r-lg">
                <div className="flex gap-2 flex-wrap mb-1">
                  {p.section  && <Pill text={`§ ${p.section}`}    cls="bg-blue-900/40 text-blue-300"/>}
                  {p.chapter  && <Pill text={`Ch. ${p.chapter}`}  cls="bg-purple-900/40 text-purple-300"/>}
                  {p.confidence && <Pill text={p.confidence}      cls="badge-neutral"/>}
                </div>
                <p className="text-slate-300 text-sm">{s(p.excerpt ?? p.applicability)}</p>
                {p.document && <p className="text-slate-500 text-xs mt-1">📄 {p.document}</p>}
              </div>
            ))}
          </div>
        </Block>
      )}
      {evidence.length > 0 && (
        <Block title={`Ranked Evidence (${evidence.length})`}>
          <div className="space-y-3">
            {evidence.map((e: any, i: number) => (
              <div key={i} className="card p-4">
                <div className="flex items-start justify-between mb-2 flex-wrap gap-2">
                  <div className="flex gap-2 flex-wrap">
                    <Pill text={`#${e.rank}`}                 cls="bg-brand/20 text-brand-light"/>
                    <Pill text={e.document}                   cls="bg-surface-border text-slate-300"/>
                    {e.article && <Pill text={`Art.${e.article}`} cls="bg-amber-900/40 text-amber-300"/>}
                    {e.section && <Pill text={`§${e.section}`}    cls="bg-blue-900/40 text-blue-300"/>}
                  </div>
                  <Pill text={e.confidence} cls={e.confidence==='HIGH'?'badge-success':e.confidence==='MEDIUM'?'badge-warn':'badge-danger'}/>
                </div>
                <p className="text-slate-300 text-sm leading-relaxed">{(e.text??'').slice(0,350)}{(e.text??'').length>350?'…':''}</p>
                <div className="flex gap-4 mt-2 text-xs text-slate-500">
                  <span>Sim: {((e.similarity_score??0)*100).toFixed(0)}%</span>
                  {e.rerank_score!=null && <span>Rerank: {(e.rerank_score*100).toFixed(0)}%</span>}
                  {e.supports && <span>{e.supports}</span>}
                </div>
              </div>
            ))}
          </div>
        </Block>
      )}
      {!evidence.length && !constitutional.length && !statutory.length && (
        <p className="text-slate-400 text-sm">No evidence retrieved yet.</p>
      )}
    </div>
  );
}

/* ── FactsTab ── */
function FactsTab({ c }: { c: CaseDetails }) {
  return (
    <div className="space-y-6">
      <Block title="Established Facts">
        {(c.facts??[]).length ? (
          <ul className="space-y-2">
            {(c.facts??[]).map((f, i) => (
              <li key={i} className="flex gap-3 card p-3">
                <span className="text-brand-light font-semibold shrink-0 text-sm">{i+1}.</span>
                <span className="text-slate-300 text-sm">{s(f)}</span>
              </li>
            ))}
          </ul>
        ) : <p className="text-slate-500 text-sm">No facts extracted</p>}
      </Block>
      {(c.unknown_facts??[]).length > 0 && (
        <Block title="Unknown / Missing Facts">
          <div className="card p-4 space-y-1">
            {(c.unknown_facts??[]).map((f,i)=><p key={i} className="text-amber-300 text-sm">? {s(f)}</p>)}
          </div>
        </Block>
      )}
      {(c.contradictions??[]).length > 0 && (
        <Block title="Contradictions">
          <div className="card p-4 space-y-1">
            {(c.contradictions??[]).map((f,i)=><p key={i} className="text-rose-300 text-sm">⚡ {s(f)}</p>)}
          </div>
        </Block>
      )}
      <Block title="Legal Issues">
        {(c.legal_issues??[]).length ? (
          <ul className="space-y-2">
            {(c.legal_issues??[]).map((issue, i) => (
              <li key={i} className="flex gap-2.5 items-start">
                <CheckCircle className="w-4 h-4 text-brand-light shrink-0 mt-0.5"/>
                <span className="text-slate-300 text-sm">{s(issue)}</span>
              </li>
            ))}
          </ul>
        ) : <p className="text-slate-500 text-sm">No issues identified</p>}
      </Block>
      {(c.possible_violations??[]).length > 0 && (
        <Block title="Possible Violations">
          <div className="space-y-1.5">
            {(c.possible_violations??[]).map((v,i)=>(
              <div key={i} className="flex gap-2 items-start">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5"/>
                <span className="text-slate-400 text-sm">{s(v)}</span>
              </div>
            ))}
          </div>
        </Block>
      )}
      {(c.legal_principles??[]).length > 0 && (
        <Block title={`Legal Principles (${(c.legal_principles??[]).length})`}>
          <div className="space-y-2">
            {(c.legal_principles??[]).map((p: any, i: number) => (
              <div key={i} className="card p-4">
                <p className="text-slate-200 font-medium text-sm mb-1">{s(p.principle)}</p>
                {p.derived_from && (
                  <p className="text-slate-500 text-xs">
                    📄 {s(p.derived_from.document)} {p.derived_from.article} {p.derived_from.section}
                  </p>
                )}
                {p.application && <p className="text-slate-400 text-sm mt-1">{s(p.application)}</p>}
                {p.confidence  && <Pill text={p.confidence} cls={p.confidence==='HIGH'?'badge-success':'badge-neutral'}/>}
              </div>
            ))}
          </div>
        </Block>
      )}
    </div>
  );
}

/* ── ReasoningTab ── */
function ReasoningTab({ c }: { c: CaseDetails }) {
  const chain = c.reasoning_chain ?? [];
  const outcomes = c.possible_outcomes ?? [];
  return (
    <div className="space-y-6">
      <div className="p-3 bg-surface-overlay border border-surface-border rounded-lg text-xs text-slate-500">
        Step-by-step reasoning chain — every step references a specific uploaded document.
      </div>
      {chain.length > 0 ? (
        <Block title={`Reasoning Chain (${chain.length} steps)`}>
          <div className="space-y-3">
            {chain.map((step: any, i: number) => (
              <div key={i} className="card p-4 border-l-4 border-brand/40">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <Pill text={`Step ${step.step}`} cls="badge-brand"/>
                  <span className="text-slate-200 font-medium text-sm">{s(step.issue)}</span>
                </div>
                {step.applicable_law && <p className="text-slate-500 text-xs mb-1">Law: {s(step.applicable_law)}</p>}
                {step.evidence_reference && (
                  <p className="text-blue-300 text-xs mb-2">
                    📄 {s(step.evidence_reference.document)}
                    {step.evidence_reference.article && ` · Art.${step.evidence_reference.article}`}
                    {step.evidence_reference.section && ` · §${step.evidence_reference.section}`}
                  </p>
                )}
                <p className="text-slate-400 text-sm">{s(step.reasoning)}</p>
                {step.interim_conclusion && (
                  <p className="text-brand-light text-sm font-medium mt-2">→ {s(step.interim_conclusion)}</p>
                )}
              </div>
            ))}
          </div>
        </Block>
      ) : <p className="text-slate-500 text-sm">Reasoning chain not available</p>}
      {outcomes.length > 0 && (
        <Block title="Possible Outcomes">
          <div className="grid md:grid-cols-2 gap-3">
            {outcomes.map((o: any, i: number) => (
              <div key={i} className="card p-4">
                <p className="text-slate-200 font-medium text-sm mb-2">{s(o.outcome)}</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-surface-border rounded-full h-1.5">
                    <div className="bg-brand h-1.5 rounded-full" style={{width:`${(o.probability??0)*100}%`}}/>
                  </div>
                  <span className="text-slate-400 text-sm w-10 text-right">{((o.probability??0)*100).toFixed(0)}%</span>
                </div>
                {o.confidence && <Pill text={o.confidence} cls="badge-neutral"/>}
              </div>
            ))}
          </div>
        </Block>
      )}
    </div>
  );
}

/* ── ArgumentsTab ── */
function ArgumentsTab({ c }: { c: CaseDetails }) {
  const [side, setSide] = useState<'plaintiff'|'defendant'>('plaintiff');
  const args = side === 'plaintiff' ? c.plaintiff_arguments : c.defendant_arguments;
  const challenges = side === 'plaintiff' ? (c.plaintiff_challenges??[]) : (c.defendant_challenges??[]);
  const mainArgs = (args?.main_arguments ?? args?.substantive_defenses ?? []);

  return (
    <div className="space-y-5">
      <div className="flex gap-2">
        <button onClick={()=>setSide('plaintiff')}
          className={`flex-1 py-2 rounded-lg font-medium text-sm transition-colors ${side==='plaintiff'?'bg-indigo-600 text-white':'bg-surface-overlay text-slate-400'}`}>
          Plaintiff Arguments
        </button>
        <button onClick={()=>setSide('defendant')}
          className={`flex-1 py-2 rounded-lg font-medium text-sm transition-colors ${side==='defendant'?'bg-rose-600 text-white':'bg-surface-overlay text-slate-400'}`}>
          Defendant Arguments
        </button>
      </div>

      {args ? (
        <div className="space-y-3">
          {args.opening_statement && (
            <div className="card p-4">
              <h4 className="text-slate-200 font-semibold mb-2">Opening Statement</h4>
              <p className="text-slate-300 text-sm">{s(args.opening_statement)}</p>
            </div>
          )}
          {mainArgs.map((arg: any, i: number) => (
            <div key={i} className="card p-4">
              <div className="flex items-start gap-3">
                <span className="text-brand-light font-bold shrink-0">{i+1}</span>
                <div className="flex-1">
                  <h5 className="text-slate-200 font-medium mb-1">{s(arg.title)}</h5>
                  <p className="text-slate-300 text-sm mb-2">{s(arg.claim ?? arg.counter_claim)}</p>
                  {arg.reasoning && <p className="text-slate-400 text-sm">{s(arg.reasoning)}</p>}
                  {arg.legal_basis && <p className="text-blue-300 text-xs mt-1">⚖ {s(arg.legal_basis)}</p>}
                  {arg.strength && (
                    <Pill text={`${arg.strength} strength`}
                      cls={arg.strength==='high'?'bg-emerald-900/25 text-emerald-400':arg.strength==='medium'?'bg-amber-900/25 text-amber-400':'bg-rose-900/25 text-rose-400'}/>
                  )}
                </div>
              </div>
            </div>
          ))}
          {args.conclusion && (
            <div className="card p-4">
              <h4 className="text-slate-200 font-semibold mb-2">Conclusion</h4>
              <p className="text-slate-300 text-sm">{s(args.conclusion)}</p>
            </div>
          )}
        </div>
      ) : <p className="text-slate-400 text-sm">Arguments not available yet</p>}

      {challenges.length > 0 && (
        <Block title="Cross-Examination Challenges">
          <div className="space-y-3">
            {challenges.map((ch: any, i: number) => (
              <div key={i} className="p-3 bg-amber-900/10 border border-amber-800/30 rounded-lg">
                <p className="text-amber-300 text-sm font-medium">{s(ch.argument ?? ch.defense)}</p>
                <p className="text-slate-300 text-sm mt-1">{s(ch.challenge)}</p>
                {ch.evidence_reference && <p className="text-slate-500 text-xs mt-1">📄 {s(ch.evidence_reference)}</p>}
                {ch.strength_of_challenge && (
                  <Pill text={ch.strength_of_challenge}
                    cls={ch.strength_of_challenge==='HIGH'?'badge-danger':'badge-warn'}/>
                )}
              </div>
            ))}
          </div>
        </Block>
      )}
    </div>
  );
}

/* ── JudgmentTab ── */
function JudgmentTab({ c }: { c: CaseDetails }) {
  const j = c.judgment ?? {};
  if (!Object.keys(j).length) return <p className="text-slate-400 text-sm">Judgment not available yet</p>;
  const fd = j.final_decision ?? {};
  const confScore = typeof j.confidence_score === 'number' ? j.confidence_score : 0;
  return (
    <div className="space-y-5">
      {Object.keys(fd).length > 0 && (
        <div className="p-5 bg-brand/10 border border-brand/30 rounded-xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
            <Gavel className="w-5 h-5 text-brand-light"/>Final Decision
          </h3>
          <IR label="Verdict"     value={fd.verdict}/>
          <IR label="Disposition" value={fd.disposition}/>
          {fd.relief_awarded && <IR label="Relief Awarded" value={fd.relief_awarded}/>}
          {confScore > 0 && (
            <div className="mt-4">
              <p className="text-slate-400 text-xs mb-1">Judicial Confidence: {(confScore*100).toFixed(0)}%</p>
              <div className="w-full bg-surface-border rounded-full h-1.5">
                <div className="bg-brand h-1.5 rounded-full" style={{width:`${confScore*100}%`}}/>
              </div>
            </div>
          )}
        </div>
      )}
      {j.judgment && (
        <Block title="Full Judgment">
          <div className="card p-4 max-h-96 overflow-y-auto">
            <p className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">{s(j.judgment)}</p>
          </div>
        </Block>
      )}
      {(j.legal_analysis??[]).length > 0 && (
        <Block title="Legal Analysis by Issue">
          <div className="space-y-3">
            {(j.legal_analysis??[]).map((a: any, i: number) => (
              <div key={i} className="card p-4">
                <h5 className="text-slate-200 font-medium mb-2">{s(a.issue)}</h5>
                {a.court_reasoning && <p className="text-slate-300 text-sm mb-2">{s(a.court_reasoning)}</p>}
                {a.conclusion_on_issue && (
                  <p className="text-brand-light text-sm font-medium">→ {s(a.conclusion_on_issue)}</p>
                )}
              </div>
            ))}
          </div>
        </Block>
      )}
      {(j.dissenting_views??[]).length > 0 && (
        <Block title="Dissenting Views">
          <ul className="space-y-1">
            {(j.dissenting_views??[]).map((v: any,i: number)=>(
              <li key={i} className="text-slate-400 text-sm">• {s(v)}</li>
            ))}
          </ul>
        </Block>
      )}
    </div>
  );
}

/* ── AnalysisTab ── */
function AnalysisTab({ c }: { c: CaseDetails }) {
  const risk = c.risk_analysis;
  if (!risk) return <p className="text-slate-400 text-sm">Risk analysis not available</p>;
  const overall = risk.overall_risk_assessment ?? {};
  const pR = risk.plaintiff_risks ?? {};
  const dR = risk.defendant_risks ?? {};
  return (
    <div className="space-y-5">
      <div className="grid md:grid-cols-2 gap-4">
        {[
          {label:'Plaintiff Win Probability', val:overall.plaintiff_win_probability??0, cls:'bg-indigo-500'},
          {label:'Defendant Win Probability', val:overall.defendant_win_probability??0, cls:'bg-rose-500'},
        ].map(({label,val,cls})=>(
          <div key={label} className="card p-4">
            <h4 className="text-slate-200 font-semibold mb-2 text-sm">{label}</h4>
            <div className="flex items-center gap-3">
              <div className="flex-1 bg-surface-border rounded-full h-2">
                <div className={`${cls} h-2 rounded-full`} style={{width:`${val*100}%`}}/>
              </div>
              <span className="text-slate-100 font-bold text-sm w-10 text-right">{(val*100).toFixed(0)}%</span>
            </div>
          </div>
        ))}
      </div>
      <div className="grid md:grid-cols-3 gap-3">
        {overall.case_complexity && <div className="card p-3"><p className="text-slate-500 text-xs">Complexity</p><p className="text-slate-100 font-bold capitalize">{s(overall.case_complexity)}</p></div>}
        {overall.settlement_likelihood!=null && <div className="card p-3"><p className="text-slate-500 text-xs">Settlement Likelihood</p><p className="text-slate-100 font-bold">{(overall.settlement_likelihood*100).toFixed(0)}%</p></div>}
        {overall.expected_duration && <div className="card p-3"><p className="text-slate-500 text-xs">Expected Duration</p><p className="text-slate-100 font-bold">{s(overall.expected_duration)}</p></div>}
      </div>
      <div className="grid md:grid-cols-2 gap-5">
        {[['Plaintiff Risks',pR],['Defendant Risks',dR]].map(([title,risks]:any)=>(
          <div key={title}>
            <h4 className="text-slate-200 font-semibold mb-2 text-sm">{title}</h4>
            {(risks.legal_risks??[]).length > 0 && (
              <div className="card p-3 mb-2">
                <p className="text-slate-500 text-xs mb-1 font-medium">Legal Risks</p>
                {(risks.legal_risks??[]).map((r:any,i:number)=><p key={i} className="text-slate-300 text-sm">• {s(r)}</p>)}
              </div>
            )}
            {risks.strength_score!=null && (
              <p className="text-slate-400 text-sm">Strength: <span className="text-slate-100 font-bold">{risks.strength_score}/10</span></p>
            )}
          </div>
        ))}
      </div>
      {risk.settlement_recommendations?.should_settle && (
        <div className="p-4 bg-emerald-900/15 border border-emerald-800/40 rounded-lg">
          <h4 className="text-emerald-400 font-semibold mb-1 text-sm">Settlement Recommended</h4>
          {risk.settlement_recommendations.recommended_settlement_range && (
            <p className="text-slate-300 text-sm">Range: {s(risk.settlement_recommendations.recommended_settlement_range)}</p>
          )}
        </div>
      )}
    </div>
  );
}

/* ── DebateTab ── */
function DebateTab({ c }: { c: CaseDetails }) {
  const debate = c.multi_model_debate ?? {};
  if (!Object.keys(debate).length) return <p className="text-slate-400 text-sm">Debate not available</p>;
  if (debate.status === 'skipped' || debate.error) return (
    <div className="p-4 bg-amber-900/15 border border-amber-800/40 rounded-lg">
      <h4 className="text-amber-400 font-semibold mb-1">Debate Unavailable</h4>
      <p className="text-slate-300 text-sm">{s(debate.error) ?? 'Groq API key required'}</p>
    </div>
  );
  const transcript = debate.debate_transcript ?? [];
  const groups: Record<number, typeof transcript> = {};
  transcript.forEach((e:any)=>{ if(!groups[e.round]) groups[e.round]=[]; groups[e.round].push(e); });
  return (
    <div className="space-y-5">
      <div className="p-5 bg-brand/10 border border-brand/25 rounded-xl">
        <h3 className="text-lg font-bold text-slate-100 mb-2 flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-brand-light"/>Multi-Model AI Debate
        </h3>
        <p className="text-slate-400 text-sm mb-3">{(debate.participating_models??[]).length} models · {debate.total_rounds??0} rounds</p>
        <div className="flex flex-wrap gap-2">
          {(debate.participating_models??[]).map((m:string,i:number)=>(
            <Pill key={i} text={m} cls="badge-brand"/>
          ))}
        </div>
      </div>
      {Object.keys(groups).sort((a,b)=>+a-+b).map(round=>(
        <div key={round} className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="h-px flex-1 bg-surface-border"/>
            <span className="text-slate-400 font-semibold text-sm px-3">Round {round}</span>
            <div className="h-px flex-1 bg-surface-border"/>
          </div>
          {groups[+round].map((entry:any,idx:number)=>(
            <div key={idx} className={`card p-4 border-l-4 ${entry.model?.includes('70B')?'border-brand':'border-blue-400'}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-200 font-semibold text-sm">{s(entry.model)}</span>
                <Pill text={`Round ${entry.round}`} cls="badge-neutral"/>
              </div>
              <p className="text-slate-400 text-sm whitespace-pre-wrap leading-relaxed">{s(entry.argument)}</p>
            </div>
          ))}
        </div>
      ))}
      {debate.final_consensus && (
        <div>
          <div className="flex items-center gap-2 my-4">
            <div className="h-px flex-1 bg-brand/30"/>
            <span className="text-slate-300 font-semibold text-sm flex items-center gap-1.5 px-3">
              <Gavel className="w-4 h-4 text-brand-light"/>Consensus Opinion
            </span>
            <div className="h-px flex-1 bg-brand/30"/>
          </div>
          <div className="card p-5 border-brand/30">
            <p className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">{s(debate.final_consensus)}</p>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── AgentsTab ── */
function AgentsTab({ c }: { c: CaseDetails }) {
  const logs = c.agent_logs ?? [];
  if (!logs.length) return <p className="text-slate-400 text-sm">No agent logs available</p>;
  return (
    <div className="space-y-3">
      <p className="text-slate-400 text-sm">{logs.length} agents executed</p>
      {logs.map((log: any, i: number) => (
        <div key={i} className="card p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-slate-200 font-semibold text-sm">{s(log.agent_name)}</h4>
            <div className="flex items-center gap-2">
              {log.execution_time!=null && (
                <span className="text-slate-500 text-xs">{log.execution_time.toFixed(1)}s</span>
              )}
              <Pill text={log.status}
                cls={log.status==='success'?'badge-success':log.status==='skipped'?'badge-warn':'badge-danger'}/>
            </div>
          </div>
          {log.error && <p className="text-rose-400 text-sm mb-2">{s(log.error)}</p>}
          {(log.reasoning_trace??[]).length > 0 && (
            <div className="mt-2 pt-2 border-t border-surface-border">
              <p className="text-slate-500 text-xs font-medium mb-1">Trace:</p>
              {(log.reasoning_trace??[]).map((t:any,j:number)=>(
                <p key={j} className="text-slate-400 text-xs">• {s(t)}</p>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
