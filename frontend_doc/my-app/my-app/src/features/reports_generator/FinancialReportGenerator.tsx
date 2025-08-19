"use client";
import React, { useState } from "react";
import UploadSection from "./components/UploadSection";
import UploadedDocumentList from "./components/UploadedDocumentList";
import GenerateReportButton from "./components/GenerateReportButton";
import GeneratedReportsList from "./components/GeneratedReportsList";
import InfoCard from "./components/InfoCard";
import { Upload, TrendingUp, Download } from "lucide-react";

interface UploadedDocument {
  id: string;
  name: string;
  type: string;
  size: string;
  uploadDate: string;
  status: "uploaded" | "processing" | "completed" | "error";
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

  // ✅ Handle file upload
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
    };

    setUploadedDocs((prev) => [newDoc, ...prev]);
  };

  // ✅ Remove document
  const removeDocument = (id: string) => {
    setUploadedDocs((prev) => prev.filter((doc) => doc.id !== id));
  };

  // ✅ Generate report
  const generateReport = async () => {
    if (uploadedDocs.length === 0) {
      setUploadError("Please upload at least one document to generate a report");
      return;
    }

    setIsGenerating(true);

    // Simulate report generation
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const newReport: GeneratedReport = {
      id: Date.now().toString(),
      filename: `Report_${Date.now()}.pdf`,
      generatedDate: new Date().toISOString(),
      size: "2.1 MB",
      sourceDocument: uploadedDocs[0].name,
    };

    setGeneratedReports((prev) => [newReport, ...prev]);
    setUploadedDocs([]);
    setIsGenerating(false);
  };

  // ✅ Download
  const downloadReport = (report: GeneratedReport) => {
    alert(`Downloading ${report.filename}`);
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
