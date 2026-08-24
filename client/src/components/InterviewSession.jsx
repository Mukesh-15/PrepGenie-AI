import React, { useState, useEffect } from 'react';
import axios from 'axios';
import EvaluationCard from './EvaluationCard';

export default function InterviewSession({ interviewData, onGenerateReport }) {
  const { interviewId, resumeFileName } = interviewData;
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [loadingQ, setLoadingQ] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [qCount, setQCount] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => { fetchNext(); }, []);

  const fetchNext = async () => {
    setLoadingQ(true); setEvaluation(null); setAnswer(''); setError(null);
    try {
      const res = await axios.post(`/api/interviews/${interviewId}/question`);
      setCurrentQuestion(res.data); setQCount(c => c + 1);
    } catch (e) { setError(e.response?.data?.detail || 'Failed to generate question'); }
    finally { setLoadingQ(false); }
  };

  const submitAnswer = async (e) => {
    e.preventDefault();
    if (!answer.trim()) return;
    setSubmitting(true); setError(null);
    try {
      const res = await axios.post(`/api/interviews/${interviewId}/answer`, { questionId: currentQuestion.questionId, answer: answer.trim() });
      setEvaluation(res.data);
    } catch (e) { setError(e.response?.data?.detail || 'Failed to evaluate answer'); }
    finally { setSubmitting(false); }
  };

  const diffBadge = (d) => {
    const v = (d || 'medium').toLowerCase();
    if (v === 'easy') return <span className="badge badge-green">Easy</span>;
    if (v === 'hard') return <span className="badge badge-red">Hard</span>;
    return <span className="badge badge-amber">Medium</span>;
  };

  return (
    <div style={{ padding: '24px 0 48px' }}>

      {/* Top bar */}
      <div className="card" style={{ padding: '12px 20px', marginBottom: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 13, color: '#374151', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '60%' }}>
          {resumeFileName}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
          <span style={{ fontSize: 11, fontWeight: 600, background: '#FFF7ED', color: '#EA580C', border: '1px solid #FED7AA', borderRadius: 99, padding: '3px 12px' }}>
            Q {qCount}
          </span>
          <button onClick={() => onGenerateReport(interviewId)} className="btn btn-ghost" style={{ padding: '6px 14px', fontSize: 12 }}>
            End Interview
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{ marginBottom: 16, padding: '10px 16px', borderRadius: 8, background: '#FEF2F2', border: '1px solid #FECACA', color: '#DC2626', fontSize: 13, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {error}
          <button onClick={fetchNext} style={{ fontSize: 12, textDecoration: 'underline', color: '#DC2626', background: 'none', border: 'none', cursor: 'pointer' }}>Retry</button>
        </div>
      )}

      {/* Loading */}
      {loadingQ && (
        <div className="card" style={{ padding: '56px 24px', textAlign: 'center' }}>
          <div className="spinner" style={{ color: '#F97316', margin: '0 auto 14px' }} />
          <p style={{ fontSize: 14, fontWeight: 500, color: '#374151' }}>Generating question from your resume...</p>
          <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4 }}>Fetching relevant context via RAG</p>
        </div>
      )}

      {/* Question card */}
      {!loadingQ && currentQuestion && (
        <div className="card" style={{ padding: '24px', boxShadow: '0 4px 16px rgba(249,115,22,0.08)', marginBottom: 16 }}>
          {/* Meta row */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="badge badge-orange">{currentQuestion.category || 'General'}</span>
              {diffBadge(currentQuestion.difficulty)}
            </div>
            <span style={{ fontSize: 11, color: '#9CA3AF' }}>Resume-grounded</span>
          </div>

          {/* Question */}
          <p style={{ fontSize: 16, fontWeight: 600, color: '#111827', lineHeight: 1.55, marginBottom: 20 }}>
            {currentQuestion.question}
          </p>

          {/* RAG context */}
          {currentQuestion.contextUsed && (
            <details style={{ marginBottom: 20 }}>
              <summary style={{ fontSize: 12, color: '#9CA3AF', cursor: 'pointer', userSelect: 'none' }}>
                View resume context ↓
              </summary>
              <div style={{ marginTop: 8, padding: '10px 12px', background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: 8, fontSize: 11, color: '#6B7280', fontFamily: 'monospace', maxHeight: 120, overflowY: 'auto', lineHeight: 1.6 }}>
                {currentQuestion.contextUsed}
              </div>
            </details>
          )}

          {/* Answer or submitted view */}
          {!evaluation ? (
            <form onSubmit={submitAnswer}>
              <textarea
                rows={5}
                value={answer}
                onChange={e => setAnswer(e.target.value)}
                placeholder="Type your answer here..."
                disabled={submitting}
                style={{
                  width: '100%', padding: '12px 14px',
                  background: '#FAFAFA', border: '1.5px solid #E5E7EB',
                  borderRadius: 8, fontSize: 14, color: '#111827',
                  resize: 'vertical', outline: 'none',
                  fontFamily: 'Inter, sans-serif', lineHeight: 1.65,
                  transition: 'border-color 0.15s'
                }}
                onFocus={e => e.target.style.borderColor = '#F97316'}
                onBlur={e => e.target.style.borderColor = '#E5E7EB'}
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 12 }}>
                <button type="submit" disabled={!answer.trim() || submitting} className="btn btn-primary" style={{ padding: '9px 20px' }}>
                  {submitting ? <><div className="spinner text-white" /><span>Evaluating...</span></> : 'Submit Answer →'}
                </button>
              </div>
            </form>
          ) : (
            <div style={{ padding: '12px 14px', background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: 8 }}>
              <p style={{ fontSize: 11, fontWeight: 600, color: '#9CA3AF', textTransform: 'uppercase', marginBottom: 6 }}>Your Answer</p>
              <p style={{ fontSize: 13, color: '#374151', lineHeight: 1.65, fontStyle: 'italic' }}>{answer}</p>
            </div>
          )}
        </div>
      )}

      {/* Evaluation */}
      {evaluation && (
        <EvaluationCard evaluation={evaluation} onNextQuestion={fetchNext} onFinishInterview={() => onGenerateReport(interviewId)} />
      )}
    </div>
  );
}
