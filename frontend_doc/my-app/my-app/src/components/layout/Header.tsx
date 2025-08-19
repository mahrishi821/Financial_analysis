"use client";
import React from "react";
import { FileText, Menu } from "lucide-react";

type Props = {
  activeTab: "onboarding" | "upload" | "financial";
  setActiveTab: (t: Props["activeTab"]) => void;
  onMenuClick: () => void;
};

const Header: React.FC<Props> = ({ activeTab, setActiveTab, onMenuClick }) => (
  <header className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center h-16">
        <div className="flex items-center space-x-3">
          <button onClick={onMenuClick} className="p-2 hover:bg-gray-100 rounded-lg lg:mr-2">
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold text-gray-900">Doc::</h1>
        </div>
        <nav className="flex space-x-2 sm:space-x-8">
          {(["onboarding", "upload", "financial"] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === tab ? "bg-blue-100 text-blue-700" : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab === "onboarding" ? "Company Onboarding" : tab === "upload" ? "Document Management" : "Financial Data Ingestion"}
            </button>
          ))}
        </nav>
      </div>
    </div>
  </header>
);

export default Header;
