// GeneratedReportsList.tsx
import { FileText, Download, Calendar } from "lucide-react";

export default function GeneratedReportsList({ reports, onDownload }: {
  reports: any[];
  onDownload: (r: any) => void;
}) {
  return (
    <div>
      <h3 className="font-semibold mb-4">Generated Reports</h3>
      {reports.map((r) => (
        <div key={r.id} className="flex justify-between p-4 border-b">
          <div>
            <p className="font-medium">{r.filename}</p>
            <p className="text-sm text-gray-500 flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              {new Date(r.generatedDate).toLocaleDateString()} • {r.size}
            </p>
          </div>
          <button onClick={() => onDownload(r)} className="flex items-center text-blue-600">
            <Download className="w-4 h-4 mr-1" /> Download
          </button>
        </div>
      ))}
    </div>
  );
}
