'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Scale,
  FileText,
  Users,
  BookOpen,
  Gavel,
  Shield,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Clock,
} from 'lucide-react';
import { casesApi, CaseDetails } from '@/lib/api';
import { formatDate, getStatusColor } from '@/lib/utils';

export default function CasePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [caseData, setCaseData] = useState<CaseDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    loadCase();
  }, [params.id]);

  useEffect(() => {
    // Poll for updates if case is processing
    if (caseData?.status === 'processing') {
      setPolling(true);
      const interval = setInterval(() => {
        loadCase(true);
      }, 3000);
      return () => clearInterval(interval);
    } else {
      setPolling(false);
    }
  }, [caseData?.status]);

  const loadCase = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const data = await casesApi.getCase(params.id);
      setCaseData(data);
    } catch (error) {
      console.error('Error loading case:', error);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-legal-darker via-legal-dark to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-legal-gold mx-auto"></div>
          <p className="text-gray-400 mt-4">Loading case...</p>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-legal-darker via-legal-dark to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Case Not Found</h2>
          <button
            onClick={() => router.push('/')}
            className="mt-4 px-6 py-2 bg-legal-gold text-legal-darker font-semibold rounded-lg hover:bg-yellow-400 transition-colors"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText },
    { id: 'facts', label: 'Facts & Issues', icon: BookOpen },
    { id: 'arguments', label: 'Arguments', icon: Users },
    { id: 'judgment', label: 'Judgment', icon: Gavel },
    { id: 'analysis', label: 'Risk Analysis', icon: TrendingUp },
    { id: 'debate', label: 'AI Debate', icon: Users },
    { id: 'agents', label: 'Agent Logs', icon: Shield },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-legal-darker via-legal-dark to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-800 bg-legal-darker/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Cases
            </button>
            <div className="flex items-center gap-3">
              <Scale className="w-6 h-6 text-legal-gold" />
              <span className="text-white font-semibold">
                {caseData.case_number}
              </span>
              <span
                className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                  caseData.status
                )}`}
              >
                {caseData.status}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Title */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">{caseData.title}</h1>
          <p className="text-gray-400">
            Created: {formatDate(caseData.created_at)}
          </p>
          {polling && (
            <div className="mt-2 flex items-center gap-2 text-blue-400">
              <Clock className="w-4 h-4 animate-spin" />
              <span className="text-sm">Processing in progress...</span>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-legal-gold text-legal-darker'
                    : 'bg-gray-800 text-gray-400 hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6">
          {activeTab === 'overview' && <OverviewTab caseData={caseData} />}
          {activeTab === 'facts' && <FactsTab caseData={caseData} />}
          {activeTab === 'arguments' && <ArgumentsTab caseData={caseData} />}
          {activeTab === 'judgment' && <JudgmentTab caseData={caseData} />}
          {activeTab === 'analysis' && <AnalysisTab caseData={caseData} />}
          {activeTab === 'debate' && <DebateTab caseData={caseData} />}
          {activeTab === 'agents' && <AgentsTab caseData={caseData} />}
        </div>
      </main>
    </div>
  );
}

function OverviewTab({ caseData }: { caseData: CaseDetails }) {
  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Case Information</h3>
          <div className="space-y-2">
            <InfoRow label="Jurisdiction" value={caseData.jurisdiction || 'N/A'} />
            <InfoRow label="Case Type" value={caseData.case_type || 'N/A'} />
            <InfoRow
              label="Confidence Score"
              value={
                caseData.confidence_score
                  ? `${(caseData.confidence_score * 100).toFixed(1)}%`
                  : 'N/A'
              }
            />
            <InfoRow label="Verdict" value={caseData.verdict || 'Pending'} />
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Parties</h3>
          <div className="space-y-2">
            {caseData.parties && Object.keys(caseData.parties).length > 0 ? (
              Object.entries(caseData.parties).map(([role, name]) => (
                <InfoRow key={role} label={role} value={String(name)} />
              ))
            ) : (
              <p className="text-gray-400">No parties information available</p>
            )}
          </div>
        </div>
      </div>

      {caseData.status === 'processing' && (
        <div className="p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
          <p className="text-blue-400">
            Case is currently being analyzed by our AI agents. This may take a few minutes.
          </p>
        </div>
      )}

      {caseData.error && (
        <div className="p-4 bg-red-900/20 border border-red-800 rounded-lg">
          <p className="text-red-400">Error: {caseData.error}</p>
        </div>
      )}
    </div>
  );
}

function FactsTab({ caseData }: { caseData: CaseDetails }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-3">Established Facts</h3>
        {caseData.facts && caseData.facts.length > 0 ? (
          <ul className="space-y-2">
            {caseData.facts.map((fact, index) => (
              <li key={index} className="flex gap-3">
                <span className="text-legal-gold font-semibold">{index + 1}.</span>
                <span className="text-gray-300">{fact}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-400">No facts extracted yet</p>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold text-white mb-3">Legal Issues</h3>
        {caseData.legal_issues && caseData.legal_issues.length > 0 ? (
          <ul className="space-y-2">
            {caseData.legal_issues.map((issue, index) => (
              <li key={index} className="flex gap-3">
                <CheckCircle className="w-5 h-5 text-legal-gold flex-shrink-0 mt-0.5" />
                <span className="text-gray-300">{issue}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-400">No legal issues identified yet</p>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold text-white mb-3">Applicable Statutes</h3>
        {caseData.statutes && caseData.statutes.length > 0 ? (
          <div className="space-y-3">
            {caseData.statutes.slice(0, 5).map((statute: any, index) => (
              <div key={index} className="p-3 bg-gray-700/50 rounded-lg">
                <p className="text-white font-medium">{statute.statute_name}</p>
                <p className="text-gray-400 text-sm mt-1">{statute.citation}</p>
                {statute.relevance && (
                  <p className="text-gray-300 text-sm mt-2">{statute.relevance}</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">No statutes identified yet</p>
        )}
      </div>
    </div>
  );
}

function ArgumentsTab({ caseData }: { caseData: CaseDetails }) {
  const [side, setSide] = useState<'plaintiff' | 'defendant'>('plaintiff');

  const legalArgs =
    side === 'plaintiff'
      ? caseData.plaintiff_arguments
      : caseData.defendant_arguments;

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        <button
          onClick={() => setSide('plaintiff')}
          className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
            side === 'plaintiff'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-400'
          }`}
        >
          Plaintiff Arguments
        </button>
        <button
          onClick={() => setSide('defendant')}
          className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
            side === 'defendant'
              ? 'bg-red-600 text-white'
              : 'bg-gray-700 text-gray-400'
          }`}
        >
          Defendant Arguments
        </button>
      </div>

      {legalArgs ? (
        <div className="space-y-4">
          {legalArgs.opening_statement && (
            <div className="p-4 bg-gray-700/50 rounded-lg">
              <h4 className="text-white font-semibold mb-2">Opening Statement</h4>
              <p className="text-gray-300">{legalArgs.opening_statement}</p>
            </div>
          )}

          {legalArgs.main_arguments && legalArgs.main_arguments.length > 0 && (
            <div>
              <h4 className="text-white font-semibold mb-3">Main Arguments</h4>
              <div className="space-y-3">
                {legalArgs.main_arguments.map((arg: any, index: number) => (
                  <div key={index} className="p-4 bg-gray-700/50 rounded-lg">
                    <div className="flex items-start gap-3">
                      <span className="text-legal-gold font-bold">{index + 1}</span>
                      <div className="flex-1">
                        <h5 className="text-white font-medium mb-1">{arg.title}</h5>
                        <p className="text-gray-300 text-sm mb-2">{arg.claim}</p>
                        {arg.reasoning && (
                          <p className="text-gray-400 text-sm">{arg.reasoning}</p>
                        )}
                        {arg.strength && (
                          <span
                            className={`inline-block mt-2 px-2 py-1 rounded text-xs font-medium ${
                              arg.strength === 'high'
                                ? 'bg-green-900/30 text-green-400'
                                : arg.strength === 'medium'
                                ? 'bg-yellow-900/30 text-yellow-400'
                                : 'bg-red-900/30 text-red-400'
                            }`}
                          >
                            {arg.strength} strength
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {legalArgs.conclusion && (
            <div className="p-4 bg-gray-700/50 rounded-lg">
              <h4 className="text-white font-semibold mb-2">Conclusion</h4>
              <p className="text-gray-300">{legalArgs.conclusion}</p>
            </div>
          )}
        </div>
      ) : (
        <p className="text-gray-400">Arguments not available yet</p>
      )}
    </div>
  );
}

function JudgmentTab({ caseData }: { caseData: CaseDetails }) {
  const judgment = caseData.judgment;

  if (!judgment || Object.keys(judgment).length === 0) {
    return <p className="text-gray-400">Judgment not available yet</p>;
  }

  return (
    <div className="space-y-6">
      {judgment.final_decision && (
        <div className="p-6 bg-gradient-to-r from-legal-gold/10 to-yellow-900/10 border border-legal-gold rounded-lg">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Gavel className="w-6 h-6 text-legal-gold" />
            Final Decision
          </h3>
          <div className="space-y-2">
            <InfoRow label="Verdict" value={judgment.final_decision.verdict} />
            <InfoRow label="Disposition" value={judgment.final_decision.disposition} />
            {judgment.final_decision.relief_awarded && (
              <InfoRow label="Relief Awarded" value={judgment.final_decision.relief_awarded} />
            )}
          </div>
        </div>
      )}

      {judgment.judgment && (
        <div>
          <h4 className="text-white font-semibold mb-3">Full Judgment</h4>
          <div className="p-4 bg-gray-700/50 rounded-lg">
            <p className="text-gray-300 whitespace-pre-wrap">{judgment.judgment}</p>
          </div>
        </div>
      )}

      {judgment.legal_analysis && judgment.legal_analysis.length > 0 && (
        <div>
          <h4 className="text-white font-semibold mb-3">Legal Analysis</h4>
          <div className="space-y-3">
            {judgment.legal_analysis.map((analysis: any, index: number) => (
              <div key={index} className="p-4 bg-gray-700/50 rounded-lg">
                <h5 className="text-white font-medium mb-2">{analysis.issue}</h5>
                <p className="text-gray-300 text-sm mb-2">{analysis.court_reasoning}</p>
                <p className="text-legal-gold text-sm font-medium">
                  {analysis.conclusion_on_issue}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function AnalysisTab({ caseData }: { caseData: CaseDetails }) {
  const risk = caseData.risk_analysis;

  if (!risk) {
    return <p className="text-gray-400">Risk analysis not available yet</p>;
  }

  return (
    <div className="space-y-6">
      {risk.overall_risk_assessment && (
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
            <h4 className="text-white font-semibold mb-2">Plaintiff Win Probability</h4>
            <div className="flex items-center gap-3">
              <div className="flex-1 bg-gray-700 rounded-full h-3">
                <div
                  className="bg-blue-500 h-3 rounded-full"
                  style={{
                    width: `${(risk.overall_risk_assessment.plaintiff_win_probability || 0) * 100}%`,
                  }}
                />
              </div>
              <span className="text-white font-bold">
                {((risk.overall_risk_assessment.plaintiff_win_probability || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          <div className="p-4 bg-red-900/20 border border-red-800 rounded-lg">
            <h4 className="text-white font-semibold mb-2">Defendant Win Probability</h4>
            <div className="flex items-center gap-3">
              <div className="flex-1 bg-gray-700 rounded-full h-3">
                <div
                  className="bg-red-500 h-3 rounded-full"
                  style={{
                    width: `${(risk.overall_risk_assessment.defendant_win_probability || 0) * 100}%`,
                  }}
                />
              </div>
              <span className="text-white font-bold">
                {((risk.overall_risk_assessment.defendant_win_probability || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {risk.plaintiff_risks && (
          <div>
            <h4 className="text-white font-semibold mb-3">Plaintiff Risks</h4>
            <div className="space-y-2">
              {risk.plaintiff_risks.legal_risks && (
                <div className="p-3 bg-gray-700/50 rounded-lg">
                  <p className="text-gray-400 text-sm font-medium mb-1">Legal Risks</p>
                  <ul className="space-y-1">
                    {risk.plaintiff_risks.legal_risks.map((r: string, i: number) => (
                      <li key={i} className="text-gray-300 text-sm">• {r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {risk.defendant_risks && (
          <div>
            <h4 className="text-white font-semibold mb-3">Defendant Risks</h4>
            <div className="space-y-2">
              {risk.defendant_risks.legal_risks && (
                <div className="p-3 bg-gray-700/50 rounded-lg">
                  <p className="text-gray-400 text-sm font-medium mb-1">Legal Risks</p>
                  <ul className="space-y-1">
                    {risk.defendant_risks.legal_risks.map((r: string, i: number) => (
                      <li key={i} className="text-gray-300 text-sm">• {r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function DebateTab({ caseData }: { caseData: CaseDetails }) {
  const debate = caseData.multi_model_debate;

  if (!debate) {
    return <p className="text-gray-400">Multi-model debate not available yet</p>;
  }

  if (debate.status === 'skipped' || debate.error) {
    return (
      <div className="p-4 bg-yellow-900/20 border border-yellow-800 rounded-lg">
        <h4 className="text-yellow-400 font-semibold mb-2">Debate Feature Unavailable</h4>
        <p className="text-gray-300">
          {debate.error || 'The multi-model debate feature requires Groq API configuration.'}
        </p>
        <p className="text-gray-400 text-sm mt-2">
          To enable this feature, add your Groq API key to the backend configuration.
        </p>
      </div>
    );
  }

  const transcript = debate.debate_transcript || [];
  const consensus = debate.final_consensus || '';
  const models = debate.participating_models || [];
  const rounds = debate.total_rounds || 0;

  // Group by round
  const roundGroups: Record<number, typeof transcript> = {};
  transcript.forEach((entry) => {
    if (!roundGroups[entry.round]) {
      roundGroups[entry.round] = [];
    }
    roundGroups[entry.round].push(entry);
  });

  // Model colors for visual distinction
  const modelColors: Record<string, string> = {
    'Llama 3 70B': 'border-blue-500 bg-blue-900/20',
    'Mixtral 8x7B': 'border-purple-500 bg-purple-900/20',
    'Gemma 2 9B': 'border-green-500 bg-green-900/20',
  };

  return (
    <div className="space-y-6">
      {/* Debate Header */}
      <div className="p-6 bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-700 rounded-lg">
        <div className="flex items-center gap-3 mb-3">
          <Users className="w-8 h-8 text-purple-400" />
          <h3 className="text-2xl font-bold text-white">Multi-Model AI Debate</h3>
        </div>
        <p className="text-gray-300 mb-4">
          {models.length} AI models debated this case over {rounds} rounds to reach a consensus.
        </p>
        <div className="flex flex-wrap gap-2">
          {models.map((model, idx) => (
            <span
              key={idx}
              className="px-3 py-1 bg-purple-800/50 text-purple-200 rounded-full text-sm font-medium"
            >
              {model}
            </span>
          ))}
        </div>
      </div>

      {/* Debate Rounds */}
      {Object.keys(roundGroups)
        .sort((a, b) => Number(a) - Number(b))
        .map((roundNum) => (
          <div key={roundNum} className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="h-px flex-1 bg-gray-700"></div>
              <h4 className="text-lg font-semibold text-white px-4">Round {roundNum}</h4>
              <div className="h-px flex-1 bg-gray-700"></div>
            </div>

            <div className="space-y-4">
              {roundGroups[Number(roundNum)].map((entry, idx) => {
                const colorClass = modelColors[entry.model] || 'border-gray-500 bg-gray-900/20';
                
                return (
                  <div
                    key={idx}
                    className={`p-5 border-l-4 rounded-lg ${colorClass}`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h5 className="text-white font-semibold text-lg flex items-center gap-2">
                        <Users className="w-5 h-5" />
                        {entry.model}
                      </h5>
                      <span className="text-xs text-gray-400">Round {entry.round}</span>
                    </div>
                    <div className="text-gray-300 whitespace-pre-wrap leading-relaxed">
                      {entry.argument}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}

      {/* Final Consensus */}
      {consensus && (
        <div className="mt-8">
          <div className="flex items-center gap-2 mb-4">
            <div className="h-px flex-1 bg-legal-gold"></div>
            <h4 className="text-xl font-bold text-white px-4 flex items-center gap-2">
              <Gavel className="w-6 h-6 text-legal-gold" />
              Final Consensus Opinion
            </h4>
            <div className="h-px flex-1 bg-legal-gold"></div>
          </div>

          <div className="p-6 bg-gradient-to-br from-legal-gold/10 to-yellow-900/10 border-2 border-legal-gold rounded-lg">
            <div className="text-gray-200 whitespace-pre-wrap leading-relaxed">
              {consensus}
            </div>
          </div>

          <div className="mt-4 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
            <p className="text-blue-300 text-sm">
              <strong>Note:</strong> This consensus was synthesized from {rounds} rounds of debate 
              between {models.length} different AI models, each bringing unique perspectives and 
              reasoning approaches to the legal analysis.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function AgentsTab({ caseData }: { caseData: CaseDetails }) {
  const logs = caseData.agent_logs || [];

  if (logs.length === 0) {
    return <p className="text-gray-400">No agent logs available yet</p>;
  }

  return (
    <div className="space-y-4">
      {logs.map((log: any, index) => (
        <div key={index} className="p-4 bg-gray-700/50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-white font-semibold">{log.agent_name}</h4>
            <span
              className={`px-2 py-1 rounded text-xs font-medium ${
                log.status === 'success'
                  ? 'bg-green-900/30 text-green-400'
                  : 'bg-red-900/30 text-red-400'
              }`}
            >
              {log.status}
            </span>
          </div>
          <p className="text-gray-400 text-sm mb-2">
            Execution Time: {log.execution_time?.toFixed(2)}s
          </p>
          {log.reasoning_trace && log.reasoning_trace.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-600">
              <p className="text-gray-400 text-xs font-medium mb-2">Reasoning Trace:</p>
              <ul className="space-y-1">
                {log.reasoning_trace.map((trace: string, i: number) => (
                  <li key={i} className="text-gray-300 text-xs">• {trace}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-2 border-b border-gray-700">
      <span className="text-gray-400">{label}:</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}
