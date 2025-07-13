"use client";

import { useState } from 'react';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function InvoiceUpload() {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFiles = (files: File[]) => {
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    if (pdfFiles.length > 0) {
      setUploading(true);
      // Simulate upload
      setTimeout(() => {
        setUploading(false);
      }, 3000);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Upload Invoice</h2>
      
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {uploading ? (
          <div className="space-y-4">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-gray-600">Processing invoice...</p>
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="w-12 h-12 text-gray-400 mx-auto" />
            <div>
              <p className="text-lg font-medium text-gray-900">Drop your invoice here</p>
              <p className="text-gray-600">or click to browse files</p>
            </div>
            <Button>Choose File</Button>
            <p className="text-sm text-gray-500">
              Supports PDF files up to 10MB
            </p>
          </div>
        )}
      </div>

      {/* Recent analysis results */}
      <div className="mt-6 space-y-4">
        <h3 className="font-medium text-gray-900">Recent Analysis</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-green-600" />
              <div>
                <p className="font-medium text-green-900">INV-2025-001.pdf</p>
                <p className="text-sm text-green-700">Risk Score: 12/100</p>
              </div>
            </div>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
              Clean
            </span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <div>
                <p className="font-medium text-red-900">INV-2025-002.pdf</p>
                <p className="text-sm text-red-700">Risk Score: 78/100</p>
              </div>
            </div>
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
              High Risk
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}