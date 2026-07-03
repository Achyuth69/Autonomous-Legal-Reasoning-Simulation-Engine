'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Shield, RefreshCw, Loader2, User, Key, Clock } from 'lucide-react';
import { sessionsApi } from '@/lib/api';
import { formatDate } from '@/lib/utils';

const PROVIDER_ICONS: Record<string, string> = {
  groq: '⚡', openai: '🤖', gemini: '✨', anthropic: '🔮',
  mistral: '💨', cohere: '🌊', together: '🤝', ollama: '🦙',
};

export default function AdminPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await sessionsApi.adminListSessions();
      setSessions(data.sessions || []);
      setTotal(data.total || 0);
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="min-h-screen bg-surface-base">
      <header className="sticky top-0 z-50 border-b border-surface-border bg-surface-base/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <button onClick={() => router.push('/')} className="btn-ghost -ml-2 text-slate-400">
            <ArrowLeft className="w-4 h-4" /> Back
          </button>
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-brand-light" />
            <span className="text-slate-200 font-semibold">Admin — User Sessions</span>
            <span className="badge badge-neutral">{total} total</span>
          </div>
          <button onClick={load} className="btn-ghost">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-surface-border bg-surface-overlay">
            <p className="text-slate-400 text-sm">
              All users who have configured an API key. Keys are masked. Stored in SQLite/PostgreSQL.
            </p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-brand animate-spin" />
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-16 text-slate-500">
              No sessions yet. Users will appear here after they configure their API key.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-surface-border bg-surface-overlay">
                    {['User', 'Provider', 'Model', 'API Key', 'Cases', 'Created'].map(h => (
                      <th key={h} className="text-left px-5 py-3 text-slate-400 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sessions.map((s, i) => (
                    <tr key={s.session_id} className={`border-b border-surface-border hover:bg-surface-overlay transition-colors ${i % 2 === 0 ? '' : 'bg-surface-raised/30'}`}>
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded-full bg-brand/20 flex items-center justify-center">
                            <User className="w-3.5 h-3.5 text-brand-light" />
                          </div>
                          <span className="text-slate-200 font-medium">{s.user_name || '—'}</span>
                        </div>
                      </td>
                      <td className="px-5 py-3">
                        <span className="text-lg mr-1">{PROVIDER_ICONS[s.provider] || '🤖'}</span>
                        <span className="text-slate-300 capitalize">{s.provider}</span>
                      </td>
                      <td className="px-5 py-3">
                        <span className="badge badge-brand font-mono text-xs">{s.model}</span>
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-1">
                          <Key className="w-3 h-3 text-slate-500" />
                          <span className="font-mono text-slate-400 text-xs">{s.api_key}</span>
                        </div>
                      </td>
                      <td className="px-5 py-3">
                        <span className="text-slate-300">{s.cases_count ?? 0}</span>
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-1 text-slate-500 text-xs">
                          <Clock className="w-3 h-3" />
                          {s.created_at ? formatDate(s.created_at) : '—'}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
