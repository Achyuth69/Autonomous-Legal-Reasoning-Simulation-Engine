'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft, Scale, FileText, Users, BookOpen, Gavel,
  Shield, TrendingUp, CheckCircle, AlertCircle, Clock,
  Database, Brain, Search, BarChart2, MessageSquare
} from 'lucide-react';
import { casesApi, CaseDetails } from '@/lib/api';
import { formatDate, getStatusColor } from '@/lib/utils';

export default function CasePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [caseData, setCaseData] = useState<CaseDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [polling, setPolling] = useState(false);

  useEffect(() => { loadCase(); }, [params.id]);

  useEffect(() => {
    if (caseData?.status === 'processing') {
      setPolling(true);
      const iv = setInterval(() => loadCase(true), 3000);
      return () => clearInterval(iv);
    } else { setPolling(false); }
  }, [caseData?.status]);

  const loadCase = async (silent = false) => {
    if (!silent) setLoading(true);
    try { setCaseData(await casesApi.getCase(params.id)); }
    catch (e) { console.error(e); }
    finally { if (!silent) setLoading(false); }
  };

  if (loading) return (
    <div className="min-h-screen bg-gradient-to-br from-legal-darker via-legal-dark to-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-legal-gold mx-auto"/>
        <p className="text-gray-400 mt-4">Loading case...</p>
      </div>
    </div>
  );

  if (!caseData) return (
    <div className="min-h-screen bg-gradient-to-br from-legal-darker via-legal-dark to-gray-900 flex items-center justify-center">
      <div className="text-center">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4"/>
        <h2 className="text-2xl font-bold text-white mb-2">Case Not Found</h2>
        <button onClick={() => router.push('/')} className="mt-4 px-6 py-2 bg-legal-gold text-legal-darker font-semibold rounded-lg">Go Home</button>
      </div>
    </div>
  );

  const tabs = [
    { id: 'overview',   label: 'Overview',        icon: FileText },
    { id: 'evidence',   label: 'Evidence',         icon: Database },
    { id: 'facts',      label: 'Facts & Issues',   icon: BookOpen },
    { id: 'reasoning',  label: 'Reasoning',        icon: Brain },
    { id: 'arguments',  label: 'Arguments',        icon: Users },
    { id: 'judgment',   label: 'Judgment',         icon: Gavel },
    { id: 'analysis',   label: 'Risk Analysis',    icon: TrendingUp },
    { id: 'debate',     label: 'AI Debate',        icon: MessageSquare },
    { id: 'agents',     label: 'Agent Logs',       icon: Shield },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-legal-darker via-legal-dark to-gray-900">
      <header className="border-b border-gray-800 bg-legal-darker/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <button onClick={() => router.push('/')} className="flex items-center gap-2 text-gray-400 hover:text-white">
            <ArrowLeft className="w-5 h-5"/> Back to Cases
          </button>
          <div className="flex items-center gap-3">
            <Scale className="w-6 h-6 text-legal-gold"/>
            <span className="text-white font-semibold">{caseData.case_number}</span>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(caseData.status)}`}>{caseData.status}</span>
            {caseData.has_legal_kb && <span className="px-2 py-1 bg-green-900/40 text-green-400 rounded text-xs">KB Active</span>}
            {!caseData.has_legal_kb && caseData.status === 'completed' && <span className="px-2 py-1 bg-yellow-900/40 text-yellow-400 rounded text-xs">No KB</span>}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">{caseData.title}</h1>
          <p className="text-gray-400">Created: {formatDate(caseData.created_at)}</p>
          {polling && <div className="mt-2 flex items-center gap-2 text-blue-400"><Clock className="w-4 h-4 animate-spin"/><span className="text-sm">AI agents processing…</span></div>}
          {!caseData.has_legal_kb && caseData.status === 'completed' && (
            <div className="mt-3 p-3 bg-yellow-900/20 border border-yellow-700 rounded-lg">
              <p className="text-yellow-300 text-sm">⚠ No legal documents indexed. <a href="/knowledge-base" className="underline hover:text-yellow-200">Upload Constitution / Law Books</a> to enable document-grounded analysis.</p>
            </div>
          )}
        </div>

        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setActiveTab(id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${activeTab === id ? 'bg-legal-gold text-legal-darker' : 'bg-gray-800 text-gray-400 hover:text-white'}`}>
              <Icon className="w-4 h-4"/>{label}
            </button>
          ))}
        </div>

        <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6">
          {activeTab === 'overview'   && <OverviewTab   c={caseData}/>}
          {activeTab === 'evidence'   && <EvidenceTab   c={caseData}/>}
          {activeTab === 'facts'      && <FactsTab      c={caseData}/>}
          {activeTab === 'reasoning'  && <ReasoningTab  c={caseData}/>}
          {activeTab === 'arguments'  && <ArgumentsTab  c={caseData}/>}
          {activeTab === 'judgment'   && <JudgmentTab   c={caseData}/>}
          {activeTab === 'analysis'   && <AnalysisTab   c={caseData}/>}
          {activeTab === 'debate'     && <DebateTab     c={caseData}/>}
          {activeTab === 'agents'     && <AgentsTab     c={caseData}/>}
        </div>
      </main>
    </div>
  );
}

