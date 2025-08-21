'use client';

import type { ClusterAlignment } from '@doesmyresumematch/shared';

export default function ClusterBars({
  clusters,
}: {
  clusters: ClusterAlignment[];
}) {
  return (
    <div className="space-y-2">
      {clusters.map((c) => (
        <div key={c.cluster}>
          <div className="text-sm mb-1">{c.cluster}</div>
          <div className="w-full h-2 bg-gray-200 rounded">
            <div
              className="h-2 bg-blue-500 rounded"
              style={{ width: `${c.align_pct.toFixed(0)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
