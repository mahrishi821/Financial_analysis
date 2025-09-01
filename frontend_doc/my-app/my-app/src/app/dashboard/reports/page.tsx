import FinancialReportGenerator from "@/features/reports_generator/FinancialReportGenerator";

export default function ReportsPage() {
  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">Reports</h1>
      <FinancialReportGenerator />
    </div>
  );
}

