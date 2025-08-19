// UploadSection.tsx
import { Upload } from "lucide-react";

export default function UploadSection({ onFileUpload, error }: {
  onFileUpload: (files: FileList | null) => void;
  error: string;
}) {
  return (
    <div className="p-6">
      <div
        className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-gray-50"
        onClick={() => document.getElementById("file-input")?.click()}
      >
        <div className="flex flex-col items-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <Upload className="w-8 h-8 text-blue-600" />
          </div>
          <h4 className="text-xl font-semibold">Drop files here or click to browse</h4>
          <p className="text-gray-600">Excel, PDF, Word, or CSV files</p>
        </div>
        <input
          id="file-input"
          type="file"
          accept=".xlsx,.xls,.pdf,.doc,.docx,.csv"
          onChange={(e) => onFileUpload(e.target.files)}
          className="hidden"
        />
      </div>
      {error && <p className="mt-2 text-red-600">{error}</p>}
    </div>
  );
}
