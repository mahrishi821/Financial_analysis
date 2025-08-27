// src/features/reports_generator/services/uploadService.ts
// Provides a helper to upload a file to the backend as multipart/form-data

export type UploadResult = {
  ok: boolean;
  data?: any;
  error?: string;
};

const API_BASE_URL =
  (typeof process !== "undefined" && (process.env.NEXT_PUBLIC_API_BASE_URL || process.env.VITE_API_BASE_URL || process.env.REACT_APP_API_BASE_URL)) ||
  "http://localhost:8000";
const UPLOAD_ENDPOINT = `${API_BASE_URL}/api/upload/`;

export async function uploadReportFile(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file, file.name);

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60_000); // 60s timeout

  try {
    const res = await fetch(UPLOAD_ENDPOINT, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeout);

    // Try to parse JSON; if it fails, return text
    const contentType = res.headers.get("content-type") || "";
    let payload: any = undefined;

    if (contentType.includes("application/json")) {
      try {
        payload = await res.json();
      } catch {
        payload = undefined;
      }
    } else {
      try {
        payload = await res.text();
      } catch {
        payload = undefined;
      }
    }

    if (!res.ok) {
      const message = (payload && (payload.error || payload.detail)) || `Upload failed with status ${res.status}`;
      return { ok: false, error: message };
    }

    return { ok: true, data: payload };
  } catch (err: any) {
    const aborted = err?.name === "AbortError";
    return { ok: false, error: aborted ? "Upload timed out" : (err?.message || "Network error during upload") };
  } finally {
    clearTimeout(timeout);
  }
}

export type ReportListItem = {
  raw_file: {
    id: number;
    file_name: string;
    created_at: string; // ISO
  };
  report_file: string; // absolute URL to generated PDF
  created_at: string; // ISO for report creation
};

export async function listReports(): Promise<UploadResult & { data?: ReportListItem[] }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/files/`, { method: "GET" });
    const contentType = res.headers.get("content-type") || "";
    let payload: any = undefined;

    if (contentType.includes("application/json")) {
      try {
        payload = await res.json();
      } catch {
        payload = undefined;
      }
    } else {
      try {
        payload = await res.text();
      } catch {
        payload = undefined;
      }
    }

    if (!res.ok) {
      const message = (payload && (payload.error || payload.detail)) || `List reports failed with status ${res.status}`;
      return { ok: false, error: message };
    }

    return { ok: true, data: payload as ReportListItem[] };
  } catch (err: any) {
    return { ok: false, error: err?.message || "Network error while listing reports" };
  }
}
