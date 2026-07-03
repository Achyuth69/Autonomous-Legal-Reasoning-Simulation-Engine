'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Scale, Key, ChevronRight, CheckCircle, Loader2, ExternalLink, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { sessionsApi, ProviderInfo } from '@/lib/api';

const PROVIDER_ICONS: Record<string, string> = {
  groq: '⚡', openai: '🤖', gemini: '✨', anthropic: '🔮',
  mistral: '💨', cohere: '🌊', together: '🤝', ollama: '🦙',
};
const PROVIDER_COLORS: Record<string, string> = {
  groq: 'border-orange-500/40 bg-orange-900/10',
  openai: 'border-green-500/40 bg-green-900/10',
  gemini: 'border-blue-500/40 bg-blue-900/10',
  anthropic: 'border-purple-500/40 bg-purple-900/10',
  mistral: 'border-cyan-500/40 bg-cyan-900/10',
  cohere: 'border-pink-500/40 bg-pink-900/10',
  together: 'border-yellow-500/40 bg-yellow-900/10',
  ollama: 'border-gray-500/40 bg-gray-900/10',
};

export default function SetupPage() {
  const router = useRouter();
  const [providers, setProviders] = useState<Record<string, ProviderInfo>>({});
  const [selectedProvider, setSelectedProvider] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('');
  const [userName, setUserName] = useState('');
  const [baseUrl, setBaseUrl] = useState('http://localhost:11434');
  const [showKey, setShowKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    sessionsApi.listProviders().then(setProviders).catch(() => {});
    // Pre-fill if already configured
    const saved = localStorage.getItem('lexai_session');
    if (saved) {
      try {
        const s = JSON.parse(saved);
        if (s.session_id) {
          router.replace('/');
        }
      } catch {}
    }
  }, []);

  const providerInfo = selectedProvider ? providers[selectedProvider] : null;

  const handleProviderSelect = (key: string) => {
    setSelectedProvider(key);
    setModel(providers[key]?.default_model || '');
    setApiKey('');
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProvider) { setError('Select a provider'); return; }
    if (!apiKey && selectedProvider !== 'ollama') { setError('Enter your API key'); return; }
    if (!model) { setError('Select a model'); return; }

    setValidating(true);
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const session = await sessionsApi.createSession({
        provider: selectedProvider,
        api_key: selectedProvider === 'ollama' ? 'ollama' : apiKey,
        model,
        user_name: userName || 'User',
        base_url: selectedProvider === 'ollama' ? baseUrl : undefined,
      });

      localStorage.setItem('lexai_session', JSON.stringify(session));
      setSuccess(`✓ ${session.message}`);
      setTimeout(() => router.push('/'), 1200);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Validation failed');
    } finally {
      setLoading(false);
      setValidating(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-base flex flex-col">
      {/* Header */}
      <header className="border-b border-surface-border bg-surface-base/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand/20 border border-brand/30 flex items-center justify-center">
            <Scale className="w-4 h-4 text-brand-light" />
          </div>
          <span className="font-semibold text-slate-100 text-sm">LexAI</span>
          <span className="text-slate-500 text-sm">· API Setup</span>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-12">
        {/* Title */}
        <div className="text-center mb-10">
          <div className="w-16 h-16 rounded-2xl bg-brand/15 border border-brand/25 flex items-center justify-center mx-auto mb-4">
            <Key className="w-8 h-8 text-brand-light" />
          </div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Choose Your AI Provider</h1>
          <p className="text-slate-400 text-base">
            LexAI works with any LLM provider. Pick one, paste your API key, and start analysing cases.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Step 1 — Provider Grid */}
          <div>
            <h2 className="text-slate-300 font-semibold mb-3 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-brand/20 text-brand-light text-xs flex items-center justify-center font-bold">1</span>
              Select Provider
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {Object.entries(providers).map(([key, info]) => (
                <button type="button" key={key} onClick={() => handleProviderSelect(key)}
                  className={`p-4 rounded-xl border-2 transition-all text-left ${
                    selectedProvider === key
                      ? `${PROVIDER_COLORS[key] || 'border-brand/40 bg-brand/10'} border-opacity-100`
                      : 'border-surface-border hover:border-slate-600 bg-surface-raised'
                  }`}>
                  <div className="text-2xl mb-1">{PROVIDER_ICONS[key] || '🤖'}</div>
                  <div className="text-slate-200 font-medium text-sm">{info.label}</div>
                  {info.free && (
                    <span className="badge badge-success text-xs mt-1">Free</span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {selectedProvider && providerInfo && (
            <>
              {/* Step 2 — Model */}
              <div>
                <h2 className="text-slate-300 font-semibold mb-3 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-brand/20 text-brand-light text-xs flex items-center justify-center font-bold">2</span>
                  Choose Model
                </h2>
                <select value={model} onChange={e => setModel(e.target.value)}
                  className="w-full bg-surface-overlay border border-surface-border rounded-xl px-4 py-3 text-slate-200 focus:border-brand/50 focus:outline-none">
                  {providerInfo.models.map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>

              {/* Step 3 — API Key */}
              <div>
                <h2 className="text-slate-300 font-semibold mb-3 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-brand/20 text-brand-light text-xs flex items-center justify-center font-bold">3</span>
                  {selectedProvider === 'ollama' ? 'Local URL' : 'API Key'}
                  <a href={providerInfo.url} target="_blank"
                    className="ml-auto text-brand-light text-xs flex items-center gap-1 hover:underline">
                    Get key <ExternalLink className="w-3 h-3" />
                  </a>
                </h2>
                {selectedProvider === 'ollama' ? (
                  <input value={baseUrl} onChange={e => setBaseUrl(e.target.value)}
                    className="w-full bg-surface-overlay border border-surface-border rounded-xl px-4 py-3 text-slate-200 focus:border-brand/50 focus:outline-none font-mono text-sm"
                    placeholder="http://localhost:11434" />
                ) : (
                  <div className="relative">
                    <input
                      type={showKey ? 'text' : 'password'}
                      value={apiKey}
                      onChange={e => setApiKey(e.target.value)}
                      placeholder={`Paste your ${providerInfo.label} API key`}
                      className="w-full bg-surface-overlay border border-surface-border rounded-xl px-4 py-3 pr-12 text-slate-200 focus:border-brand/50 focus:outline-none font-mono text-sm"
                    />
                    <button type="button" onClick={() => setShowKey(!showKey)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 p-1">
                      {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                )}
              </div>

              {/* Step 4 — Name */}
              <div>
                <h2 className="text-slate-300 font-semibold mb-3 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-brand/20 text-brand-light text-xs flex items-center justify-center font-bold">4</span>
                  Your Name <span className="text-slate-500 font-normal text-sm">(optional)</span>
                </h2>
                <input value={userName} onChange={e => setUserName(e.target.value)}
                  placeholder="e.g. Arjun Rao"
                  className="w-full bg-surface-overlay border border-surface-border rounded-xl px-4 py-3 text-slate-200 focus:border-brand/50 focus:outline-none" />
              </div>
            </>
          )}

          {/* Errors / Success */}
          {error && (
            <div className="p-4 bg-rose-900/15 border border-rose-800/40 rounded-xl flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <p className="text-rose-300 text-sm">{error}</p>
            </div>
          )}
          {success && (
            <div className="p-4 bg-emerald-900/15 border border-emerald-800/40 rounded-xl flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <p className="text-emerald-300 text-sm">{success}</p>
            </div>
          )}

          {/* Submit */}
          <button type="submit" disabled={loading || !selectedProvider}
            className="btn-primary w-full justify-center py-3.5 text-base disabled:opacity-40">
            {loading ? (
              <><Loader2 className="w-5 h-5 animate-spin" />{validating ? 'Validating API key…' : 'Setting up…'}</>
            ) : (
              <>Start Analysing Cases <ChevronRight className="w-5 h-5" /></>
            )}
          </button>
        </form>

        <p className="text-center text-slate-600 text-xs mt-8">
          Your API key is validated once then stored locally. It is sent to the backend only to make LLM calls.
        </p>
      </main>
    </div>
  );
}
