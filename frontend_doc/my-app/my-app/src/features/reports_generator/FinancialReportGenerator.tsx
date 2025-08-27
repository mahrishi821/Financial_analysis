"use client";
import React, { useState } from "react";
import UploadSection from "./components/UploadSection";
import UploadedDocumentList from "./components/UploadedDocumentList";
import GenerateReportButton from "./components/GenerateReportButton";
import InfoCard from "./components/InfoCard";
import BackendReportsList from "./components/BackendReportsList";
import { Upload, TrendingUp, Download } from "lucide-react";
import { uploadReportFile, listReports } from "./services/uploadService";

interface UploadedDocument {
  id: string;
  name: string;
  type: string;
  size: string;
  uploadDate: string;
  status: "uploaded" | "processing" | "completed" | "error";
  fileRef?: File; // keep a reference to upload on Generate click
}

export default function FinancialReportGenerator() {
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);
  const [uploadError, setUploadError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportsRefreshToken, setReportsRefreshToken] = useState(0);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  // ✅ Handle file select (store only; do NOT call backend yet)
  const handleFileUpload = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];

    // validate
    if (file.size > 50 * 1024 * 1024) {
      setUploadError("File size must be less than 50MB");
      return;
    }

    setUploadError("");

    const newDoc: UploadedDocument = {
      id: Date.now().toString(),
      name: file.name,
      type: file.type,
      size: `${Math.round(file.size / 1024)} KB`,
      uploadDate: new Date().toISOString().split("T")[0],
      status: "uploaded",
      fileRef: file,
    };

    setUploadedDocs((prev) => [newDoc, ...prev]);
  };

  // ✅ Remove document
  const removeDocument = (id: string) => {
    setUploadedDocs((prev) => prev.filter((doc) => doc.id !== id));
  };

  // ✅ Generate report: now triggers backend upload for selected file(s)
  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

  const generateReport = async () => {
    if (uploadedDocs.length === 0) {
      setUploadError("Please upload at least one document to generate a report");
      return;
    }

    // take the first pending/uploaded doc
    const target = uploadedDocs.find((d) => d.status === "uploaded" || d.status === "error") || uploadedDocs[0];
    if (!target?.fileRef) {
      setUploadError("No file attached to upload. Please re-select the file.");
      return;
    }

    setIsGenerating(true);
    // mark as processing
    setUploadedDocs((prev) => prev.map((d) => (d.id === target.id ? { ...d, status: "processing" } : d)));

    const { ok, data, error } = await uploadReportFile(target.fileRef);

    if (!ok) {
      setUploadError(error || "Upload failed");
      setToast({ message: error || "Upload failed", type: "error" });
      setUploadedDocs((prev) => prev.map((d) => (d.id === target.id ? { ...d, status: "error" } : d)));
      setIsGenerating(false);
      return;
    }

    // mark as completed and clear the uploaded item from the list
    setUploadedDocs((prev) => prev.filter((d) => d.id !== target.id));

    // Show success toast (use backend message if present)
    const backendMsg = (data && (data.message || data.data?.message)) || "Report generated Successfully";
    setToast({ message: backendMsg, type: "success" });

    // Poll the reports endpoint until the new report appears (up to ~5s)
    const fileId = (data && (data.data?.file_id || data.file_id)) as number | undefined;
    let found = false;
    for (let i = 0; i < 5; i++) {
      await sleep(1000);
      const rep = await listReports();
      if (rep.ok && Array.isArray(rep.data) && fileId) {
        if (rep.data.some((it) => it.raw_file?.id === fileId)) {
          found = true;
          break;
        }
      }
    }

    // bump refresh token to reload reports list
    setReportsRefreshToken((x) => x + 1);

    setIsGenerating(false);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Upload */}
      <UploadSection onFileUpload={handleFileUpload} error={uploadError} />

      {/* Uploaded Docs */}
      {uploadedDocs.length > 0 && (
        <>
          <UploadedDocumentList docs={uploadedDocs} onRemove={removeDocument} />
          <div className="mt-6 flex justify-center">
            <GenerateReportButton
              onClick={generateReport}
              isGenerating={isGenerating}
              disabled={uploadedDocs.length === 0}
            />
          </div>
        </>
      )}

      {/* Completed Reports */}
      <BackendReportsList refreshToken={reportsRefreshToken} />

      {/* Info Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        <InfoCard
          title="Easy Upload"
          description="Drag and drop or click to upload"
          icon={<Upload className="w-5 h-5 text-white" />}
          color="border-blue-200 bg-blue-50"
        />
        <InfoCard
          title="Smart Analysis"
          description="AI-powered insights from data"
          icon={<TrendingUp className="w-5 h-5 text-white" />}
          color="border-purple-200 bg-purple-50"
        />
        <InfoCard
          title="Ready Reports"
          description="Download detailed PDF reports"
          icon={<Download className="w-5 h-5 text-white" />}
          color="border-green-200 bg-green-50"
        />
      </div>
      {/* Toast */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded shadow text-white ${toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'}`}
          onAnimationEnd={() => undefined}
        >
          {toast.message}
        </div>
      )}
    </div>
  );
}
