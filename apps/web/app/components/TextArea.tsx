'use client';

interface Props {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}

export default function TextArea({ value, onChange, placeholder }: Props) {
  return (
    <textarea
      className="w-full h-40 p-2 border rounded"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  );
}
