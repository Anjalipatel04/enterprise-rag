"use client";

import { FileText, Loader2, Upload } from "lucide-react";
import { useRef, useState } from "react";
import { uploadFiles, type UploadResponse } from "@/lib/api";

type Props = {
  onUploaded: (items: UploadResponse[]) => void;
};

export function FileUpload({ onUploaded }: Props) {
  const [files, setFiles] = useState<File[]>([]);
  const [chunkSize, setChunkSize] = useState(900);
  const [chunkOverlap, setChunkOverlap] = useState(120);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function submit() {
    if (!files.length) {
      setError("Choose at least one PDF, DOCX, or PPTX file.");
      return;
    }
    setIsUploading(true);
    setError(null);
    try {
      const uploaded = await uploadFiles(files, chunkSize, chunkOverlap);
      onUploaded(uploaded);
      setFiles([]);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="border-b border-line bg-white px-5 py-4">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="min-w-0 flex-1">
          <label className="mb-2 block text-sm font-semibold text-ink">Documents</label>
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="flex w-full items-center justify-center gap-2 border border-dashed border-line bg-panel px-4 py-5 text-sm font-medium text-ink hover:border-accent"
          >
            <Upload size={18} />
            Select PDF, DOCX, or PPTX files
          </button>
          <input
            ref={inputRef}
            className="hidden"
            type="file"
            multiple
            accept=".pdf,.docx,.pptx"
            onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
          />
          {files.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {files.map((file) => (
                <span key={file.name} className="inline-flex max-w-full items-center gap-1 border border-line bg-white px-2 py-1 text-xs">
                  <FileText size={14} />
                  <span className="truncate">{file.name}</span>
                </span>
              ))}
            </div>
          )}
        </div>

        <label className="text-sm font-medium text-ink">
          Chunk size
          <input className="mt-2 block w-28 border border-line px-3 py-2" type="number" value={chunkSize} min={200} max={3000} onChange={(e) => setChunkSize(Number(e.target.value))} />
        </label>
        <label className="text-sm font-medium text-ink">
          Overlap
          <input className="mt-2 block w-28 border border-line px-3 py-2" type="number" value={chunkOverlap} min={0} max={1000} onChange={(e) => setChunkOverlap(Number(e.target.value))} />
        </label>
        <button
          type="button"
          onClick={submit}
          disabled={isUploading}
          className="inline-flex h-10 items-center justify-center gap-2 bg-accent px-4 text-sm font-semibold text-white disabled:opacity-60"
        >
          {isUploading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
          Index
        </button>
      </div>
      {error && <p className="mt-3 text-sm font-medium text-red-700">{error}</p>}
    </section>
  );
}
