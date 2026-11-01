import { ParseResponse } from "@/types/resume";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function uploadAndParseResume(file: File): Promise<ParseResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/parse`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let errorMsg = `Upload failed with status ${res.status}`;
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export async function getResumeById(id: string): Promise<ParseResponse> {
  const res = await fetch(`${API_BASE}/api/resumes/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch resume: ${res.statusText}`);
  }

  return res.json();
}

export async function listResumes(): Promise<ParseResponse[]> {
  const res = await fetch(`${API_BASE}/api/resumes`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to list resumes: ${res.statusText}`);
  }

  return res.json();
}

