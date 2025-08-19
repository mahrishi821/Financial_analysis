// GenerateReportButton.tsx
import { TrendingUp, Loader2 } from "lucide-react";

export default function GenerateReportButton({ onClick, isGenerating }: {
  onClick: () => void;
  isGenerating: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={isGenerating}
      className="px-6 py-3 bg-blue-600 text-white rounded-lg flex items-center"
    >
      {isGenerating ? <Loader2 className="w-5 h-5 mr-2 animate-spin" /> : <TrendingUp className="w-5 h-5 mr-2" />}
      {isGenerating ? "Generating..." : "Generate Report"}
    </button>
  );
}
