import UserProfile from "@/components/profile/UserProfile";

export default function ProfilePage() {
  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">Profile</h1>
      <div className="max-w-xl">
        <UserProfile />
      </div>
    </div>
  );
}

