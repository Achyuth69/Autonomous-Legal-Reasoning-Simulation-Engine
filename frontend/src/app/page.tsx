'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, Scale, FileText, List } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import { casesApi, CaseResponse } from '@/lib/api';
import { formatDate, getStatusColor } from '@/lib/utils';

export default function Home() {
  const router = useRouter();
  const [cases, setCases] = useState<CaseResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      const data = await casesApi.listCases();
      setCases(data);
    } catch (error) {
      console.error('Error loading cases:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCaseCreated = (caseData: CaseResponse) => {
    setCases([caseData, ...cases]);
    setShowUpload(false);
    router.push(`/cases/${caseData.id}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-legal-darker via-legal-dark to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-800 bg-legal-darker/50 backdrop-blur-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Scale className="w-8 h-8 text-legal-gold" />
              <div>
                <h1 className="text-2xl font-bold text-white">
                  Autonomous Legal Reasoning Engine
                </h1>
                <p className="text-sm text-gray-400">
                  AI-Powered Multi-Agent Legal Analysis
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowUpload(!showUpload)}
              className="flex items-center gap-2 px-6 py-3 bg-legal-gold text-legal-darker font-semibold rounded-lg hover:bg-yellow-400 transition-colors"
            >
              <Upload className="w-5 h-5" />
              New Case
            </button>
            <a
              href="/knowledge-base"
              className="flex items-center gap-2 px-4 py-3 bg-gray-700 text-gray-200 font-semibold rounded-lg hover:bg-gray-600 transition-colors"
            >
              Knowledge Base
            </a>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Upload Section */}
        {showUpload && (
          <div className="mb-8 animate-in slide-in-from-top">
            <FileUpload onCaseCreated={handleCaseCreated} />
          </div>
        )}

        {/* Welcome Section */}
        {cases.length === 0 && !loading && !showUpload && (
          <div className="text-center py-20">
            <Scale className="w-24 h-24 text-legal-gold mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-white mb-4">
              Welcome to Legal Reasoning Engine
            </h2>
            <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
              Upload a legal document to begin autonomous multi-agent analysis.
              Our AI agents will extract facts, research applicable law, 
              generate arguments, and simulate judicial reasoning.
            </p>
            <button
              onClick={() => setShowUpload(true)}
              className="px-8 py-4 bg-legal-gold text-legal-darker font-semibold rounded-lg hover:bg-yellow-400 transition-colors text-lg"
            >
              Upload Your First Case
            </button>

            {/* Feature Cards */}
            <div className="grid md:grid-cols-3 gap-6 mt-16 max-w-5xl mx-auto">
              <div className="p-6 bg-gray-800/50 rounded-lg border border-gray-700">
                <FileText className="w-12 h-12 text-legal-gold mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  Document Processing
                </h3>
                <p className="text-gray-400">
                  Upload PDF, DOCX, or text files. OCR support for scanned documents.
                </p>
              </div>
              <div className="p-6 bg-gray-800/50 rounded-lg border border-gray-700">
                <Scale className="w-12 h-12 text-legal-gold mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  AI Agents
                </h3>
                <p className="text-gray-400">
                  10 specialized agents collaborate to analyze your case from every angle.
                </p>
              </div>
              <div className="p-6 bg-gray-800/50 rounded-lg border border-gray-700">
                <List className="w-12 h-12 text-legal-gold mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  Comprehensive Reports
                </h3>
                <p className="text-gray-400">
                  Get detailed analysis with citations, arguments, and judicial opinions.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Cases List */}
        {cases.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <List className="w-6 h-6" />
              Your Cases
            </h2>
            <div className="grid gap-4">
              {cases.map((caseItem) => (
                <div
                  key={caseItem.id}
                  onClick={() => router.push(`/cases/${caseItem.id}`)}
                  className="p-6 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-legal-gold transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold text-white">
                          {caseItem.title}
                        </h3>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                            caseItem.status
                          )}`}
                        >
                          {caseItem.status}
                        </span>
                      </div>
                      <p className="text-gray-400 text-sm mb-2">
                        Case Number: {caseItem.case_number}
                      </p>
                      <p className="text-gray-500 text-sm">
                        Created: {formatDate(caseItem.created_at)}
                      </p>
                    </div>
                    <FileText className="w-8 h-8 text-gray-600" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-legal-gold mx-auto"></div>
            <p className="text-gray-400 mt-4">Loading cases...</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-20">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-gray-500 text-sm">
            © 2024 Autonomous Legal Reasoning Engine. For educational purposes only.
            Not a substitute for professional legal advice.
          </p>
        </div>
      </footer>
    </div>
  );
}
