// UploadedDocumentList.tsx
import { X, Loader2, CheckCircle, AlertCircle } from "lucide-react";

export default function UploadedDocumentList({ docs, onRemove }: {
  docs: any[];
  onRemove: (id: string) => void;
}) {
  return (
    <div className="mt-6 space-y-3">
      {docs.map((doc) => (
        <div key={doc.id} className="flex justify-between p-4 bg-gray-50 rounded-lg border">
          <div>
            <p className="font-medium">{doc.name}</p>
            <p className="text-sm text-gray-500">{doc.size} • {doc.uploadDate}</p>
          </div>
          {doc.status === "uploaded" && (
            <button onClick={() => onRemove(doc.id)} className="text-red-600">
              <X />
            </button>
          )}
          {doc.status === "processing" && <Loader2 className="animate-spin" />}
          {doc.status === "completed" && <CheckCircle className="text-green-600" />}
          {doc.status === "error" && <AlertCircle className="text-red-600" />}
        </div>
      ))}
    </div>
  );
}
