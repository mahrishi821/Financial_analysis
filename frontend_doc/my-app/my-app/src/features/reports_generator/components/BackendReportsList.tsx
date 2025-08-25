"use client";
// BackendReportsList.tsx
import { Download, RefreshCcw, CheckCircle, Loader2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { BackendFileItem, listUploadedFiles } from "../services/uploadService";

export default function BackendReportsList() {
  const [items, setItems] = useState<BackendFileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const loadingRef = useRef(false);

  const load = useCallback(async () => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);
    setError("");
    const res = await listUploadedFiles();
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

  // Poll while there are processing items (so done list can grow)
  useEffect(() => {
    const hasProcessing = items.some((i) => i.status === "processing");
    if (!hasProcessing) return;
    const t = setInterval(() => {
      load();
    }, 5000);
    return () => clearInterval(t);
  }, [items, load]);

  const doneItems = items.filter((i) => i.status === "done");
  const processingCount = items.filter((i) => i.status === "processing").length;

  return (
    <div id="backend-reports" className="mt-8">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Reports (completed)</h3>
        <button onClick={load} className="text-blue-600 flex items-center" disabled={loading}>
          <RefreshCcw className={`w-4 h-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {processingCount > 0 && (
        <div className="mb-2 text-sm text-yellow-700 flex items-center">
          <Loader2 className="w-4 h-4 mr-1 animate-spin" /> Processing {processingCount} file(s)...
        </div>
      )}

      {error && <div className="text-red-600 mb-2">{error}</div>}

      <div className="divide-y border rounded-lg bg-white">
        {loading && doneItems.length === 0 && (
          <div className="p-4 text-gray-500">Loading...</div>
        )}
        {!loading && doneItems.length === 0 && !error && (
          <div className="p-4 text-gray-500">No completed reports yet</div>
        )}
        {doneItems.map((f) => (
          <div key={f.id} className="p-4 flex items-center justify-between">
            <div>
              <div className="font-medium flex items-center">
                <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                {f.file_name}
              </div>
              <div className="text-sm text-gray-500">
                {new Date(f.created_at).toLocaleString()} • {f.file_type}
              </div>
            </div>
            <a href={f.file} target="_blank" rel="noreferrer" className="text-blue-600 flex items-center">
              <Download className="w-4 h-4 mr-1" /> Download
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

