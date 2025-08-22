'use client';

import { useCallback, useRef, useState } from 'react';

interface Props {
  onFile: (file: File) => void;
}

export default function DragAndDrop({ onFile }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState('');

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files || files.length === 0) return;
      const file = files[0];
      onFile(file);
      setUploadedFileName(file.name);
    },
    [onFile],
  );

  return (
    <div
      className="flex flex-col items-center justify-center p-6 border-2 border-dashed rounded cursor-pointer text-center text-sm text-gray-500 hover:border-blue-400"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
    >
      {uploadedFileName ? (
        <p className="text-green-600">Uploaded: {uploadedFileName}</p>
      ) : (
        <p>Drag & drop resume PDF or click to select</p>
      )}
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.doc,.docx"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}