/* ─── helpers ─────────────────────────────────────────────────── */
function IR({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-2 border-b border-gray-700">
      <span className="text-gray-400">{label}:</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}
function Badge({ text, color = 'bg-gray-700 text-gray-300' }: { text: string; color?: string }) {
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${color}`}>{text}</span>;
}
function confColor(c: string) {
  return c === 'HIGH' ? 'text-green-400' : c === 'MEDIUM' || c === 'MEDIUM-HIGH' ? 'text-yellow-400' : 'text-red-400';
}
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-white mb-3">{title}</h3>
      {children}
    </div>
  );
}

/* ─── OverviewTab ─────────────────────────────────────────────── */
function OverviewTab({ c }: { c: CaseDetails }) {
  const conf = c.confidence_assessment;
  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <Section title="Case Information">
            <div className="space-y-1">
              <IR label="Jurisdiction" value={c.jurisdiction || 'N/A'}/>
              <IR label="Case Type" value={c.case_type || 'N/A'}/>
              <IR label="Verdict" value={c.verdict || 'Pending'}/>
              {conf && <IR label="AI Confidence" value={`${conf.confidence_label} (${(conf.overall_confidence * 100).toFixed(0)}%)`}/>}
            </div>
          </Section>
        </div>
        <div>
          <Section title="Parties">
            {c.parties && Object.keys(c.parties).length > 0
              ? Object.entries(c.parties).map(([role, name]) => <IR key={role} label={role} value={String(name)}/>)
              : <p className="text-gray-400">No parties information available</p>}
          </Section>
        </div>
      </div>

      {conf && (
        <div className="p-4 bg-gray-700/50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-white font-semibold">Confidence Assessment</h4>
            <Badge text={conf.confidence_label} color={conf.confidence_label === 'HIGH' ? 'bg-green-900/40 text-green-400' : 'bg-yellow-900/40 text-yellow-400'}/>
          </div>
          <div className="w-full bg-gray-600 rounded-full h-2 mb-3">
            <div className="bg-legal-gold h-2 rounded-full" style={{ width: `${conf.overall_confidence * 100}%` }}/>
          </div>
          {conf.limitations?.length > 0 && (
            <ul className="space-y-1">
              {conf.limitations.map((l: string, i: number) => <li key={i} className="text-yellow-300 text-sm">⚠ {l}</li>)}
            </ul>
          )}
        </div>
      )}

      {c.status === 'processing' && <div className="p-4 bg-blue-900/20 border border-blue-800 rounded-lg"><p className="text-blue-400">Agents are analysing this case…</p></div>}
      {c.error && <div className="p-4 bg-red-900/20 border border-red-800 rounded-lg"><p className="text-red-400">Error: {c.error}</p></div>}
    </div>
  );
}

/* ─── EvidenceTab ─────────────────────────────────────────────── */
function EvidenceTab({ c }: { c: CaseDetails }) {
  const evidence = c.ranked_evidence || [];
  const constitutional = c.constitutional_provisions || [];
  const statutory = c.statutory_provisions || [];
  return (
    <div className="space-y-6">
      {!c.has_legal_kb && (
        <div className="p-4 bg-yellow-900/20 border border-yellow-700 rounded-lg">
          <p className="text-yellow-300 text-sm">No legal documents indexed. <a href="/knowledge-base" className="underline">Upload documents</a> to enable RAG-based evidence retrieval.</p>
        </div>
      )}
      {c.evidence_summary && (
        <div className="p-4 bg-gray-700/50 rounded-lg">
          <h4 className="text-white font-semibold mb-1">Evidence Summary</h4>
          <p className="text-gray-300 text-sm">{c.evidence_summary}</p>
        </div>
      )}
      {constitutional.length > 0 && (
        <Section title={`Constitutional Provisions (${constitutional.length})`}>
          <div className="space-y-3">
            {constitutional.map((p: any, i: number) => (
              <div key={i} className="p-3 border-l-4 border-yellow-500 bg-yellow-900/10 rounded-r-lg">
                <div className="flex gap-2 flex-wrap mb-1">
                  {p.article && <Badge text={`Article ${p.article}`} color="bg-yellow-900/40 text-yellow-300"/>}
                  {p.section && <Badge text={`Section ${p.section}`} color="bg-blue-900/40 text-blue-300"/>}
                  {p.confidence && <Badge text={p.confidence} color={p.confidence === 'HIGH' ? 'bg-green-900/40 text-green-400' : 'bg-gray-700 text-gray-300'}/>}
                </div>
                <p className="text-gray-300 text-sm">{p.excerpt || p.text || p.applicability}</p>
                {p.document && <p className="text-gray-500 text-xs mt-1">Source: {p.document}</p>}
              </div>
            ))}
          </div>
        </Section>
      )}
      {statutory.length > 0 && (
        <Section title={`Statutory Provisions (${statutory.length})`}>
          <div className="space-y-3">
            {statutory.map((p: any, i: number) => (
              <div key={i} className="p-3 border-l-4 border-blue-500 bg-blue-900/10 rounded-r-lg">
                <div className="flex gap-2 flex-wrap mb-1">
                  {p.section && <Badge text={`Section ${p.section}`} color="bg-blue-900/40 text-blue-300"/>}
                  {p.chapter && <Badge text={`Chapter ${p.chapter}`} color="bg-purple-900/40 text-purple-300"/>}
                  {p.confidence && <Badge text={p.confidence} color="bg-gray-700 text-gray-300"/>}
                </div>
                <p className="text-gray-300 text-sm">{p.excerpt || p.applicability}</p>
                {p.document && <p className="text-gray-500 text-xs mt-1">Source: {p.document}</p>}
              </div>
            ))}
          </div>
        </Section>
      )}
      {evidence.length > 0 && (
        <Section title={`Ranked Evidence (${evidence.length} pieces)`}>
          <div className="space-y-3">
            {evidence.map((e: any, i: number) => (
              <div key={i} className="p-4 bg-gray-700/50 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex gap-2 flex-wrap">
                    <Badge text={`#${e.rank}`} color="bg-legal-gold/20 text-legal-gold"/>
                    <Badge text={e.document} color="bg-gray-600 text-gray-200"/>
                    {e.article && <Badge text={`Art. ${e.article}`} color="bg-yellow-900/40 text-yellow-300"/>}
                    {e.section && <Badge text={`§ ${e.section}`} color="bg-blue-900/40 text-blue-300"/>}
                    <Badge text={e.evidence_type || e.doc_type} color="bg-gray-700 text-gray-400"/>
                  </div>
                  <Badge text={e.confidence} color={e.confidence === 'HIGH' ? 'bg-green-900/40 text-green-400' : e.confidence === 'MEDIUM' ? 'bg-yellow-900/40 text-yellow-400' : 'bg-red-900/40 text-red-400'}/>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">{e.text?.slice(0, 350)}{e.text?.length > 350 ? '…' : ''}</p>
                <div className="flex gap-4 mt-2 text-xs text-gray-500">
                  <span>Similarity: {(e.similarity_score * 100).toFixed(0)}%</span>
                  {e.rerank_score !== null && <span>Rerank: {(e.rerank_score * 100).toFixed(0)}%</span>}
                  {e.supports && <span className={e.supports === 'plaintiff' ? 'text-blue-400' : e.supports === 'defendant' ? 'text-red-400' : 'text-gray-400'}>Supports: {e.supports}</span>}
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}
      {evidence.length === 0 && constitutional.length === 0 && statutory.length === 0 && (
        <p className="text-gray-400">No evidence retrieved. Upload legal documents to the Knowledge Base first.</p>
      )}
    </div>
  );
}

