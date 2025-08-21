import Link from 'next/link';

export default function TrustBox() {
  return (
    <div className="p-4 bg-gray-100 rounded text-sm space-y-3">
      <div>
        <h3 className="font-semibold">How we score</h3>
        <p>
          We compare your resume and job using cosine similarity with penalties.
          Skills are grouped into clusters, and required skills matter more.
        </p>
      </div>
      <div>
        <h3 className="font-semibold">Privacy</h3>
        <p>
          By default we keep nothing. You can opt in to save your results and delete
          them later with one click.
        </p>
      </div>
      <div>
        <h3 className="font-semibold">Accuracy</h3>
        <p>Use this as guidance, not a guarantee.</p>
      </div>
      <div className="flex space-x-4">
        <Link href="/about" className="underline">
          About
        </Link>
        <Link href="/privacy" className="underline">
          Privacy
        </Link>
      </div>
    </div>
  );
}

