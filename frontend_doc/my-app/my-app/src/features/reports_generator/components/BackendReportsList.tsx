"use client";
// BackendReportsList.tsx
import { Download, RefreshCcw } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { ReportListItem, listReports } from "../services/uploadService";

export default function BackendReportsList({ refreshToken = 0 }: { refreshToken?: number }) {
  const [items, setItems] = useState<ReportListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const loadingRef = useRef(false);

  const load = useCallback(async () => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);
    setError("");
    const res = await listReports();
    if (!res.ok) {
      setError(res.error || "Failed to load reports");
      setItems([]);
    } else {
      const data = Array.isArray(res.data) ? res.data : [];
      setItems(data);
    }
    setLoading(false);
    loadingRef.current = false;
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Re-load whenever parent requests a refresh
  useEffect(() => {
    load();
  }, [refreshToken, load]);

  return (
    <div id="backend-reports" className="mt-8">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Reports</h3>
        <button onClick={load} className="text-blue-600 flex items-center" disabled={loading}>
          <RefreshCcw className={`w-4 h-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && <div className="text-red-600 mb-2">{error}</div>}

      <div className="divide-y border rounded-lg bg-white">
        {loading && items.length === 0 && (
          <div className="p-4 text-gray-500">Loading...</div>
        )}
        {!loading && items.length === 0 && !error && (
          <div className="p-4 text-gray-500">No reports yet</div>
        )}
        {items.map((f) => (
          <div key={f.raw_file.id} className="p-4 flex items-center justify-between">
            <div>
              <div className="font-medium flex items-center">
                {f.raw_file.file_name}
              </div>
              <div className="text-sm text-gray-500">
                {new Date(f.created_at || f.raw_file.created_at).toLocaleString()}
              </div>
            </div>
            <a href={f.report_file} target="_blank" rel="noreferrer" className="text-blue-600 flex items-center">
              <Download className="w-4 h-4 mr-1" /> Download
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

