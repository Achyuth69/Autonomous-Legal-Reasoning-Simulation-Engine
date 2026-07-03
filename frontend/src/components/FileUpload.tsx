'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X } from 'lucide-react';
import { casesApi, CaseResponse } from '@/lib/api';

interface FileUploadProps {
  onCaseCreated: (caseData: CaseResponse) => void;
}

export default function FileUpload({ onCaseCreated }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setTitle(acceptedFiles[0].name);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: false,
  });

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const caseData = await casesApi.uploadCase(selectedFile, title);
      onCaseCreated(caseData);
      setSelectedFile(null);
      setTitle('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Upload Legal Document</h2>

      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-legal-gold bg-legal-gold/10'
              : 'border-gray-600 hover:border-gray-500'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          {isDragActive ? (
            <p className="text-gray-300 text-lg">Drop the file here...</p>
          ) : (
            <div>
              <p className="text-gray-300 text-lg mb-2">
                Drag & drop a legal document here, or click to select
              </p>
              <p className="text-gray-500 text-sm">
                Supported formats: PDF, DOCX, TXT (Max 10MB)
              </p>
            </div>
          )}
        </div>
      ) : (
        <div>
          <div className="flex items-center gap-4 p-4 bg-gray-700/50 rounded-lg mb-4">
            <FileText className="w-10 h-10 text-legal-gold" />
            <div className="flex-1">
              <p className="text-white font-medium">{selectedFile.name}</p>
              <p className="text-gray-400 text-sm">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              className="p-2 hover:bg-gray-600 rounded transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Case Title (Optional)
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-legal-gold"
              placeholder="Enter a custom title for this case"
            />
          </div>

          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full px-6 py-3 bg-legal-gold text-legal-darker font-semibold rounded-lg hover:bg-yellow-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-legal-darker"></div>
                Processing...
              </span>
            ) : (
              'Start Analysis'
            )}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-900/20 border border-red-800 rounded-lg">
          <p className="text-red-400">{error}</p>
        </div>
      )}
    </div>
  );
}
