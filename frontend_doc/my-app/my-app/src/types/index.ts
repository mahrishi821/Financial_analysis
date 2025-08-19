export interface FileItem {
  id: number;
  filename: string;
  uploadDate: string;
  uploader: string;
  size: string;
}

export interface UserProfile {
  name: string;
  surname: string;
  dateOfBirth: string;
  email: string;
  phone: string;
  profilePicture?: string;
}

export interface Company {
  id: number;
  company_name: string;
}

export type ReportingPeriod = 'monthly' | 'quarterly' | 'ytd' | 'annual';

export interface UploadedFinancialFile {
  id: number;
  filename: string;
  fileType: 'balance_sheet' | 'profit_loss';
  period: ReportingPeriod;
  company: string;
  uploadDate: string;
  size: string;
}
