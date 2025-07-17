import React from 'react';
import { Shield, Bell, User } from 'lucide-react';

const DashboardHeader: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Shield className="w-8 h-8 text-blue-600 mr-3" />
            <h1 className="text-xl font-bold text-gray-900">
              Satarkta
            </h1>
          </div>

          <nav className="hidden md:flex space-x-8">
            <a href="#" className="text-gray-700 hover:text-gray-900 font-medium">
              Dashboard
            </a>
            <a href="#" className="text-gray-500 hover:text-gray-900">
              Reports
            </a>
            <a href="#" className="text-gray-500 hover:text-gray-900">
              Settings
            </a>
          </nav>

          <div className="flex items-center space-x-4">
            <button className="relative p-2 text-gray-500 hover:text-gray-700">
              <Bell className="w-5 h-5" />
              <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full"></span>
            </button>
            <button className="p-2 text-gray-500 hover:text-gray-700">
              <User className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;
