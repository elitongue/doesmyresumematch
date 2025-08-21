'use client';

import type { GapItem } from '@doesmyresumematch/shared';

export default function GapsList({ gaps }: { gaps: GapItem[] }) {
  return (
    <ul className="space-y-1">
      {gaps.map((g) => (
        <li key={g.skill} className="flex items-center">
          {g.required && <span className="text-red-500 mr-2">*</span>}
          <span>{g.skill}</span>
        </li>
      ))}
    </ul>
  );
}
