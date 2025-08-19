"use client";
import React, { useState, useEffect, useRef } from "react";
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
  Menu,
  X,
  LogOut,
  User,
  AlertCircle,
  Search,
  FileSpreadsheet,
  TrendingUp
} from "lucide-react";

interface FileItem {
  id: number;
  filename: string;
  uploadDate: string;
  uploader: string;
  size: string;
}

interface UserProfile {
  name: string;
  surname: string;
  dateOfBirth: string;
  email: string;
  phone: string;
  profilePicture?: string;
}

interface Company {
  id: number;
  company_name: string;
}

interface UploadedFinancialFile {
  id: number;
  filename: string;
  fileType: 'balance_sheet' | 'profit_loss';
  period: string;
  company: string;
  uploadDate: string;
  size: string;
}

type ReportingPeriod = 'monthly' | 'quarterly' | 'ytd' | 'annual';
type ActiveTab = "onboarding" | "upload" | "financial";

const DocPlatform: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>("");
  const [selectedCompanyName, setSelectedCompanyName] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>("onboarding");
  const [isSideMenuOpen, setIsSideMenuOpen] = useState(false);
  const sideMenuRef = useRef<HTMLDivElement>(null);

  // Financial Data Ingestion States
  const [reportingPeriod, setReportingPeriod] = useState<ReportingPeriod>('quarterly');
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [showDropdown, setShowDropdown] = useState<boolean>(false);
  const [balanceSheetFile, setBalanceSheetFile] = useState<File | null>(null);
  const [profitLossFile, setProfitLossFile] = useState<File | null>(null);
  const [uploadErrors, setUploadErrors] = useState<{
    balanceSheet?: string;
    profitLoss?: string;
  }>({});

  // Keep demo user profile data (no API integration mentioned)
  const [userProfile] = useState<UserProfile>({
    name: "John",
    surname: "Doe",
    dateOfBirth: "1990-05-15",
    email: "john.doe@company.com",
    phone: "+1 (555) 123-4567",
    profilePicture: ""
  });

  // Keep demo uploaded files for document management (no API integration for fetching these)
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

  // Keep demo financial files (no API integration for fetching these)
  const [uploadedFinancialFiles, setUploadedFinancialFiles] = useState<UploadedFinancialFile[]>([
    {
      id: 1,
      filename: "Q3-2024-Balance-Sheet.xlsx",
      fileType: 'balance_sheet',
      period: 'quarterly',
      company: 'Apple Inc.',
      uploadDate: "2024-10-15",
      size: "245 KB"
    },
    {
      id: 2,
      filename: "Q3-2024-Profit-Loss.xlsx",
      fileType: 'profit_loss',
      period: 'quarterly',
      company: 'Apple Inc.',
      uploadDate: "2024-10-15",
      size: "198 KB"
    },
    {
      id: 3,
      filename: "Sep-2024-Balance-Sheet.xlsx",
      fileType: 'balance_sheet',
      period: 'monthly',
      company: 'Microsoft Corporation',
      uploadDate: "2024-10-05",
      size: "187 KB"
    }
  ]);

  // API integration for companies - remove mock data
  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/companies/");
        if (!response.ok) throw new Error("Failed to fetch companies");
        const data = await response.json();
        setCompanies(data);
      } catch (error) {
        console.error("Error fetching companies:", error);
      }
    };
    fetchCompanies();
  }, []);

  // Handle clicking outside the side menu to close it
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (sideMenuRef.current && !sideMenuRef.current.contains(event.target as Node)) {
        setIsSideMenuOpen(false);
      }
    };

    if (isSideMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isSideMenuOpen]);

  // Handle logout
  const handleLogout = () => {
    console.log("User logged out");
    setIsSideMenuOpen(false);
    // Add actual logout logic here later
  };

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

  // Filter companies based on search term for financial tab
  const filteredCompanies = companies.filter(company =>
    company.company_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Handle company selection for financial tab
  const handleFinancialCompanySelect = (company: Company) => {
    setSelectedCompany(company.id.toString());
    setSelectedCompanyName(company.company_name);
    setSearchTerm(company.company_name);
    setShowDropdown(false);
  };

  // Clear company selection for financial tab
  const clearFinancialCompanySelection = () => {
    setSelectedCompany("");
    setSelectedCompanyName("");
    setSearchTerm("");
  };

  // Get template names based on period
  const getTemplateName = (type: 'balance_sheet' | 'profit_loss', period: ReportingPeriod) => {
    const periodLabels = {
      monthly: 'Monthly',
      quarterly: 'Quarterly',
      ytd: 'Year-to-Date',
      annual: 'Annual'
    };

    const typeLabels = {
      balance_sheet: 'Balance Sheet',
      profit_loss: 'Profit & Loss'
    };

    return `${periodLabels[period]} ${typeLabels[type]} Template`;
  };

  // Handle template download
  const handleTemplateDownload = (type: 'balance_sheet' | 'profit_loss') => {
    const templateName = getTemplateName(type, reportingPeriod);
    // In a real app, this would trigger an actual file download
    alert(`Downloading: ${templateName}.xlsx`);
    console.log(`Download template: ${type}_${reportingPeriod}_template.xlsx`);
  };

  // Validate financial file type
  const validateFinancialFile = (file: File): string | null => {
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
      'text/csv', // .csv
      'application/csv'
    ];

    const allowedExtensions = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      return 'Only Excel (.xlsx, .xls) and CSV files are allowed';
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      return 'File size must be less than 10MB';
    }

    return null;
  };

  // Handle financial file upload
  const handleFinancialFileUpload = (file: File, type: 'balance_sheet' | 'profit_loss') => {
    const error = validateFinancialFile(file);

    if (error) {
      setUploadErrors(prev => ({ ...prev, [type === 'balance_sheet' ? 'balanceSheet' : 'profitLoss']: error }));
      return;
    }

    // Clear errors
    setUploadErrors(prev => ({ ...prev, [type === 'balance_sheet' ? 'balanceSheet' : 'profitLoss']: undefined }));

    // Set file
    if (type === 'balance_sheet') {
      setBalanceSheetFile(file);
    } else {
      setProfitLossFile(file);
    }
  };

  // Submit financial files
  const handleSubmitFinancialFiles = async () => {
    if (!selectedCompany) {
      alert('Please select a company first');
      return;
    }

    if (!balanceSheetFile && !profitLossFile) {
      alert('Please upload at least one file');
      return;
    }

    try {
      // In a real app, this would make API calls to upload files
      console.log('Submitting financial files:', {
        company_id: selectedCompany,
        period: reportingPeriod,
        balance_sheet: balanceSheetFile?.name,
        profit_loss: profitLossFile?.name
      });

      // Mock successful upload
      const selectedCompanyData = companies.find(c => c.id.toString() === selectedCompany);

      if (balanceSheetFile) {
        const newFile: UploadedFinancialFile = {
          id: Date.now(),
          filename: balanceSheetFile.name,
          fileType: 'balance_sheet',
          period: reportingPeriod,
          company: selectedCompanyData?.company_name || '',
          uploadDate: new Date().toISOString().split('T')[0],
          size: `${Math.round(balanceSheetFile.size / 1024)} KB`
        };
        setUploadedFinancialFiles(prev => [newFile, ...prev]);
      }

      if (profitLossFile) {
        const newFile: UploadedFinancialFile = {
          id: Date.now() + 1,
          filename: profitLossFile.name,
          fileType: 'profit_loss',
          period: reportingPeriod,
          company: selectedCompanyData?.company_name || '',
          uploadDate: new Date().toISOString().split('T')[0],
          size: `${Math.round(profitLossFile.size / 1024)} KB`
        };
        setUploadedFinancialFiles(prev => [newFile, ...prev]);
      }

      // Reset form
      setBalanceSheetFile(null);
      setProfitLossFile(null);
      alert('Financial files uploaded successfully!');

    } catch (error) {
      console.error("Error uploading financial files:", error);
      alert("Error uploading financial files.");
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // API integration for company onboarding - keep as is
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setSelectedFile(file);
  };

  // API integration for ZIP file upload - keep as is
  const handleUploadClick = async () => {
    if (!selectedFile) {
      alert("Please choose a file first");
      return;
    }
    if (!selectedCompany && activeTab === "upload") {
      alert("Please select a company before uploading");
      return;
    }
    if (!selectedFile.name.endsWith(".zip")) {
      alert("Only ZIP files are supported");
      return;
    }
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("company", selectedCompany);
      formData.append("company_id", selectedCompany);
      const response = await fetch("http://localhost:8000/api/upload-zip/", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Failed to upload file");
      }
      const data = await response.json();
      console.log("Upload successful", data);
      alert("File uploaded successfully!");
      setSelectedFile(null);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file.");
    }
  };

  // API integration for file upload - keep as is
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (!file) {
      alert("Please choose a file first");
      return;
    }
    if (!selectedCompany) {
      alert("Please select a company before uploading");
      return;
    }
    if (!file.name.endsWith(".zip")) {
      alert("Only ZIP files are supported");
      return;
    }
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("company", selectedCompany);
      const response = await fetch("http://localhost:8000/api/upload-zip/", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Failed to upload file");
      }
      const data = await response.json();
      console.log("Upload successful", data);
      alert("File uploaded successfully!");
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Overlay for mobile when side menu is open */}
      {isSideMenuOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"></div>
      )}

      {/* Side Menu */}
      <div
        ref={sideMenuRef}
        className={`fixed top-0 left-0 h-full w-80 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out ${
          isSideMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Side Menu Header */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Profile</h2>
          <button
            onClick={() => setIsSideMenuOpen(false)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* User Profile Section */}
        <div className="p-6 space-y-4">
          {/* Profile Picture */}
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center">
              {userProfile.profilePicture ? (
                <img
                  src={userProfile.profilePicture}
                  alt="Profile"
                  className="w-20 h-20 rounded-full object-cover"
                />
              ) : (
                <User className="w-10 h-10 text-gray-400" />
              )}
            </div>
          </div>

          {/* Profile Information */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                Full Name
              </label>
              <p className="text-gray-900 font-medium">
                {userProfile.name} {userProfile.surname}
              </p>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                Date of Birth
              </label>
              <div className="flex items-center text-gray-700">
                <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                {new Date(userProfile.dateOfBirth).toLocaleDateString()}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                Email
              </label>
              <div className="flex items-center text-gray-700">
                <Mail className="w-4 h-4 mr-2 text-gray-400" />
                <span className="text-sm">{userProfile.email}</span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                Phone
              </label>
              <div className="flex items-center text-gray-700">
                <Phone className="w-4 h-4 mr-2 text-gray-400" />
                {userProfile.phone}
              </div>
            </div>
          </div>
        </div>

        {/* Logout Button */}
        <div className="absolute bottom-6 left-6 right-6">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center px-4 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
          >
            <LogOut className="w-5 h-5 mr-2" />
            Logout
          </button>
        </div>
      </div>

      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              {/* Menu Toggle Button */}
              <button
                onClick={() => setIsSideMenuOpen(true)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors lg:mr-2"
              >
                <Menu className="w-5 h-5 text-gray-600" />
              </button>

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
              <button
                onClick={() => setActiveTab("financial")}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === "financial"
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Financial Data Ingestion
              </button>
            </nav>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Company Onboarding Tab */}
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

            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
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
                    onClick={(e) => {
                      e.preventDefault();
                      handleSubmit(e as any);
                    }}
                    className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 flex items-center"
                  >
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Onboard Company
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Document Management Tab */}
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
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.company_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Upload Section */}
            <div
              className="bg-white rounded-xl shadow-sm border border-gray-200 mb-8"
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const file = e.dataTransfer.files[0];
                if (file) handleFileUpload({ target: { files: [file] } } as any);
              }}
            >
              <div className="p-6">
                <div
                  className="p-6 border-2 border-dashed border-gray-300 rounded-lg text-center hover:border-blue-400 transition-colors cursor-pointer"
                  onClick={() => document.getElementById("file-upload")?.click()}
                >
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">
                    Upload ZIP File
                  </h4>
                  <p className="text-gray-600 mb-4">
                    Drag and drop your ZIP file here, or click to browse
                  </p>
                  <input
                    type="file"
                    accept=".zip"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    Supported formats: ZIP files containing Excel, Word, PDF, PPT documents
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

        {/* Financial Data Ingestion Tab */}
        {activeTab === "financial" && (
          <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
                <TrendingUp className="w-8 h-8 mr-3 text-blue-600" />
                Financial Data Ingestion
              </h2>
              <p className="text-gray-600">
                Upload company financial statements for Balance Sheet and Profit & Loss reporting
              </p>
            </div>

            {/* Step 1: Company Selection */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Building className="w-5 h-5 mr-2 text-blue-600" />
                  Step 1: Select Company
                </h3>
              </div>
              <div className="p-6">
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <div className="flex items-center">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => {
                          setSearchTerm(e.target.value);
                          setShowDropdown(true);
                        }}
                        onFocus={() => setShowDropdown(true)}
                        className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Search for a company..."
                      />
                      {selectedCompany && (
                        <button
                          onClick={clearFinancialCompanySelection}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>

                    {/* Dropdown */}
                    {showDropdown && searchTerm && (
                      <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
                        {filteredCompanies.length > 0 ? (
                          filteredCompanies.map((company) => (
                            <button
                              key={company.id}
                              onClick={() => handleFinancialCompanySelect(company)}
                              className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                            >
                              <div className="font-medium text-gray-900">{company.company_name}</div>
                            </button>
                          ))
                        ) : (
                          <div className="px-4 py-3 text-gray-500">No companies found</div>
                        )}
                      </div>
                    )}
                  </div>

                  {selectedCompany && (
                    <div className="mt-3 flex items-center text-green-600">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      <span className="text-sm">Selected: {selectedCompanyName}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Step 2: Reporting Period */}
            {selectedCompany && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Calendar className="w-5 h-5 mr-2 text-blue-600" />
                    Step 2: Select Reporting Period
                  </h3>
                </div>
                <div className="p-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {([
                      { value: 'monthly', label: 'Monthly' },
                      { value: 'quarterly', label: 'Quarterly' },
                      { value: 'ytd', label: 'Year-to-Date (YTD)' },
                      { value: 'annual', label: 'Annual (Full Year)' }
                    ] as const).map((period) => (
                      <label
                        key={period.value}
                        className={`cursor-pointer border-2 rounded-lg p-4 text-center transition-all ${
                          reportingPeriod === period.value
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <input
                          type="radio"
                          name="reportingPeriod"
                          value={period.value}
                          checked={reportingPeriod === period.value}
                          onChange={(e) => setReportingPeriod(e.target.value as ReportingPeriod)}
                          className="sr-only"
                        />
                        <div className="font-medium">{period.label}</div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Template Download */}
            {selectedCompany && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Download className="w-5 h-5 mr-2 text-blue-600" />
                    Step 3: Download Templates
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Download the templates, fill them with data, and upload them back
                  </p>
                </div>
                <div className="p-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Balance Sheet Template */}
                    <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                          <FileSpreadsheet className="w-8 h-8 text-green-600 mr-3" />
                          <div>
                            <h4 className="font-semibold text-gray-900">Balance Sheet</h4>
                            <p className="text-sm text-gray-600">
                              {getTemplateName('balance_sheet', reportingPeriod)}
                            </p>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleTemplateDownload('balance_sheet')}
                        className="w-full px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download Template
                      </button>
                    </div>

                    {/* Profit & Loss Template */}
                    <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                          <FileSpreadsheet className="w-8 h-8 text-purple-600 mr-3" />
                          <div>
                            <h4 className="font-semibold text-gray-900">Profit & Loss</h4>
                            <p className="text-sm text-gray-600">
                              {getTemplateName('profit_loss', reportingPeriod)}
                            </p>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleTemplateDownload('profit_loss')}
                        className="w-full px-4 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download Template
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: File Upload */}
            {selectedCompany && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Upload className="w-5 h-5 mr-2 text-blue-600" />
                    Step 4: Upload Completed Files
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Upload your completed Balance Sheet and/or Profit & Loss files
                  </p>
                </div>
                <div className="p-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Balance Sheet Upload */}
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-400 transition-colors">
                      <div className="text-center">
                        <FileSpreadsheet className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h4 className="text-lg font-medium text-gray-900 mb-2">Balance Sheet</h4>

                        {balanceSheetFile ? (
                          <div className="text-sm text-green-600 mb-4">
                            <CheckCircle className="w-4 h-4 inline mr-1" />
                            {balanceSheetFile.name}
                          </div>
                        ) : (
                          <p className="text-gray-600 mb-4">Upload your completed Balance Sheet</p>
                        )}

                        <input
                          type="file"
                          accept=".xlsx,.xls,.csv"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) handleFinancialFileUpload(file, 'balance_sheet');
                          }}
                          className="hidden"
                          id="balance-sheet-upload"
                        />
                        <label
                          htmlFor="balance-sheet-upload"
                          className="cursor-pointer inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                        >
                          <Upload className="w-4 h-4 mr-2" />
                          {balanceSheetFile ? 'Replace File' : 'Choose File'}
                        </label>

                        {uploadErrors.balanceSheet && (
                          <div className="mt-2 text-sm text-red-600 flex items-center">
                            <AlertCircle className="w-4 h-4 mr-1" />
                            {uploadErrors.balanceSheet}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Profit & Loss Upload */}
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-400 transition-colors">
                      <div className="text-center">
                        <FileSpreadsheet className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h4 className="text-lg font-medium text-gray-900 mb-2">Profit & Loss</h4>

                        {profitLossFile ? (
                          <div className="text-sm text-green-600 mb-4">
                            <CheckCircle className="w-4 h-4 inline mr-1" />
                            {profitLossFile.name}
                          </div>
                        ) : (
                          <p className="text-gray-600 mb-4">Upload your completed Profit & Loss</p>
                        )}

                        <input
                          type="file"
                          accept=".xlsx,.xls,.csv"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) handleFinancialFileUpload(file, 'profit_loss');
                          }}
                          className="hidden"
                          id="profit-loss-upload"
                        />
                        <label
                          htmlFor="profit-loss-upload"
                          className="cursor-pointer inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                        >
                          <Upload className="w-4 h-4 mr-2" />
                          {profitLossFile ? 'Replace File' : 'Choose File'}
                        </label>

                        {uploadErrors.profitLoss && (
                          <div className="mt-2 text-sm text-red-600 flex items-center">
                            <AlertCircle className="w-4 h-4 mr-1" />
                            {uploadErrors.profitLoss}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 text-xs text-gray-500">
                    <p>Supported formats: Excel (.xlsx, .xls) and CSV files</p>
                    <p>Maximum file size: 10MB per file</p>
                  </div>

                  {/* Submit Button */}
                  <div className="mt-6 flex justify-end">
                    <button
                      onClick={handleSubmitFinancialFiles}
                      disabled={!selectedCompany || (!balanceSheetFile && !profitLossFile)}
                      className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
                    >
                      <CheckCircle className="w-5 h-5 mr-2" />
                      Submit Files
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Uploaded Financial Files History */}
            {uploadedFinancialFiles.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <FileText className="w-5 h-5 mr-2 text-blue-600" />
                    Previously Uploaded Financial Files
                  </h3>
                </div>
                <div className="divide-y divide-gray-200">
                  {uploadedFinancialFiles.map((file) => (
                    <div key={file.id} className="p-6 flex items-center justify-between hover:bg-gray-50 transition-colors">
                      <div className="flex items-center space-x-4">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          file.fileType === 'balance_sheet' ? 'bg-green-100' : 'bg-purple-100'
                        }`}>
                          <FileSpreadsheet className={`w-5 h-5 ${
                            file.fileType === 'balance_sheet' ? 'text-green-600' : 'text-purple-600'
                          }`} />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{file.filename}</h4>
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span className="capitalize">{file.fileType.replace('_', ' ')}</span>
                            <span className="capitalize">{file.period}</span>
                            <span>{file.company}</span>
                            <span>{file.uploadDate}</span>
                            <span>{file.size}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocPlatform;