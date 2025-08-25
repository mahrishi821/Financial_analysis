"use client";
import React, { useState } from "react";
import UploadSection from "./components/UploadSection";
import UploadedDocumentList from "./components/UploadedDocumentList";
import GenerateReportButton from "./components/GenerateReportButton";
import GeneratedReportsList from "./components/GeneratedReportsList";
import InfoCard from "./components/InfoCard";
import BackendReportsList from "./components/BackendReportsList";
import { Upload, TrendingUp, Download } from "lucide-react";
import { uploadReportFile } from "./services/uploadService";

interface UploadedDocument {
  id: string;
  name: string;
  type: string;
  size: string;
  uploadDate: string;
  status: "uploaded" | "processing" | "completed" | "error";
  fileRef?: File; // keep a reference to upload on Generate click
}

interface GeneratedReport {
  id: string;
  filename: string;
  generatedDate: string;
  size: string;
  sourceDocument: string;
}

export default function FinancialReportGenerator() {
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);
  const [generatedReports, setGeneratedReports] = useState<GeneratedReport[]>([]);
  const [uploadError, setUploadError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

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
      setUploadedDocs((prev) => prev.map((d) => (d.id === target.id ? { ...d, status: "error" } : d)));
      setIsGenerating(false);
      return;
    }

    // mark as completed
    setUploadedDocs((prev) => prev.map((d) => (d.id === target.id ? { ...d, status: "completed" } : d)));

    // optionally append to mock GeneratedReports if API returns a name
    const maybeFilename = (data && (data.filename || data.file || data.report_filename)) as string | undefined;
    if (maybeFilename) {
      const newReport: GeneratedReport = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        filename: maybeFilename,
        generatedDate: new Date().toISOString(),
        size: (data && (data.size || data.file_size)) || "-",
        sourceDocument: target.name,
      };
      setGeneratedReports((prev) => [newReport, ...prev]);
    }

    setIsGenerating(false);
  };

  // ✅ Download (redirect users to backend-completed reports section)
  const downloadReport = (report: GeneratedReport) => {
    const el = typeof document !== 'undefined' ? document.getElementById('backend-reports') : null;
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    alert('Please use the "Reports (completed)" section below to download the finalized file.');
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
            />
          </div>
        </>
      )}

      {/* Reports */}
      {generatedReports.length > 0 && (
        <GeneratedReportsList
          reports={generatedReports}
          onDownload={downloadReport}
        />
      )}

      {/* Completed Reports */}
      <BackendReportsList />

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
    </div>
  );
}
