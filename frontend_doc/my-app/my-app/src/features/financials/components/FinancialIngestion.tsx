"use client";
import React, { useState } from "react";
import { TrendingUp } from "lucide-react";
import CompanySelector from "./CompanySelector";
import ReportingPeriodSelector from "./ReportingPeriodSelector";
import TemplateDownloader from "./TemplateDownloader";
import FinancialFileUploader from "./FinancialFileUploader";
import type { UploadedFinancialFile } from "@/types";
import { useFinancialUpload } from "../hooks/useFinancialUpload";

const FinancialIngestion: React.FC = () => {
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>("");
  const [selectedCompanyName, setSelectedCompanyName] = useState<string>("");
  const [history, setHistory] = useState<UploadedFinancialFile[]>([
    { id: 1, filename: "Q3-2024-Balance-Sheet.xlsx", fileType: "balance_sheet", period: "quarterly", company: "Apple Inc.", uploadDate: "2024-10-15", size: "245 KB" },
    { id: 2, filename: "Q3-2024-Profit-Loss.xlsx", fileType: "profit_loss", period: "quarterly", company: "Apple Inc.", uploadDate: "2024-10-15", size: "198 KB" },
    { id: 3, filename: "Sep-2024-Balance-Sheet.xlsx", fileType: "balance_sheet", period: "monthly", company: "Microsoft Corporation", uploadDate: "2024-10-05", size: "187 KB" },
  ]);

  const {
    reportingPeriod, setReportingPeriod,
    balanceSheetFile, profitLossFile, errors, onUpload
  } = useFinancialUpload();

  const onSubmit = async (_files: { bs?: File; pl?: File }) => {
    // Stub for real API upload
    console.log("Submitting financial files:", {
      company_id: selectedCompanyId,
      period: reportingPeriod,
      balance_sheet: _files.bs?.name,
      profit_loss: _files.pl?.name,
    });
    alert("Financial files uploaded successfully!");
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <TrendingUp className="w-8 h-8 mr-3 text-blue-600" />
          Financial Data Ingestion
        </h2>
        <p className="text-gray-600">Upload company financial statements for Balance Sheet and Profit & Loss reporting</p>
      </div>

      <CompanySelector
        selectedCompanyId={selectedCompanyId}
        setSelectedCompanyId={setSelectedCompanyId}
        setSelectedCompanyName={setSelectedCompanyName}
      />
      <ReportingPeriodSelector visible={!!selectedCompanyId} reportingPeriod={reportingPeriod} setReportingPeriod={setReportingPeriod} />
      <TemplateDownloader visible={!!selectedCompanyId} reportingPeriod={reportingPeriod} />
      <FinancialFileUploader
        visible={!!selectedCompanyId}
        selectedCompany={selectedCompanyId}
        reportingPeriod={reportingPeriod}
        balanceSheetFile={balanceSheetFile}
        profitLossFile={profitLossFile}
        errors={errors}
        onUpload={onUpload}
        onSubmit={onSubmit}
        history={history}
        setHistory={setHistory}
        companyName={selectedCompanyName}
      />
    </div>
  );
};

export default FinancialIngestion;
