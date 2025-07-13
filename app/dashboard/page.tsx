"use client";

import { Metadata } from 'next';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { InvoiceUpload } from '@/components/dashboard/InvoiceUpload';
import { RecentScans } from '@/components/dashboard/RecentScans';
import { StatsCards } from '@/components/dashboard/StatsCards';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <StatsCards />
        <div className="grid lg:grid-cols-3 gap-8 mt-8">
          <div className="lg:col-span-2">
            <InvoiceUpload />
          </div>
          <div>
            <RecentScans />
          </div>
        </div>
      </div>
    </div>
  );
}