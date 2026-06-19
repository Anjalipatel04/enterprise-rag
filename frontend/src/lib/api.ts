export type Citation = {
  document_id: string;
  filename: string;
  chunk_id: string;
  page: number | null;
  heading: string | null;
  score: number;
  text: string;
};

export type ChatResponse = {
  answer: string;
  citations: Citation[];
  grounded: boolean;
  refused: boolean;
};

export type UploadResponse = {
  document_id: string;
  filename: string;
  chunks_indexed: number;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function uploadFiles(files: File[], chunkSize: number, chunkOverlap: number): Promise<UploadResponse[]> {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));
  form.append("chunk_size", String(chunkSize));
  form.append("chunk_overlap", String(chunkOverlap));

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: form
  });
  if (!response.ok) {
    throw new Error(await extractError(response));
  }
  return response.json();
}

export async function sendQuestion(question: string, topK: number): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK })
  });
  if (!response.ok) {
    throw new Error(await extractError(response));
  }
  return response.json();
}

async function extractError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    return typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
  } catch {
    return `Request failed with ${response.status}`;
  }
}
