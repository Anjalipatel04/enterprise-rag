"use client";

import { Database, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { ChatPanel } from "@/components/ChatPanel";
import { FileUpload } from "@/components/FileUpload";
import type { UploadResponse } from "@/lib/api";

export default function Home() {
  const [uploads, setUploads] = useState<UploadResponse[]>([]);

  return (
    <main className="flex h-screen flex-col overflow-hidden">
      <header className="border-b border-line bg-white px-5 py-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="text-xl font-semibold text-ink">Enterprise Document QA</h1>
            <p className="text-sm text-slate-600">Hybrid retrieval, reranking, Gemini, and grounded citations.</p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs font-medium text-slate-700">
            <span className="inline-flex items-center gap-1 border border-line px-2 py-1"><Database size={14} /> Qdrant HNSW</span>
            <span className="inline-flex items-center gap-1 border border-line px-2 py-1"><ShieldCheck size={14} /> Guardrails</span>
          </div>
        </div>
      </header>
      <FileUpload onUploaded={(items) => setUploads((current) => [...items, ...current])} />
      {uploads.length > 0 && (
        <div className="border-b border-line bg-panel px-5 py-2 text-xs text-slate-700">
          {uploads.map((item) => `${item.filename}: ${item.chunks_indexed} chunks`).join(" · ")}
        </div>
      )}
      <ChatPanel />
    </main>
  );
}
