import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

export default function UploadResume({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (files) => {
      if (files[0]?.type !== 'application/pdf') return setError('Please upload a PDF file.');
      setFile(files[0]); setError(null);
    },
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false
  });

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true); setError(null);
    const form = new FormData();
    form.append('resume', file);
    try {
      const res = await axios.post('/api/interviews/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } });
      onUploadSuccess(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to process resume. Try again.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto py-10">
      {/* Header */}
      <div className="text-center mb-8">
        <div style={{ width: 48, height: 48, borderRadius: 14, background: 'linear-gradient(135deg, #F97316, #EA580C)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', boxShadow: '0 4px 14px rgba(249,115,22,0.35)' }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>
        </div>
        <h1 className="font-bold text-gray-900 mb-1" style={{ fontSize: 22, letterSpacing: '-0.4px' }}>AI Technical Interview</h1>
        <p className="text-sm text-gray-500">Upload your resume to get personalized adaptive questions</p>
      </div>

      {/* Card */}
      <div className="card p-6" style={{ boxShadow: '0 4px 20px rgba(249,115,22,0.08)' }}>
        {/* Dropzone */}
        <div {...getRootProps()} style={{
          border: `2px dashed ${isDragActive ? '#F97316' : file ? '#A3E635' : '#D1D5DB'}`,
          borderRadius: 10, padding: '28px 20px', textAlign: 'center', cursor: 'pointer',
          background: isDragActive ? '#FFF7ED' : file ? '#F7FEE7' : '#FAFAFA',
          transition: 'all 0.2s'
        }}>
          <input {...getInputProps()} />
          {file ? (
            <>
              <p className="font-semibold text-gray-800 text-sm">{file.name}</p>
              <p className="text-xs text-gray-400 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB • Click to replace</p>
            </>
          ) : (
            <>
              <p className="text-sm font-medium text-gray-700">{isDragActive ? 'Drop here...' : 'Click to upload or drag & drop'}</p>
              <p className="text-xs text-gray-400 mt-1">PDF only, max 10MB</p>
            </>
          )}
        </div>

        {error && <p className="text-xs text-red-600 mt-3 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>}

        <button onClick={handleUpload} disabled={!file || loading} className="btn btn-primary w-full mt-4" style={{ padding: '10px 0', fontSize: 14 }}>
          {loading ? <><div className="spinner text-white" /><span>Processing Resume...</span></> : 'Start Interview →'}
        </button>
      </div>

    </div>
  );
}
