import DocumentChatbot from '@/features/chatbot/components/DocumentChatbot';
import DashboardOverview from '@/features/dashboard/components/DashboardOverview';
export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6">
        <DashboardOverview />
      </div>
      {/* Floating chatbot widget */}
      <DocumentChatbot />
    </div>
  );
}
