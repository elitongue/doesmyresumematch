'use client';

interface Props {
  score: number;
  label: string;
}

export default function ScoreDial({ score, label }: Props) {
  const pct = Math.round(score);
  const color =
    pct >= 85
      ? '#22c55e'
      : pct >= 70
        ? '#3b82f6'
        : pct >= 55
          ? '#eab308'
          : '#ef4444';
  const badgeClass =
    pct >= 85
      ? 'bg-green-500'
      : pct >= 70
        ? 'bg-blue-500'
        : pct >= 55
          ? 'bg-yellow-500'
          : 'bg-red-500';
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: `conic-gradient(${color} ${pct * 3.6}deg, #e5e7eb 0)`,
          }}
        />
        <div className="absolute inset-2 bg-white rounded-full flex items-center justify-center">
          <span className="text-3xl font-bold">{pct}</span>
        </div>
      </div>
      <span
        className={`mt-2 px-2 py-1 rounded text-white text-sm ${badgeClass}`}
      >
        {label}
      </span>
    </div>
  );
}
