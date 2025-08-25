"use client";
// FilesList.tsx
import { Download, RefreshCcw, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { BackendFileItem, listUploadedFiles } from "../services/uploadService";

export default function FilesList() {
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
      setError(res.error || "Failed to load files");
      setItems([]);
    } else {
      setItems(Array.isArray(res.data) ? res.data : []);
    }
    setLoading(false);
    loadingRef.current = false;
  }, []);

  // Initial load
  useEffect(() => {
    load();
  }, [load]);

  // Auto-poll every 5s while any file is processing
  useEffect(() => {
    const hasProcessing = items.some((i) => i.status === "processing");
    if (!hasProcessing) return;
    const t = setInterval(() => {
      load();
    }, 5000);
    return () => clearInterval(t);
  }, [items, load]);

  const renderStatus = (status: string) => {
    if (status === "done") {
      return (
        <span className="text-sm flex items-center text-green-600">
          <CheckCircle className="w-4 h-4 mr-1" /> done
        </span>
      );
    }
    if (status === "error") {
      return (
        <span className="text-sm flex items-center text-red-600">
          <AlertCircle className="w-4 h-4 mr-1" /> error
        </span>
      );
    }
    if (status === "processing") {
      return (
        <span className="text-sm flex items-center text-yellow-600">
          <Loader2 className="w-4 h-4 mr-1 animate-spin" /> processing
        </span>
      );
    }
    return <span className="text-sm text-gray-600">{status}</span>;
  };

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Uploaded Files</h3>
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
          <div className="p-4 text-gray-500">No files yet</div>
        )}
        {items.map((f) => (
          <div key={f.id} className="p-4 flex items-center justify-between">
            <div>
              <div className="font-medium">{f.file_name}</div>
              <div className="text-sm text-gray-500">
                {new Date(f.created_at).toLocaleString()} • {f.file_type}
              </div>
            </div>
            <div className="flex items-center gap-4">
              {renderStatus(f.status)}
              {f.status === 'done' ? (
                <a href={f.file} target="_blank" rel="noreferrer" className="text-blue-600 flex items-center">
                  <Download className="w-4 h-4 mr-1" /> Download
                </a>
              ) : (
                <span className="text-gray-400 flex items-center cursor-not-allowed" title="Available when status is done">
                  <Download className="w-4 h-4 mr-1" /> Download
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
