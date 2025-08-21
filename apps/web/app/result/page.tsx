'use client';

import { useEffect, useState } from 'react';
import LoadingState from '../components/LoadingState';
import ScoreDial from '../components/ScoreDial';
import SkillsList from '../components/SkillsList';
import GapsList from '../components/GapsList';
import ClusterBars from '../components/ClusterBars';
import TrustBox from '../components/TrustBox';
import type { ScoreResponse } from '@doesmyresumematch/shared';

export default function ResultPage() {
  const [id, setId] = useState<string | null>(null);
  const [data, setData] = useState<ScoreResponse | null>(null);
  const [showRewrites, setShowRewrites] = useState(false);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
  const ANALYTICS_ENABLED = process.env.NEXT_PUBLIC_ANALYTICS_ENABLED === '1';

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setId(params.get('id'));
  }, []);

  useEffect(() => {
    if (!id) return;
    const stored =
      typeof window !== 'undefined' ? localStorage.getItem(`match-${id}`) : null;
    if (stored) {
      setData(JSON.parse(stored) as ScoreResponse);
    }
  }, [id]);

  useEffect(() => {
    if (!data || !ANALYTICS_ENABLED) return;
    fetch(`${API_BASE}/v1/metrics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event: 'match_completed', score: data.score }),
    });
  }, [data, ANALYTICS_ENABLED, API_BASE]);

  if (!id || !data) return <LoadingState />;

  const handleExport = async () => {
    const res = await fetch(`/api/snapshot/${id}`);
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `doesmyresumematch-${id}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-6">
      <div className="flex justify-end">
        <button
          onClick={handleExport}
          className="px-4 py-2 bg-green-600 text-white rounded"
        >
          Export PDF
        </button>
      </div>
      <ScoreDial score={data.score} label={data.label} />
      <div>
        <h2 className="font-semibold mb-2">Best-fit skills</h2>
        <SkillsList skills={data.best_fit} />
      </div>
      <div>
        <h2 className="font-semibold mb-2">Gaps</h2>
        <GapsList gaps={data.gaps} />
      </div>
      <div>
        <h2 className="font-semibold mb-2">Cluster alignment</h2>
        <ClusterBars clusters={data.clusters} />
      </div>
      {data.rewrites && data.rewrites.length > 0 && (
        <div>
          <button
            onClick={() => setShowRewrites((s) => !s)}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
          >
            Try improved bullets
          </button>
          {showRewrites && (
            <ul className="mt-2 list-disc pl-5 space-y-1">
              {data.rewrites.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          )}
        </div>
      )}
      <TrustBox />
    </div>
  );
}
