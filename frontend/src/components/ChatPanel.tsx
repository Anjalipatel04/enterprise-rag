"use client";

import { Loader2, Send } from "lucide-react";
import { useState } from "react";
import { sendQuestion, type ChatResponse } from "@/lib/api";
import { Citations } from "./Citations";

type Message = {
  role: "user" | "assistant";
  content: string;
  result?: ChatResponse;
};

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Upload enterprise documents, then ask a question. Answers are grounded in retrieved sources." }
  ]);
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;
    setQuestion("");
    setError(null);
    setMessages((current) => [...current, { role: "user", content: trimmed }]);
    setLoading(true);
    try {
      const result = await sendQuestion(trimmed, topK);
      setMessages((current) => [...current, { role: "assistant", content: result.answer, result }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="flex min-h-0 flex-1 flex-col">
      <div className="flex-1 overflow-y-auto px-5 py-5">
        <div className="mx-auto max-w-4xl space-y-4">
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} className={message.role === "user" ? "ml-auto max-w-2xl bg-ink p-4 text-white" : "mr-auto max-w-3xl border border-line bg-white p-4"}>
              <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
              {message.result && <Citations citations={message.result.citations} />}
            </div>
          ))}
          {loading && (
            <div className="inline-flex items-center gap-2 border border-line bg-white px-4 py-3 text-sm text-slate-700">
              <Loader2 className="animate-spin" size={18} />
              Retrieving, reranking, and grounding answer
            </div>
          )}
          {error && <div className="border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">{error}</div>}
        </div>
      </div>
      <form onSubmit={submit} className="border-t border-line bg-white px-5 py-4">
        <div className="mx-auto flex max-w-4xl gap-3">
          <label className="w-20 text-sm font-medium text-ink">
            Top K
            <input className="mt-1 w-full border border-line px-2 py-2" type="number" min={1} max={20} value={topK} onChange={(event) => setTopK(Number(event.target.value))} />
          </label>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a question about the uploaded documents"
            className="min-h-14 flex-1 resize-none border border-line px-3 py-3 text-sm outline-none focus:border-accent"
          />
          <button type="submit" disabled={loading} className="inline-flex h-14 w-14 items-center justify-center bg-accent text-white disabled:opacity-60" title="Send question">
            <Send size={20} />
          </button>
        </div>
      </form>
    </section>
  );
}
