"use client";
import React from "react";
import { Calendar } from "lucide-react";
import type { ReportingPeriod } from "@/types";

type Props = {
  reportingPeriod: ReportingPeriod;
  setReportingPeriod: (p: ReportingPeriod) => void;
  visible: boolean;
};

const ReportingPeriodSelector: React.FC<Props> = ({ reportingPeriod, setReportingPeriod, visible }) => {
  if (!visible) return null;
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Calendar className="w-5 h-5 mr-2 text-blue-600" />
          Step 2: Select Reporting Period
        </h3>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { value: "monthly", label: "Monthly" },
            { value: "quarterly", label: "Quarterly" },
            { value: "ytd", label: "Year-to-Date (YTD)" },
            { value: "annual", label: "Annual (Full Year)" },
          ].map(p => (
            <label key={p.value} className={`cursor-pointer border-2 rounded-lg p-4 text-center transition-all ${reportingPeriod === p.value ? "border-blue-500 bg-blue-50 text-blue-700" : "border-gray-200 hover:border-gray-300"}`}>
              <input type="radio" name="reportingPeriod" value={p.value} className="sr-only"
                     checked={reportingPeriod === p.value}
                     onChange={() => setReportingPeriod(p.value as ReportingPeriod)} />
              <div className="font-medium">{p.label}</div>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ReportingPeriodSelector;
