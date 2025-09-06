import "./globals.css";
import { ReactNode } from "react";
import { AuthProvider } from "@/context/AuthContext";
import { UserProvider } from "@/context/UserContext";



export const metadata = {
  title: "Doc Platform",
  description: "Refactored modular frontend",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <UserProvider>

              {children}

          </UserProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
