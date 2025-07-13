import { TrendingUp, Shield, AlertTriangle, FileText } from 'lucide-react';

const stats = [
  {
    title: 'Total Scans',
    value: '2,847',
    change: '+12%',
    changeType: 'positive',
    icon: FileText,
  },
  {
    title: 'Fraud Detected',
    value: '23',
    change: '-5%',
    changeType: 'negative',
    icon: AlertTriangle,
  },
  {
    title: 'Clean Invoices',
    value: '2,824',
    change: '+13%',
    changeType: 'positive',
    icon: Shield,
  },
  {
    title: 'Risk Score Avg',
    value: '15.2',
    change: '-8%',
    changeType: 'negative',
    icon: TrendingUp,
  },
];

export function StatsCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{stat.title}</p>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            </div>
            <div className={`p-3 rounded-full ${
              stat.changeType === 'positive' ? 'bg-green-100' : 'bg-red-100'
            }`}>
              <stat.icon className={`w-6 h-6 ${
                stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
              }`} />
            </div>
          </div>
          <div className="mt-4">
            <span className={`text-sm font-medium ${
              stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
            }`}>
              {stat.change}
            </span>
            <span className="text-sm text-gray-500 ml-1">from last month</span>
          </div>
        </div>
      ))}
    </div>
  );
}