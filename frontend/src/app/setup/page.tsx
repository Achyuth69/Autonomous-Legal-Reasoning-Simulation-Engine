'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Scale, Key, ChevronRight, CheckCircle, Loader2, ExternalLink, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { sessionsApi } from '@/lib/api';

/* ─── Static provider list (shown immediately, no API needed) ─── */
const STATIC_PROVIDERS: Record<string, { label: string; url: string; free: boolean; models: string[]; default_model: string }> = {
  groq:      { label: 'Groq',            url: 'https://console.groq.com',                    free: true,  models: ['llama-3.3-70b-versatile','llama-3.1-70b-versatile','llama-3.1-8b-instant','gemma2-9b-it','gemma-7b-it'],                                              default_model: 'llama-3.1-8b-instant' },
  openai:    { label: 'OpenAI',          url: 'https://platform.openai.com/api-keys',        free: false, models: ['gpt-4o','gpt-4o-mini','gpt-4-turbo','gpt-4','gpt-3.5-turbo','o1-mini'],                                                                              default_model: 'gpt-4o-mini' },
  gemini:    { label: 'Google Gemini',   url: 'https://aistudio.google.com/app/apikey',      free: true,  models: ['gemini-2.0-flash','gemini-1.5-flash','gemini-1.5-flash-8b','gemini-1.5-pro'],                                                                         default_model: 'gemini-1.5-flash' },
  anthropic: { label: 'Claude',          url: 'https://console.anthropic.com/keys',          free: false, models: ['claude-3-5-sonnet-20241022','claude-3-5-haiku-20241022','claude-3-opus-20240229','claude-3-haiku-20240307'],                                           default_model: 'claude-3-5-haiku-20241022' },
  mistral:   { label: 'Mistral',         url: 'https://console.mistral.ai/api-keys',         free: false, models: ['mistral-large-latest','mistral-small-latest','open-mixtral-8x22b','open-mistral-7b'],                                                                 default_model: 'mistral-small-latest' },
  cohere:    { label: 'Cohere',          url: 'https://dashboard.cohere.com/api-keys',       free: true,  models: ['command-r-plus','command-r','command','command-light'],                                                                                                default_model: 'command-r' },
  together:  { label: 'Together AI',     url: 'https://api.together.xyz/settings/api-keys',  free: false, models: ['meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo','meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo','mistralai/Mixtral-8x7B-Instruct-v0.1','Qwen/Qwen2.5-72B-Instruct-Turbo'], default_model: 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo' },
  ollama:    { label: 'Ollama (Local)',  url: 'https://ollama.com',                          free: true,  models: ['llama3.2','llama3.1','mistral','gemma2','qwen2.5','phi3.5','deepseek-r1'],                                                                             default_model: 'llama3.2' },
};

const ICONS: Record<string, string> = { groq:'⚡', openai:'🤖', gemini:'✨', anthropic:'🔮', mistral:'💨', cohere:'🌊', together:'🤝', ollama:'🦙' };
const COLORS: Record<string, string> = {
  groq:'border-orange-500 bg-orange-950/40', openai:'border-green-500 bg-green-950/40',
  gemini:'border-blue-500 bg-blue-950/40', anthropic:'border-purple-500 bg-purple-950/40',
  mistral:'border-cyan-500 bg-cyan-950/40', cohere:'border-pink-500 bg-pink-950/40',
  together:'border-yellow-500 bg-yellow-950/40', ollama:'border-slate-500 bg-slate-900/40',
};

export default function SetupPage() {
  const router = useRouter();
  const [provider, setProvider]     = useState('');
  const [apiKey, setApiKey]         = useState('');
  const [model, setModel]           = useState('');
  const [userName, setUserName]     = useState('');
  const [baseUrl, setBaseUrl]       = useState('http://localhost:11434');
  const [showKey, setShowKey]       = useState(false);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState('');
  const [success, setSuccess]       = useState('');

  /* Redirect if already configured */
  useEffect(() => {
    const s = localStorage.getItem('lexai_session');
    if (s) { try { if (JSON.parse(s)?.session_id) { router.replace('/'); return; } } catch {} }
  }, []);

  const info = provider ? STATIC_PROVIDERS[provider] : null;

  const pick = (key: string) => {
    setProvider(key);
    setModel(STATIC_PROVIDERS[key].default_model);
    setApiKey(''); setError(''); setSuccess('');
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!provider)                                  { setError('Select a provider'); return; }
    if (!apiKey && provider !== 'ollama')           { setError('Enter your API key'); return; }
    if (!model)                                     { setError('Select a model'); return; }

    setLoading(true); setError(''); setSuccess('');
    try {
      const session = await sessionsApi.createSession({
        provider,
        api_key: provider === 'ollama' ? 'ollama' : apiKey,
        model,
        user_name: userName || 'User',
        base_url:  provider === 'ollama' ? baseUrl : undefined,
      });
      localStorage.setItem('lexai_session', JSON.stringify(session));
      setSuccess(`✓ ${session.message}`);
      setTimeout(() => router.push('/'), 1000);
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'API key validation failed');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-surface-base flex flex-col">
      {/* Header */}
      <header className="border-b border-surface-border">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-brand/20 border border-brand/30 flex items-center justify-center">
            <Scale className="w-3.5 h-3.5 text-brand-light"/>
          </div>
          <span className="font-semibold text-slate-200 text-sm">LexAI</span>
          <span className="text-slate-600 text-sm">· API Setup</span>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-10">
        {/* Hero */}
        <div className="text-center mb-10">
          <div className="w-14 h-14 rounded-2xl bg-brand/15 border border-brand/25 flex items-center justify-center mx-auto mb-4">
            <Key className="w-7 h-7 text-brand-light"/>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 mb-2">Choose Your AI Provider</h1>
          <p className="text-slate-400 text-sm max-w-md mx-auto">
            LexAI works with any LLM. Pick one, paste your API key, and start analysing cases.
          </p>
        </div>

        <form onSubmit={submit} className="space-y-7">

          {/* Step 1 — Provider grid */}
          <div>
            <p className="text-slate-300 font-semibold text-sm mb-3 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-brand/25 text-brand-light text-xs flex items-center justify-center font-bold">1</span>
              Select Provider
            </p>
            <div className="grid grid-cols-4 gap-2.5">
              {Object.entries(STATIC_PROVIDERS).map(([k, v]) => (
                <button type="button" key={k} onClick={() => pick(k)}
                  className={`p-3.5 rounded-xl border-2 text-left transition-all ${
                    provider === k
                      ? `${COLORS[k]} ring-1 ring-white/10`
                      : 'border-surface-border bg-surface-raised hover:border-slate-600'
                  }`}>
                  <div className="text-xl mb-1">{ICONS[k]}</div>
                  <div className="text-slate-200 font-medium text-xs leading-snug">{v.label}</div>
                  {v.free && <span className="text-emerald-400 text-xs">Free</span>}
                </button>
              ))}
            </div>
          </div>

          {info && (
            <>
              {/* Step 2 — Model */}
              <div>
                <p className="text-slate-300 font-semibold text-sm mb-2 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-brand/25 text-brand-light text-xs flex items-center justify-center font-bold">2</span>
                  Select Model
                </p>
                <select value={model} onChange={e => setModel(e.target.value)}
                  className="w-full bg-surface-overlay border border-surface-border rounded-xl px-4 py-3 text-slate-200 text-sm focus:border-brand/50 focus:outline-none">
                  {info.models.map(m => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>

              {/* Step 3 — API Key */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-slate-300 font-semibold text-sm flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-brand/25 text-brand-light text-xs flex items-center justify-center font-bold">3</span>
                    {provider === 'ollama' ? 'Ollama Server URL' : 'API Key'}
                  </p>
                  <a href={info.url} target="_blank" className="text-brand-light text-xs flex items-center gap-1 hover:underline">
                    Get key <ExternalLink className="w-3 h-3"/>
                  </a>
                </div>
                {provider === 'ollama' ? (
                  <input value={baseUrl} onChange={e => setBaseUrl(e.target.value)}
                    className="w-full bg-surface-overlay border border-surface-border rounded-xl px-4 py-3 text-slate-200 text-sm font-mono focus:border-brand/50 focus:outline-none"
                    placeholder="http://localhost:11434"/>
                ) : (
                  <div className="relative">
                    <input type={showKey ? 'text' : 'password'} value={apiKey}
                      onChange={e => setApiKey(e.target.value)}
                      placeholder={`Paste your ${info.label} API key`}
                      className="w-full bg-surface-overlay border border-surface-border rounded-xl px-4 py-3 pr-11 text-slate-200 text-sm font-mono focus:border-brand/50 focus:outline-none"/>
                    <button type="button" onClick={() => setShowKey(!showKey)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 p-1">
                      {showKey ? <EyeOff className="w-4 h-4"/> : <Eye className="w-4 h-4"/>}
                    </button>
                  </div>
                )}
              </div>

              {/* Step 4 — Name (optional) */}
              <div>
                <p className="text-slate-300 font-semibold text-sm mb-2 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-brand/25 text-brand-light text-xs flex items-center justify-center font-bold">4</span>
                  Your Name <span className="text-slate-600 font-normal">(optional)</span>
                </p>
                <input value={userName} onChange={e => setUserName(e.target.value)}
                  placeholder="e.g. Arjun Rao"
                  className="w-full bg-surface-overlay border border-surface-border rounded-xl px-4 py-3 text-slate-200 text-sm focus:border-brand/50 focus:outline-none"/>
              </div>
            </>
          )}

          {/* Feedback */}
          {error && (
            <div className="p-4 bg-rose-950/40 border border-rose-700/50 rounded-xl flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5"/>
              <p className="text-rose-300 text-sm">{error}</p>
            </div>
          )}
          {success && (
            <div className="p-4 bg-emerald-950/40 border border-emerald-700/50 rounded-xl flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5"/>
              <p className="text-emerald-300 text-sm">{success}</p>
            </div>
          )}

          {/* CTA */}
          <button type="submit" disabled={loading || !provider}
            className="btn-primary w-full justify-center py-3.5 text-sm disabled:opacity-40 disabled:cursor-not-allowed">
            {loading
              ? <><Loader2 className="w-4 h-4 animate-spin"/>Validating API key…</>
              : <>Start Analysing Cases <ChevronRight className="w-4 h-4"/></>}
          </button>
        </form>

        <p className="text-center text-slate-600 text-xs mt-6">
          Your key is validated once, stored locally, and sent to the backend only when making LLM calls.
        </p>
      </main>
    </div>
  );
}
