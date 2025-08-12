"use client";
import React, { useState } from "react";
import {
  Upload,
  FileText,
  Calendar,
  Mail,
  Phone,
  Building,
  Globe,
  Users,
  CheckCircle,
  Download,
  Eye,
} from "lucide-react";

interface FileItem {
  id: number;
  filename: string;
  uploadDate: string;
  uploader: string;
  size: string;
}

const DocPlatform: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"onboarding" | "upload">(
    "onboarding"
  );
  const [selectedCompany, setSelectedCompany] = useState<string>("");

  const [formData, setFormData] = useState({
    company_name: "",
    sector: "",
    sub_sector: "",
    country: "",
    incorporation_date: "",
    contact_person_name: "",
    contact_email: "",
    phone: "",
    frequency: "",
    status: "Active",
  });

  const [uploadedFiles, setUploadedFiles] = useState<FileItem[]>([
    {
      id: 1,
      filename: "Q3-2024-Financial-Reports.zip",
      uploadDate: "2024-10-15",
      uploader: "John Smith",
      size: "2.4 MB",
    },
    {
      id: 2,
      filename: "Legal-Documents-Update.zip",
      uploadDate: "2024-09-28",
      uploader: "Sarah Johnson",
      size: "1.8 MB",
    },
    {
      id: 3,
      filename: "Product-Roadmap-H2.zip",
      uploadDate: "2024-09-15",
      uploader: "Mike Chen",
      size: "3.1 MB",
    },
  ]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  //   e.preventDefault();
  //   console.log("Form submitted:", formData);
  //   // API call or further handling logic here
  // };
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();

  try {
    const response = await fetch("http://localhost:8000/api/companies/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error("Failed to submit form");
    }

    const data = await response.json();
    console.log("Success:", data);
    alert("Company onboarded successfully!");

    // Optionally reset form
    setFormData({
      company_name: "",
      sector: "",
      sub_sector: "",
      country: "",
      incorporation_date: "",
      contact_person_name: "",
      contact_email: "",
      phone: "",
      frequency: "",
      status: "Active",
    });
  } catch (error) {
    console.error("Error:", error);
    alert("Error onboarding company.");
  }
};


  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const newFile: FileItem = {
        id: uploadedFiles.length + 1,
        filename: file.name,
        uploadDate: new Date().toISOString().split("T")[0],
        uploader: "Current User",
        size: (file.size / (1024 * 1024)).toFixed(1) + " MB",
      };
      setUploadedFiles([newFile, ...uploadedFiles]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">Doc::</h1>
            </div>
            <nav className="flex space-x-8">
              <button
                onClick={() => setActiveTab("onboarding")}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === "onboarding"
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Company Onboarding
              </button>
              <button
                onClick={() => setActiveTab("upload")}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === "upload"
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Document Management
              </button>
            </nav>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "onboarding" && (
          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Company Onboarding
              </h2>
              <p className="text-gray-600">
                Add a new company to the platform.
              </p>
            </div>

            <form
              onSubmit={handleSubmit}
              className="bg-white rounded-xl shadow-sm border border-gray-200"
            >
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Building className="w-5 h-5 mr-2 text-blue-600" />
                  Company Information
                </h3>
              </div>

              <div className="p-6 space-y-6">
                {/* Company Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Company Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="company_name"
                      value={formData.company_name}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border rounded-lg"
                      placeholder="Enter legal company name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sector <span className="text-red-500">*</span>
                    </label>
                    <select
                      name="sector"
                      value={formData.sector}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border rounded-lg"
                    >
                      <option value="">Select sector</option>
                      <option value="SaaS">SaaS</option>
                      <option value="Fintech">Fintech</option>
                      <option value="Biotech">Biotech</option>
                      <option value="E-commerce">E-commerce</option>
                      <option value="AI/ML">AI/ML</option>
                      <option value="Healthcare">Healthcare</option>
                      <option value="EdTech">EdTech</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sub-sector
                    </label>
                    <input
                      type="text"
                      name="sub_sector"
                      value={formData.sub_sector}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border rounded-lg"
                      placeholder="More specific category"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Country <span className="text-red-500">*</span>
                    </label>
                    <select
                      name="country"
                      value={formData.country}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border rounded-lg"
                    >
                      <option value="">Select country</option>
                      <option value="United States">United States</option>
                      <option value="United Kingdom">United Kingdom</option>
                      <option value="Canada">Canada</option>
                      <option value="Germany">Germany</option>
                      <option value="France">France</option>
                      <option value="Singapore">Singapore</option>
                      <option value="India">India</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Incorporation Date <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      name="incorporation_date"
                      value={formData.incorporation_date}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Reporting Frequency{" "}
                      <span className="text-red-500">*</span>
                    </label>
                    <select
                      name="frequency"
                      value={formData.frequency}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border rounded-lg"
                    >
                      <option value="">Select frequency</option>
                      <option value="Quarterly">Quarterly</option>
                      <option value="Semi-Annual">Semi-Annual</option>
                      <option value="Annual">Annual</option>
                    </select>
                  </div>
                </div>

                {/* Contact Information */}
                <div className="border-t border-gray-200 pt-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <Users className="w-5 h-5 mr-2 text-blue-600" />
                    Contact Information
                  </h4>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Contact Person <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        name="contact_person_name"
                        value={formData.contact_person_name}
                        onChange={handleInputChange}
                        required
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="Primary contact name"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Contact Email <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="email"
                        name="contact_email"
                        value={formData.contact_email}
                        onChange={handleInputChange}
                        required
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="contact@company.com"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Phone Number
                      </label>
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="+1 (555) 123-4567"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Status <span className="text-red-500">*</span>
                      </label>
                      <select
                        name="status"
                        value={formData.status}
                        onChange={handleInputChange}
                        required
                        className="w-full px-3 py-2 border rounded-lg"
                      >
                        <option value="Active">Active</option>
                        <option value="Inactive">Inactive</option>
                        <option value="Offboarded">Offboarded</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Submit Button */}
                <div className="flex justify-end pt-6 border-t border-gray-200">
                  <button
                    type="submit"
                    className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 flex items-center"
                  >
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Onboard Company
                  </button>
                </div>
              </div>
            </form>
          </div>
        )}

        {activeTab === "upload" && (
          <div className="max-w-6xl mx-auto">
            {/* Upload Header */}
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Document Management
              </h2>
              <p className="text-gray-600">
                Upload and manage company document submissions.
              </p>
            </div>

            {/* Company Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Company <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="w-full md:w-1/2 px-3 py-2 border rounded-lg"
              >
                <option value="">-- Choose a company --</option>
                <option value="Acme Corp">Acme Corp</option>
                <option value="Globex Inc.">Globex Inc.</option>
                <option value="Initech">Initech</option>
                <option value="Hooli">Hooli</option>
              </select>
            </div>

            {/* Upload Section */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-8">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Upload className="w-5 h-5 mr-2 text-blue-600" />
                  Upload New Documents
                </h3>
              </div>

              <div className="p-6">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">
                    Upload ZIP File
                  </h4>
                  <p className="text-gray-600 mb-4">
                    Drag and drop your ZIP file here, or click to browse
                  </p>
                  <input
                    type="file"
                    // accept=".zip"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 cursor-pointer transition-colors"
                  >
                    Choose File
                  </label>
                  <p className="text-xs text-gray-500 mt-2">
                    Supported formats: ZIP files containing Excel, Word, PDF,
                    PPT documents
                  </p>
                </div>
              </div>
            </div>

            {/* Uploaded Files List */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-blue-600" />
                  Previously Uploaded Documents
                </h3>
              </div>

              <div className="divide-y divide-gray-200">
                {uploadedFiles.map((file) => (
                  <div
                    key={file.id}
                    className="p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {file.filename}
                        </h4>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            {file.uploadDate}
                          </span>
                          <span className="flex items-center">
                            <Users className="w-4 h-4 mr-1" />
                            {file.uploader}
                          </span>
                          <span>{file.size}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocPlatform;
