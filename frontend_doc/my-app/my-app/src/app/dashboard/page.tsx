import DocumentChatbot from '@/features/chatbot/components/DocumentChatbot';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-600 mb-6">Welcome back! Use the assistant to chat over your uploaded documents.</p>
        {/* Your existing dashboard content could go here */}
      </div>
      {/* Floating chatbot widget */}
      <DocumentChatbot />
    </div>
  );
}
