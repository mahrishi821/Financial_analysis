"use client";
import { useState } from "react";
import type { ReportingPeriod } from "@/types";

export function useFinancialUpload() {
  const [reportingPeriod, setReportingPeriod] = useState<ReportingPeriod>("quarterly");
  const [balanceSheetFile, setBalanceSheetFile] = useState<File | null>(null);
  const [profitLossFile, setProfitLossFile] = useState<File | null>(null);
  const [errors, setErrors] = useState<{ balanceSheet?: string; profitLoss?: string }>({});

  const validate = (file: File) => {
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv',
      'application/csv',
    ];
    const allowedExtensions = ['.xlsx', '.xls', '.csv'];
    const ext = '.' + (file.name.split('.').pop() || '').toLowerCase();
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(ext)) return 'Only Excel (.xlsx, .xls) and CSV files are allowed';
    if (file.size > 10 * 1024 * 1024) return 'File size must be less than 10MB';
    return null;
  };

  const onUpload = (file: File, type: 'balance_sheet' | 'profit_loss') => {
    const err = validate(file);
    if (err) {
      setErrors(prev => ({ ...prev, [type === 'balance_sheet' ? 'balanceSheet' : 'profitLoss']: err }));
      return;
    }
    setErrors(prev => ({ ...prev, [type === 'balance_sheet' ? 'balanceSheet' : 'profitLoss']: undefined }));
    if (type === 'balance_sheet') setBalanceSheetFile(file); else setProfitLossFile(file);
  };

  return {
    reportingPeriod, setReportingPeriod,
    balanceSheetFile, profitLossFile, errors, onUpload,
  };
}
