"use client";
import React from "react";
import { FileText, Calendar, Users, Eye, Download } from "lucide-react";
import type { FileItem } from "@/types";

type Props = {
  files: FileItem[];
};

const UploadedFileList: React.FC<Props> = ({ files }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200">
    <div className="p-6 border-b border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 flex items-center">
        <FileText className="w-5 h-5 mr-2 text-blue-600" />
        Previously Uploaded Documents
      </h3>
    </div>
    <div className="divide-y divide-gray-200">
      {files.map((file) => (
        <div key={file.id} className="p-6 flex items-center justify-between hover:bg-gray-50 transition-colors">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h4 className="font-medium text-gray-900">{file.filename}</h4>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span className="flex items-center"><Calendar className="w-4 h-4 mr-1" />{file.uploadDate}</span>
                <span className="flex items-center"><Users className="w-4 h-4 mr-1" />{file.uploader}</span>
                <span>{file.size}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"><Eye className="w-4 h-4" /></button>
            <button className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"><Download className="w-4 h-4" /></button>
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default UploadedFileList;
