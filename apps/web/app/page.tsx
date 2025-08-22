'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { siteTitle } from '@doesmyresumematch/shared';
import DragAndDrop from './components/DragAndDrop';
import TextArea from './components/TextArea';
import LoadingState from './components/LoadingState';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
const ANALYTICS_ENABLED = process.env.NEXT_PUBLIC_ANALYTICS_ENABLED === '1';

export default function Page() {
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState('');
  const [loading, setLoading] = useState(false);
  const [consent, setConsent] = useState(false);
  const [clientId, setClientId] = useState('');
  const router = useRouter();

  useEffect(() => {
    let cid = localStorage.getItem('client-id');
    if (!cid) {
      cid = Math.random().toString(36).slice(2);
      localStorage.setItem('client-id', cid);
    }
    setClientId(cid);
    if (ANALYTICS_ENABLED) {
      fetch(`${API_BASE}/v1/metrics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event: 'pageview' }),
      });
    }
  }, []);

  const handleSubmit = async () => {
    if (!file || !job) return;
    setLoading(true);
    try {
      const resumeRes = await fetch(`${API_BASE}/v1/parse/resume`, {
        method: 'POST',
        // Send the raw file so the browser sets the correct headers and payload
        body: file,
        headers: {
          'Content-Type': file.type || 'application/pdf',
          'X-Client-Id': clientId,
        },
      });
      const resumeData = await resumeRes.json();
      const jobRes = await fetch(`${API_BASE}/v1/parse/job`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Client-Id': clientId,
        },
        body: JSON.stringify({ source: job }),
      });
      const jobData = await jobRes.json();
      const matchRes = await fetch(`${API_BASE}/v1/match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Client-Id': clientId,
          'X-Consent-Save': String(consent),
        },
        body: JSON.stringify({
          resume_doc_id: resumeData.doc_id,
          job_doc_id: jobData.doc_id,
        }),
      });
      const matchData = await matchRes.json();
      const id = Date.now().toString();
      localStorage.setItem(`match-${id}`, JSON.stringify(matchData));
      router.push(`/result?id=${id}`);
    } catch (e) {
      console.error(e);
      alert('Request failed');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState />;

  return (
    <div className="max-w-xl mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-semibold text-center">{siteTitle}</h1>
      <DragAndDrop onFile={setFile} />
      <TextArea
        value={job}
        onChange={setJob}
        placeholder="Paste job description or URL"
      />
      <label className="flex items-center space-x-2">
        <input
          type="checkbox"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
        />
        <span>Allow saving my results for later</span>
      </label>
      <button
        onClick={handleSubmit}
        disabled={!file || !job}
        className="w-full bg-blue-500 text-white py-2 rounded disabled:opacity-50"
      >
        Analyze
      </button>
    </div>
  );
}
