"use client";
import React, { useState } from "react";
import { Search, CheckCircle, X, Building } from "lucide-react";
import { useCompanies } from "@/context/CompanyContext";
import type { Company } from "@/types";

type Props = {
  selectedCompanyId: string;
  setSelectedCompanyId: (id: string) => void;
  setSelectedCompanyName: (name: string) => void;
};

const CompanySelector: React.FC<Props> = ({ selectedCompanyId, setSelectedCompanyId, setSelectedCompanyName }) => {
  const { companies } = useCompanies();
  const [searchTerm, setSearchTerm] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);

  const filtered = companies.filter(c => c.company_name.toLowerCase().includes(searchTerm.toLowerCase()));

  const select = (c: Company) => {
    setSelectedCompanyId(String(c.id));
    setSelectedCompanyName(c.company_name);
    setSearchTerm(c.company_name);
    setShowDropdown(false);
  };

  const clear = () => {
    setSelectedCompanyId("");
    setSelectedCompanyName("");
    setSearchTerm("");
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Building className="w-5 h-5 mr-2 text-blue-600" />
          Step 1: Select Company
        </h3>
      </div>
      <div className="p-6">
        <div className="relative">
          <label className="block text-sm font-medium text-gray-700 mb-2">Company <span className="text-red-500">*</span></label>
          <div className="relative">
            <div className="flex items-center">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setShowDropdown(true); }}
                onFocus={() => setShowDropdown(true)}
                className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Search for a company..."
              />
              {selectedCompanyId && (
                <button onClick={clear} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            {showDropdown && searchTerm && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
                {filtered.length ? filtered.map(c => (
                  <button key={c.id} onClick={() => select(c)} className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0">
                    <div className="font-medium text-gray-900">{c.company_name}</div>
                  </button>
                )) : <div className="px-4 py-3 text-gray-500">No companies found</div>}
              </div>
            )}
          </div>

          {selectedCompanyId && (
            <div className="mt-3 flex items-center text-green-600">
              <CheckCircle className="w-4 h-4 mr-2" />
              <span className="text-sm">Selected</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompanySelector;