/* ─── FactsTab ────────────────────────────────────────────────── */
function FactsTab({ c }: { c: CaseDetails }) {
  return (
    <div className="space-y-6">
      <Section title="Established Facts">
        {c.facts?.length ? (
          <ul className="space-y-2">
            {c.facts.map((f, i) => (
              <li key={i} className="flex gap-3"><span className="text-legal-gold font-semibold shrink-0">{i + 1}.</span><span className="text-gray-300">{f}</span></li>
            ))}
          </ul>
        ) : <p className="text-gray-400">No facts extracted</p>}
      </Section>
      {c.unknown_facts?.length ? (
        <Section title="Unknown / Missing Facts">
          <ul className="space-y-1">
            {c.unknown_facts.map((f, i) => <li key={i} className="text-orange-300 text-sm">? {f}</li>)}
          </ul>
        </Section>
      ) : null}
      {c.contradictions?.length ? (
        <Section title="Contradictions Found">
          <ul className="space-y-1">
            {c.contradictions.map((f, i) => <li key={i} className="text-red-300 text-sm">⚡ {f}</li>)}
          </ul>
        </Section>
      ) : null}
      <Section title="Legal Issues">
        {c.legal_issues?.length ? (
          <ul className="space-y-2">
            {c.legal_issues.map((issue, i) => (
              <li key={i} className="flex gap-3"><CheckCircle className="w-5 h-5 text-legal-gold shrink-0 mt-0.5"/><span className="text-gray-300">{issue}</span></li>
            ))}
          </ul>
        ) : <p className="text-gray-400">No issues identified</p>}
      </Section>
      {c.possible_violations?.length ? (
        <Section title="Possible Violations">
          <ul className="space-y-1">
            {c.possible_violations.map((v, i) => <li key={i} className="flex gap-2"><AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5"/><span className="text-gray-300 text-sm">{v}</span></li>)}
          </ul>
        </Section>
      ) : null}
      {c.legal_principles?.length ? (
        <Section title={`Legal Principles (${c.legal_principles.length})`}>
          <div className="space-y-3">
            {c.legal_principles.map((p: any, i: number) => (
              <div key={i} className="p-3 bg-gray-700/50 rounded-lg">
                <p className="text-white font-medium text-sm">{p.principle}</p>
                {p.derived_from && (
                  <p className="text-gray-500 text-xs mt-1">Source: {p.derived_from.document} {p.derived_from.article} {p.derived_from.section}</p>
                )}
                {p.application && <p className="text-gray-400 text-sm mt-1">{p.application}</p>}
                {p.confidence && <Badge text={p.confidence} color={p.confidence === 'HIGH' ? 'bg-green-900/40 text-green-400' : 'bg-gray-700 text-gray-300'}/>}
              </div>
            ))}
          </div>
        </Section>
      ) : null}
    </div>
  );
}

/* ─── ReasoningTab ────────────────────────────────────────────── */
function ReasoningTab({ c }: { c: CaseDetails }) {
  const chain = c.reasoning_chain || [];
  const outcomes = c.possible_outcomes || [];
  return (
    <div className="space-y-6">
      <div className="p-3 bg-gray-700/30 rounded-lg text-sm text-gray-400">
        This panel shows the step-by-step reasoning chain constructed by the AI from retrieved documentary evidence.
        Every step references a specific document, article, or section.
      </div>
      {chain.length > 0 ? (
        <Section title={`Reasoning Chain (${chain.length} steps)`}>
          <div className="space-y-4">
            {chain.map((step: any, i: number) => (
              <div key={i} className="p-4 bg-gray-700/50 rounded-lg border-l-4 border-legal-gold/50">
                <div className="flex items-center gap-2 mb-2">
                  <span className="bg-legal-gold text-legal-darker text-xs font-bold px-2 py-0.5 rounded">Step {step.step}</span>
                  <span className="text-white font-medium text-sm">{step.issue}</span>
                </div>
                {step.applicable_law && <p className="text-gray-400 text-sm mb-1">Law: {step.applicable_law}</p>}
                {step.evidence_reference && (
                  <p className="text-blue-300 text-xs mb-2">
                    📄 {step.evidence_reference.document} {step.evidence_reference.article && `| Art. ${step.evidence_reference.article}`} {step.evidence_reference.section && `| § ${step.evidence_reference.section}`}
                  </p>
                )}
                <p className="text-gray-300 text-sm">{step.reasoning}</p>
                {step.interim_conclusion && (
                  <p className="text-legal-gold text-sm font-medium mt-2">→ {step.interim_conclusion}</p>
                )}
              </div>
            ))}
          </div>
        </Section>
      ) : <p className="text-gray-400">Reasoning chain not available</p>}
      {outcomes.length > 0 && (
        <Section title="Possible Outcomes">
          <div className="grid md:grid-cols-2 gap-3">
            {outcomes.map((o: any, i: number) => (
              <div key={i} className="p-4 bg-gray-700/50 rounded-lg">
                <p className="text-white font-medium text-sm mb-2">{o.outcome}</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-600 rounded-full h-2">
                    <div className="bg-legal-gold h-2 rounded-full" style={{ width: `${(o.probability || 0) * 100}%` }}/>
                  </div>
                  <span className="text-gray-300 text-sm">{((o.probability || 0) * 100).toFixed(0)}%</span>
                </div>
                {o.confidence && <Badge text={o.confidence} color="bg-gray-600 text-gray-300"/>}
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}

/* ─── ArgumentsTab ────────────────────────────────────────────── */
function ArgumentsTab({ c }: { c: CaseDetails }) {
  const [side, setSide] = useState<'plaintiff' | 'defendant'>('plaintiff');
  const legalArgs = side === 'plaintiff' ? c.plaintiff_arguments : c.defendant_arguments;
  const challenges = side === 'plaintiff' ? (c.plaintiff_challenges || []) : (c.defendant_challenges || []);

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        <button onClick={() => setSide('plaintiff')} className={`flex-1 py-2 rounded-lg font-medium transition-colors ${side === 'plaintiff' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400'}`}>Plaintiff Arguments</button>
        <button onClick={() => setSide('defendant')} className={`flex-1 py-2 rounded-lg font-medium transition-colors ${side === 'defendant' ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-400'}`}>Defendant Arguments</button>
      </div>

      {legalArgs ? (
        <div className="space-y-4">
          {legalArgs.opening_statement && (
            <div className="p-4 bg-gray-700/50 rounded-lg">
              <h4 className="text-white font-semibold mb-2">Opening Statement</h4>
              <p className="text-gray-300">{legalArgs.opening_statement}</p>
            </div>
          )}
          {(legalArgs.main_arguments || legalArgs.substantive_defenses || []).map((arg: any, i: number) => (
            <div key={i} className="p-4 bg-gray-700/50 rounded-lg">
              <div className="flex items-start gap-3">
                <span className="text-legal-gold font-bold shrink-0">{i + 1}</span>
                <div className="flex-1">
                  <h5 className="text-white font-medium mb-1">{arg.title}</h5>
                  <p className="text-gray-300 text-sm mb-2">{arg.claim || arg.counter_claim}</p>
                  {arg.reasoning && <p className="text-gray-400 text-sm">{arg.reasoning}</p>}
                  {arg.legal_basis && <p className="text-blue-300 text-xs mt-1">⚖ {arg.legal_basis}</p>}
                  {arg.strength && <Badge text={`${arg.strength} strength`} color={arg.strength === 'high' ? 'bg-green-900/30 text-green-400' : arg.strength === 'medium' ? 'bg-yellow-900/30 text-yellow-400' : 'bg-red-900/30 text-red-400'}/>}
                </div>
              </div>
            </div>
          ))}
          {legalArgs.conclusion && (
            <div className="p-4 bg-gray-700/50 rounded-lg">
              <h4 className="text-white font-semibold mb-2">Conclusion</h4>
              <p className="text-gray-300">{legalArgs.conclusion}</p>
            </div>
          )}
        </div>
      ) : <p className="text-gray-400">Arguments not available yet</p>}

      {challenges.length > 0 && (
        <div>
          <h4 className="text-white font-semibold mb-3">Cross-Examination Challenges</h4>
          <div className="space-y-3">
            {challenges.map((ch: any, i: number) => (
              <div key={i} className="p-3 bg-orange-900/10 border border-orange-800/40 rounded-lg">
                <p className="text-orange-300 text-sm font-medium">{ch.argument || ch.defense}</p>
                <p className="text-gray-300 text-sm mt-1">{ch.challenge}</p>
                {ch.evidence_reference && <p className="text-gray-500 text-xs mt-1">📄 {ch.evidence_reference}</p>}
                {ch.strength_of_challenge && <Badge text={ch.strength_of_challenge} color={ch.strength_of_challenge === 'HIGH' ? 'bg-red-900/40 text-red-400' : 'bg-yellow-900/40 text-yellow-400'}/>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── JudgmentTab ─────────────────────────────────────────────── */
function JudgmentTab({ c }: { c: CaseDetails }) {
  const j = c.judgment;
  if (!j || Object.keys(j).length === 0) return <p className="text-gray-400">Judgment not available yet</p>;
  return (
    <div className="space-y-6">
      {j.final_decision && (
        <div className="p-6 bg-gradient-to-r from-legal-gold/10 to-yellow-900/10 border border-legal-gold rounded-lg">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><Gavel className="w-6 h-6 text-legal-gold"/>Final Decision</h3>
          <div className="space-y-1">
            <IR label="Verdict" value={j.final_decision.verdict}/>
            <IR label="Disposition" value={j.final_decision.disposition}/>
            {j.final_decision.relief_awarded && <IR label="Relief Awarded" value={j.final_decision.relief_awarded}/>}
          </div>
          {j.confidence_score > 0 && (
            <div className="mt-4">
              <p className="text-gray-400 text-sm mb-1">Judicial Confidence: {(j.confidence_score * 100).toFixed(0)}%</p>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div className="bg-legal-gold h-2 rounded-full" style={{ width: `${j.confidence_score * 100}%` }}/>
              </div>
            </div>
          )}
        </div>
      )}
      {j.judgment && (
        <Section title="Full Judgment">
          <div className="p-4 bg-gray-700/50 rounded-lg max-h-96 overflow-y-auto">
            <p className="text-gray-300 whitespace-pre-wrap text-sm leading-relaxed">{j.judgment}</p>
          </div>
        </Section>
      )}
      {j.legal_analysis?.length > 0 && (
        <Section title="Legal Analysis by Issue">
          <div className="space-y-3">
            {j.legal_analysis.map((a: any, i: number) => (
              <div key={i} className="p-4 bg-gray-700/50 rounded-lg">
                <h5 className="text-white font-medium mb-2">{a.issue}</h5>
                {a.court_reasoning && <p className="text-gray-300 text-sm mb-2">{a.court_reasoning}</p>}
                {a.conclusion_on_issue && <p className="text-legal-gold text-sm font-medium">→ {a.conclusion_on_issue}</p>}
              </div>
            ))}
          </div>
        </Section>
      )}
      {j.dissenting_views?.length > 0 && (
        <Section title="Dissenting Views">
          <ul className="space-y-1">
            {j.dissenting_views.map((v: string, i: number) => <li key={i} className="text-gray-400 text-sm">• {v}</li>)}
          </ul>
        </Section>
      )}
    </div>
  );
}

/* ─── AnalysisTab ─────────────────────────────────────────────── */
function AnalysisTab({ c }: { c: CaseDetails }) {
  const risk = c.risk_analysis;
  if (!risk) return <p className="text-gray-400">Risk analysis not available</p>;
  const overall = risk.overall_risk_assessment || {};
  const pRisks = risk.plaintiff_risks || {};
  const dRisks = risk.defendant_risks || {};
  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-4">
        {[
          { label: 'Plaintiff Win Probability', val: overall.plaintiff_win_probability || 0, color: 'bg-blue-500' },
          { label: 'Defendant Win Probability', val: overall.defendant_win_probability || 0, color: 'bg-red-500' },
        ].map(({ label, val, color }) => (
          <div key={label} className="p-4 bg-gray-700/50 rounded-lg">
            <h4 className="text-white font-semibold mb-2">{label}</h4>
            <div className="flex items-center gap-3">
              <div className="flex-1 bg-gray-600 rounded-full h-3">
                <div className={`${color} h-3 rounded-full`} style={{ width: `${val * 100}%` }}/>
              </div>
              <span className="text-white font-bold w-12 text-right">{(val * 100).toFixed(0)}%</span>
            </div>
          </div>
        ))}
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        {overall.case_complexity && <div className="p-3 bg-gray-700/50 rounded-lg"><p className="text-gray-400 text-xs">Complexity</p><p className="text-white font-bold capitalize">{overall.case_complexity}</p></div>}
        {overall.settlement_likelihood !== undefined && <div className="p-3 bg-gray-700/50 rounded-lg"><p className="text-gray-400 text-xs">Settlement Likelihood</p><p className="text-white font-bold">{(overall.settlement_likelihood * 100).toFixed(0)}%</p></div>}
        {overall.expected_duration && <div className="p-3 bg-gray-700/50 rounded-lg"><p className="text-gray-400 text-xs">Expected Duration</p><p className="text-white font-bold">{overall.expected_duration}</p></div>}
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        {[['Plaintiff Risks', pRisks], ['Defendant Risks', dRisks]].map(([title, risks]: any) => (
          <div key={title}>
            <h4 className="text-white font-semibold mb-3">{title}</h4>
            {risks.legal_risks?.length > 0 && (
              <div className="p-3 bg-gray-700/50 rounded-lg mb-2">
                <p className="text-gray-400 text-xs mb-1 font-medium">Legal Risks</p>
                {risks.legal_risks.map((r: string, i: number) => <p key={i} className="text-gray-300 text-sm">• {r}</p>)}
              </div>
            )}
            {risks.strength_score !== undefined && (
              <p className="text-gray-400 text-sm">Strength Score: <span className="text-white font-bold">{risks.strength_score}/10</span></p>
            )}
          </div>
        ))}
      </div>
      {risk.settlement_recommendations?.should_settle && (
        <div className="p-4 bg-green-900/20 border border-green-800 rounded-lg">
          <h4 className="text-green-400 font-semibold mb-1">Settlement Recommended</h4>
          {risk.settlement_recommendations.recommended_settlement_range && (
            <p className="text-gray-300 text-sm">Range: {risk.settlement_recommendations.recommended_settlement_range}</p>
          )}
          {risk.settlement_recommendations.settlement_timing && (
            <p className="text-gray-300 text-sm">Timing: {risk.settlement_recommendations.settlement_timing}</p>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── DebateTab ───────────────────────────────────────────────── */
function DebateTab({ c }: { c: CaseDetails }) {
  const debate = c.multi_model_debate;
  if (!debate) return <p className="text-gray-400">Debate not available</p>;
  if (debate.status === 'skipped' || debate.error) return (
    <div className="p-4 bg-yellow-900/20 border border-yellow-800 rounded-lg">
      <h4 className="text-yellow-400 font-semibold mb-2">Debate Unavailable</h4>
      <p className="text-gray-300">{debate.error || 'Groq API key required'}</p>
    </div>
  );
  const transcript = debate.debate_transcript || [];
  const groups: Record<number, typeof transcript> = {};
  transcript.forEach(e => { if (!groups[e.round]) groups[e.round] = []; groups[e.round].push(e); });
  const modelColors: Record<string, string> = {
    'Llama 3.3 70B': 'border-blue-500 bg-blue-900/10',
    'Llama 3.1 8B': 'border-purple-500 bg-purple-900/10',
  };
  return (
    <div className="space-y-6">
      <div className="p-6 bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-700 rounded-lg">
        <h3 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
          <MessageSquare className="w-8 h-8 text-purple-400"/>Multi-Model AI Debate
        </h3>
        <p className="text-gray-300 mb-3">{(debate.participating_models || []).length} models · {debate.total_rounds || 0} rounds</p>
        <div className="flex flex-wrap gap-2">
          {(debate.participating_models || []).map((m: string, i: number) => (
            <Badge key={i} text={m} color="bg-purple-800/50 text-purple-200"/>
          ))}
        </div>
      </div>
      {Object.keys(groups).sort((a, b) => +a - +b).map(round => (
        <div key={round} className="space-y-4">
          <div className="flex items-center gap-2"><div className="h-px flex-1 bg-gray-700"/><h4 className="text-white font-semibold px-4">Round {round}</h4><div className="h-px flex-1 bg-gray-700"/></div>
          {groups[+round].map((entry, idx) => (
            <div key={idx} className={`p-5 border-l-4 rounded-lg ${modelColors[entry.model] || 'border-gray-500 bg-gray-900/20'}`}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-white font-semibold">{entry.model}</span>
                <span className="text-xs text-gray-400">Round {entry.round}</span>
              </div>
              <p className="text-gray-300 text-sm whitespace-pre-wrap leading-relaxed">{entry.argument}</p>
            </div>
          ))}
        </div>
      ))}
      {debate.final_consensus && (
        <div className="mt-6">
          <div className="flex items-center gap-2 mb-4"><div className="h-px flex-1 bg-legal-gold"/><h4 className="text-xl font-bold text-white px-4 flex items-center gap-2"><Gavel className="w-5 h-5 text-legal-gold"/>Consensus Opinion</h4><div className="h-px flex-1 bg-legal-gold"/></div>
          <div className="p-6 bg-gradient-to-br from-legal-gold/10 to-yellow-900/10 border-2 border-legal-gold rounded-lg">
            <p className="text-gray-200 whitespace-pre-wrap text-sm leading-relaxed">{debate.final_consensus}</p>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── AgentsTab ───────────────────────────────────────────────── */
function AgentsTab({ c }: { c: CaseDetails }) {
  const logs = c.agent_logs || [];
  if (!logs.length) return <p className="text-gray-400">No agent logs available</p>;
  return (
    <div className="space-y-4">
      <p className="text-gray-400 text-sm">{logs.length} agents executed</p>
      {logs.map((log: any, i: number) => (
        <div key={i} className="p-4 bg-gray-700/50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-white font-semibold">{log.agent_name}</h4>
            <div className="flex items-center gap-2">
              {log.execution_time && <span className="text-gray-500 text-xs">{log.execution_time.toFixed(1)}s</span>}
              <Badge text={log.status} color={log.status === 'success' ? 'bg-green-900/30 text-green-400' : log.status === 'skipped' ? 'bg-yellow-900/30 text-yellow-400' : 'bg-red-900/30 text-red-400'}/>
            </div>
          </div>
          {log.error && <p className="text-red-400 text-sm mb-2">{log.error}</p>}
          {log.reasoning_trace?.length > 0 && (
            <div className="mt-2 pt-2 border-t border-gray-600">
              <p className="text-gray-500 text-xs font-medium mb-1">Trace:</p>
              {log.reasoning_trace.map((t: string, j: number) => <p key={j} className="text-gray-300 text-xs">• {t}</p>)}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
