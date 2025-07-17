"use client";

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import DashboardHeader from '@/components/dashboard/DashboardHeader';
import InvoiceUpload from '@/components/dashboard/InvoiceUpload';
import RecentScans from '@/components/dashboard/RecentScans';
import StatsCards from '@/components/dashboard/StatsCards';
import BankVerification from '@/components/dashboard/BankVerification';
import { FileText, CreditCard, BarChart3, Settings } from 'lucide-react';

const EnhancedDashboard: React.FC = () => {
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

        <Tabs defaultValue="invoice-processing" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="invoice-processing" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Invoice Processing
            </TabsTrigger>
            <TabsTrigger value="bank-verification" className="flex items-center gap-2">
              <CreditCard className="w-4 h-4" />
              Bank Verification
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Settings
            </TabsTrigger>
          </TabsList>

          <TabsContent value="invoice-processing" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <InvoiceUpload onUploadComplete={handleUploadComplete} />
              </div>
              <div>
                <RecentScans refreshTrigger={refreshTrigger} />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="bank-verification" className="space-y-6">
            <BankVerification />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Fraud Detection Trends
                </h3>
                <div className="text-center text-gray-500 py-8">
                  Analytics dashboard coming soon...
                </div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Risk Distribution
                </h3>
                <div className="text-center text-gray-500 py-8">
                  Risk analysis charts coming soon...
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                System Settings
              </h3>
              <div className="text-center text-gray-500 py-8">
                Settings panel coming soon...
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default EnhancedDashboard;