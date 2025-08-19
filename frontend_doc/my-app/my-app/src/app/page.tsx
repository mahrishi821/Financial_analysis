"use client";
import React, { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import UserProfile from "@/components/profile/UserProfile";
import OnboardingForm from "@/features/onboarding/components/OnboardingForm";
import DocumentManager from "@/features/documents/components/DocumentManager";
import FinancialIngestion from "@/features/financials/components/FinancialIngestion";
import FinancialReportGenerator from "@/features/reports_generator/FinancialReportGenerator";

// Add FinancialReportGenerator as a tab option
type ActiveTab = "reportGenerator" | "onboarding" | "upload" | "financial";

export default function DocPlatformPage() {
  // Default tab is set to report generator
  const [activeTab, setActiveTab] = useState<ActiveTab>("reportGenerator");
  const [isSideMenuOpen, setIsSideMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar isOpen={isSideMenuOpen} onClose={() => setIsSideMenuOpen(false)}>
        <UserProfile />
      </Sidebar>

      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onMenuClick={() => setIsSideMenuOpen(true)}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "reportGenerator" && <FinancialReportGenerator />}
        {activeTab === "onboarding" && <OnboardingForm />}
        {activeTab === "upload" && <DocumentManager />}
        {activeTab === "financial" && <FinancialIngestion />}
      </main>
    </div>
  );
}
