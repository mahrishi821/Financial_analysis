"use client";
import React from "react";
import { Upload } from "lucide-react";

type Props = {
  onDropFile: (file: File) => void;
};

const UploadSection: React.FC<Props> = ({ onDropFile }) => (
  <div
    className="bg-white rounded-xl shadow-sm border border-gray-200 mb-8"
    onDragOver={(e) => e.preventDefault()}
    onDrop={(e) => {
      e.preventDefault();
      const f = e.dataTransfer.files?.[0];
      if (f) onDropFile(f);
    }}
  >
    <div className="p-6">
      <div
        className="p-6 border-2 border-dashed border-gray-300 rounded-lg text-center hover:border-blue-400 transition-colors cursor-pointer"
        onClick={() => document.getElementById("zip-upload")?.click()}
      >
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h4 className="text-lg font-medium text-gray-900 mb-2">Upload ZIP File</h4>
        <p className="text-gray-600 mb-4">Drag and drop your ZIP file here, or click to browse</p>
        <input
          type="file"
          accept=".zip"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onDropFile(f);
          }}
          className="hidden"
          id="zip-upload"
        />
        <p className="text-xs text-gray-500 mt-2">
          Supported formats: ZIP files containing Excel, Word, PDF, PPT documents
        </p>
      </div>
    </div>
  </div>
);

export default UploadSection;
