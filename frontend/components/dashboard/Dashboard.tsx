import React, { useState } from 'react';
import DashboardHeader from './DashboardHeader';
import StatsCards from './StatsCards';
import InvoiceUpload from './InvoiceUpload';
import RecentScans from './RecentScans';

const Dashboard: React.FC = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

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
};

export default Dashboard;