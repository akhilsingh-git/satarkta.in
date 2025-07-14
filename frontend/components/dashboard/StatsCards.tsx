import React from 'react';
import { FileText, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';

const StatsCards: React.FC = () => {
  // In a real implementation, these would come from your backend
  const stats = [
    {
      title: 'Total Scans',
      value: '156',
      change: '+12%',
      icon: FileText,
      color: 'blue',
      trend: 'up'
    },
    {
      title: 'High Risk',
      value: '23',
      change: '-5%',
      icon: AlertTriangle,
      color: 'red',
      trend: 'down'
    },
    {
      title: 'Verified',
      value: '89',
      change: '+8%',
      icon: CheckCircle,
      color: 'green',
      trend: 'up'
    },
    {
      title: 'Avg. Risk Score',
      value: '42.5',
      change: '-3%',
      icon: TrendingUp,
      color: 'purple',
      trend: 'down'
    }
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-600',
      red: 'bg-red-100 text-red-600',
      green: 'bg-green-100 text-green-600',
      purple: 'bg-purple-100 text-purple-600'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${getColorClasses(stat.color)}`}>
                <Icon className="w-6 h-6" />
              </div>
              <span className={`text-sm font-medium ${
                stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}>
                {stat.change}
              </span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{stat.value}</h3>
            <p className="text-gray-600 text-sm mt-1">{stat.title}</p>
          </div>
        );
      })}
    </div>
  );
};

export default StatsCards;