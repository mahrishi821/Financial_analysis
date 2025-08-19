"use client";
import React from "react";
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, Download, FileText } from "lucide-react";
import type { UploadedFinancialFile } from "@/types";

type Props = {
  selectedCompany: string;
  reportingPeriod: 'monthly' | 'quarterly' | 'ytd' | 'annual';
  balanceSheetFile: File | null;
  profitLossFile: File | null;
  errors: { balanceSheet?: string; profitLoss?: string };
  onUpload: (file: File, type: 'balance_sheet' | 'profit_loss') => void;
  onSubmit: (files: { bs?: File; pl?: File }) => void;
  history: UploadedFinancialFile[];
  setHistory: React.Dispatch<React.SetStateAction<UploadedFinancialFile[]>>;
  companyName: string;
  visible: boolean;
};

const FinancialFileUploader: React.FC<Props> = ({
  selectedCompany, reportingPeriod, balanceSheetFile, profitLossFile, errors,
  onUpload, onSubmit, history, setHistory, companyName, visible
}) => {
  if (!visible) return null;

  const handleSubmit = () => {
    if (!selectedCompany) return alert("Please select a company first");
    if (!balanceSheetFile && !profitLossFile) return alert("Please upload at least one file");
    onSubmit({ bs: balanceSheetFile ?? undefined, pl: profitLossFile ?? undefined });

    const today = new Date().toISOString().slice(0,10);
    if (balanceSheetFile) {
      setHistory(prev => [{
        id: Date.now(),
        filename: balanceSheetFile.name,
        fileType: "balance_sheet",
        period: reportingPeriod,
        company: companyName,
        uploadDate: today,
        size: `${Math.round(balanceSheetFile.size/1024)} KB`
      }, ...prev]);
    }
    if (profitLossFile) {
      setHistory(prev => [{
        id: Date.now()+1,
        filename: profitLossFile.name,
        fileType: "profit_loss",
        period: reportingPeriod,
        company: companyName,
        uploadDate: today,
        size: `${Math.round(profitLossFile.size/1024)} KB`
      }, ...prev]);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Upload className="w-5 h-5 mr-2 text-blue-600" />
          Step 4: Upload Completed Files
        </h3>
        <p className="text-sm text-gray-600 mt-1">Upload your completed Balance Sheet and/or Profit & Loss files</p>
      </div>
      <div className="p-6">
        <div className="grid md:grid-cols-2 gap-6">
          {[
            { key: "balance_sheet", title: "Balance Sheet", file: balanceSheetFile, error: errors.balanceSheet },
            { key: "profit_loss", title: "Profit & Loss", file: profitLossFile, error: errors.profitLoss },
          ].map(b => (
            <div key={b.key} className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-400 transition-colors">
              <div className="text-center">
                <FileSpreadsheet className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">{b.title}</h4>
                {b.file ? (
                  <div className="text-sm text-green-600 mb-4">
                    <CheckCircle className="w-4 h-4 inline mr-1" />
                    {b.file.name}
                  </div>
                ) : (
                  <p className="text-gray-600 mb-4">Upload your completed {b.title}</p>
                )}
                <input
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  id={`${b.key}-upload`}
                  className="hidden"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) onUpload(f, b.key as "balance_sheet" | "profit_loss");
                  }}
                />
                <label htmlFor={`${b.key}-upload`} className="cursor-pointer inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors">
                  <Upload className="w-4 h-4 mr-2" />
                  {b.file ? "Replace File" : "Choose File"}
                </label>
                {b.error && (
                  <div className="mt-2 text-sm text-red-600 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {b.error}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 text-xs text-gray-500">
          <p>Supported formats: Excel (.xlsx, .xls) and CSV files</p>
          <p>Maximum file size: 10MB per file</p>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleSubmit}
            disabled={!selectedCompany || (!balanceSheetFile && !profitLossFile)}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
          >
            <CheckCircle className="w-5 h-5 mr-2" />
            Submit Files
          </button>
        </div>
      </div>

      {history.length > 0 && (
        <div className="border-t border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FileText className="w-5 h-5 mr-2 text-blue-600" />
              Previously Uploaded Financial Files
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {history.map((f) => (
              <div key={f.id} className="p-6 flex items-center justify-between hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${f.fileType === "balance_sheet" ? "bg-green-100" : "bg-purple-100"}`}>
                    <FileSpreadsheet className={`w-5 h-5 ${f.fileType === "balance_sheet" ? "text-green-600" : "text-purple-600"}`} />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{f.filename}</h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="capitalize">{f.fileType.replace("_", " ")}</span>
                      <span className="capitalize">{f.period}</span>
                      <span>{f.company}</span>
                      <span>{f.uploadDate}</span>
                      <span>{f.size}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FinancialFileUploader;
