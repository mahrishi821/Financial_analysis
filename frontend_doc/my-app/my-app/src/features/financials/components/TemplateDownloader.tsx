"use client";
import React from "react";
import { Download, FileSpreadsheet } from "lucide-react";
import type { ReportingPeriod } from "@/types";

type Props = {
  reportingPeriod: ReportingPeriod;
  visible: boolean;
};

const getTemplateName = (type: 'balance_sheet' | 'profit_loss', period: ReportingPeriod) => {
  const periodLabels = { monthly: 'Monthly', quarterly: 'Quarterly', ytd: 'Year-to-Date', annual: 'Annual' };
  const typeLabels = { balance_sheet: 'Balance Sheet', profit_loss: 'Profit & Loss' };
  return `${periodLabels[period]} ${typeLabels[type]} Template`;
};

const TemplateDownloader: React.FC<Props> = ({ reportingPeriod, visible }) => {
  if (!visible) return null;

  const handle = (type: 'balance_sheet' | 'profit_loss') => {
    const name = getTemplateName(type, reportingPeriod);
    alert(`Downloading: ${name}.xlsx`);
    console.log(`Download template: ${type}_${reportingPeriod}_template.xlsx`);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Download className="w-5 h-5 mr-2 text-blue-600" />
          Step 3: Download Templates
        </h3>
        <p className="text-sm text-gray-600 mt-1">Download the templates, fill them with data, and upload them back</p>
      </div>
      <div className="p-6 grid md:grid-cols-2 gap-6">
        {[
          { key: "balance_sheet", title: "Balance Sheet", color: "green" },
          { key: "profit_loss", title: "Profit & Loss", color: "purple" },
        ].map(b => (
          <div key={b.key} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <FileSpreadsheet className="w-8 h-8 mr-3 text-gray-600" />
                <div>
                  <h4 className="font-semibold text-gray-900">{b.title}</h4>
                  <p className="text-sm text-gray-600">{getTemplateName(b.key as any, reportingPeriod)}</p>
                </div>
              </div>
            </div>
            <button
              onClick={() => handle(b.key as any)}
              className={`w-full px-4 py-2 bg-${b.color}-600 text-white font-medium rounded-lg hover:bg-${b.color}-700 transition-colors`}
            >
              <Download className="w-4 h-4 inline mr-2" />
              Download Template
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TemplateDownloader;
