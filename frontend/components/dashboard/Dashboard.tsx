import React from 'react';
import { Metadata } from 'next';
// Fixed imports - using default imports instead of named imports
import DashboardHeader from '@/components/dashboard/DashboardHeader';
import InvoiceUpload from '@/components/dashboard/InvoiceUpload';
import RecentScans from '@/components/dashboard/RecentScans';
import StatsCards from '@/components/dashboard/StatsCards';

export const metadata: Metadata = {
  title: 'Dashboard - Invoice Fraud Detection',
  description: 'Monitor and analyze invoice fraud detection results',
};

export default function DashboardPage() {
  const [refreshTrigger, setRefreshTrigger] = React.useState(0);

  const handleUploadComplete = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <StatsCards />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <InvoiceUpload onUploadComplete={handleUploadComplete} />
          </div>
          <div>
            <RecentScans refreshTrigger={refreshTrigger} />
          </div>
        </div>
      </main>
    </div>
  );
}
