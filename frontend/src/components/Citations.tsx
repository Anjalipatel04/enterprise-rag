import type { Citation } from "@/lib/api";

export function Citations({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  return (
    <div className="mt-4 space-y-3">
      <h3 className="text-sm font-semibold text-ink">Sources</h3>
      {citations.map((citation, index) => (
        <article key={citation.chunk_id} className="border border-line bg-white p-3">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-600">
            <span className="font-semibold text-ink">[{index + 1}] {citation.filename}</span>
            <span>score {citation.score.toFixed(3)}</span>
          </div>
          <p className="mb-2 text-xs text-slate-600">{citation.heading ?? "Document section"}{citation.page ? ` · page ${citation.page}` : ""}</p>
          <p className="line-clamp-4 text-sm leading-6 text-slate-800">{citation.text}</p>
        </article>
      ))}
    </div>
  );
}
