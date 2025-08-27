// GenerateReportButton.tsx
import { TrendingUp, Loader2 } from "lucide-react";

export default function GenerateReportButton({ onClick, isGenerating, disabled = false }: {
  onClick: () => void;
  isGenerating: boolean;
  disabled?: boolean;
}) {
  const isDisabled = isGenerating || disabled;
  return (
    <button
      onClick={onClick}
      disabled={isDisabled}
      className={`px-6 py-3 rounded-lg flex items-center text-white ${isDisabled ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
    >
      {isGenerating ? <Loader2 className="w-5 h-5 mr-2 animate-spin" /> : <TrendingUp className="w-5 h-5 mr-2" />}
      {isGenerating ? "Generating..." : "Generate Report"}
    </button>
  );
}
