import { redirect } from "next/navigation";

export default function RootPage() {
  // Always redirect root to dashboard; middleware will guard if not logged in
  redirect("/dashboard");
}
