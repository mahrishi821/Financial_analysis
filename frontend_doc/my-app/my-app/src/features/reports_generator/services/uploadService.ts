// src/features/reports_generator/services/uploadService.ts
// Provides helpers to upload/list reports via the shared axios API client

import api from "@/service/api";

export type UploadResult = {
  ok: boolean;
  data?: any;
  error?: string;
};

export async function uploadReportFile(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file, file.name);

  try {
    const res = await api.post("/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return { ok: true, data: res.data };
  } catch (err: any) {
    const status = err?.response?.status;
    const payload = err?.response?.data;
    const message = (payload && (payload.error || payload.detail)) ||
      (status ? `Upload failed with status ${status}` : (err?.message || "Network error during upload"));
    return { ok: false, error: message };
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
    const res = await api.get("/reports/");
    return { ok: true, data: (res.data as ReportListItem[]) };
  } catch (err: any) {
    const status = err?.response?.status;
    const payload = err?.response?.data;
    const message = (payload && (payload.error || payload.detail)) ||
      (status ? `List reports failed with status ${status}` : (err?.message || "Network error while listing reports"));
    return { ok: false, error: message };
  }
}
