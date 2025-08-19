// InfoCard.tsx
export default function InfoCard({ title, description, icon, color }: {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}) {
  return (
    <div className={`p-6 rounded-xl border ${color}`}>
      <div className="flex items-center mb-3">
        {icon}
        <h4 className="ml-3 font-semibold">{title}</h4>
      </div>
      <p className="text-sm">{description}</p>
    </div>
  );
}
