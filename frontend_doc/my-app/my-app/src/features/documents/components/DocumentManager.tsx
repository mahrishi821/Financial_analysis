"use client";
import React, { useState } from "react";
import UploadedFileList from "./UploadedFileList";
import UploadSection from "./UploadSection";
import Select from "@/components/common/Select";
import { useCompanies } from "@/context/CompanyContext";
import { useFileUpload } from "../hooks/useFileUpload";
import type { FileItem } from "@/types";

const DocumentManager: React.FC = () => {
  const { companies } = useCompanies();
  const [selectedCompany, setSelectedCompany] = useState<string>("");
  const [files, setFiles] = useState<FileItem[]>([
    { id: 1, filename: "Q3-2024-Financial-Reports.zip", uploadDate: "2024-10-15", uploader: "John Smith", size: "2.4 MB" },
    { id: 2, filename: "Legal-Documents-Update.zip", uploadDate: "2024-09-28", uploader: "Sarah Johnson", size: "1.8 MB" },
    { id: 3, filename: "Product-Roadmap-H2.zip", uploadDate: "2024-09-15", uploader: "Mike Chen", size: "3.1 MB" },
  ]);
  const { uploadZip, loading } = useFileUpload();

  const handleUpload = async (file: File) => {
    if (!selectedCompany) return alert("Please select a company before uploading");
    if (!file.name.endsWith(".zip")) return alert("Only ZIP files are supported");
    await uploadZip(selectedCompany, file);
    alert("File uploaded successfully!");
    setFiles(prev => [{ id: Date.now(), filename: file.name, uploadDate: new Date().toISOString().slice(0,10), uploader: "You", size: `${Math.round(file.size/1024)} KB` }, ...prev]);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Document Management</h2>
        <p className="text-gray-600">Upload and manage company document submissions.</p>
      </div>

      <div className="mb-6 max-w-md">
        <Select label="Select Company *" value={selectedCompany} onChange={(e) => setSelectedCompany(e.target.value)}>
          <option value="">-- Choose a company --</option>
          {companies.map(c => <option key={c.id} value={c.id}>{c.company_name}</option>)}
        </Select>
      </div>

      <UploadSection onDropFile={handleUpload} />
      <UploadedFileList files={files} />
    </div>
  );
};

export default DocumentManager;
