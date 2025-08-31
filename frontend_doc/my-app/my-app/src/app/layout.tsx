import "./globals.css";
import { ReactNode } from "react";
import { CompanyProvider } from "@/context/CompanyContext";
import { UserProvider } from "@/context/UserContext";
import { AuthProvider } from "@/context/AuthContext";

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
            <CompanyProvider>
              {children}
            </CompanyProvider>
          </UserProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
