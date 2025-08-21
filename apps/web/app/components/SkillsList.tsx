'use client';

import type { SkillItem } from '@doesmyresumematch/shared';

export default function SkillsList({ skills }: { skills: SkillItem[] }) {
  return (
    <ul className="space-y-1">
      {skills.map((s) => {
        const e = s.evidence || {};
        const title =
          e.tenure_years !== undefined
            ? `Tenure: ${e.tenure_years.toFixed(1)} yrs, last used ${e.months_since_last_use} mo ago`
            : undefined;
        return (
          <li key={s.skill} title={title} className="flex justify-between">
            <span>{s.skill}</span>
            <span className="text-gray-500 text-sm">
              {s.contribution.toFixed(2)}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
