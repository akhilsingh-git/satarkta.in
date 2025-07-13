import { FileText, AlertTriangle, Shield, Clock } from 'lucide-react';

const recentScans = [
  {
    id: '1',
    fileName: 'Invoice_ABC_001.pdf',
    timestamp: '2 minutes ago',
    riskScore: 15,
    status: 'clean',
    vendor: 'ABC Technologies',
  },
  {
    id: '2',
    fileName: 'Invoice_XYZ_045.pdf',
    timestamp: '15 minutes ago',
    riskScore: 82,
    status: 'high-risk',
    vendor: 'XYZ Solutions',
  },
  {
    id: '3',
    fileName: 'Invoice_DEF_123.pdf',
    timestamp: '1 hour ago',
    riskScore: 35,
    status: 'medium-risk',
    vendor: 'DEF Services',
  },
  {
    id: '4',
    fileName: 'Invoice_GHI_789.pdf',
    timestamp: '2 hours ago',
    riskScore: 8,
    status: 'clean',
    vendor: 'GHI Corporation',
  },
];

export function RecentScans() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Recent Scans</h2>
      
      <div className="space-y-4">
        {recentScans.map((scan) => (
          <div key={scan.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <FileText className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900 text-sm">{scan.fileName}</p>
                  <p className="text-xs text-gray-600">{scan.vendor}</p>
                  <div className="flex items-center space-x-1 mt-1">
                    <Clock className="w-3 h-3 text-gray-400" />
                    <span className="text-xs text-gray-500">{scan.timestamp}</span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="flex items-center space-x-2 mb-1">
                  {scan.status === 'clean' && <Shield className="w-4 h-4 text-green-600" />}
                  {scan.status === 'medium-risk' && <AlertTriangle className="w-4 h-4 text-yellow-600" />}
                  {scan.status === 'high-risk' && <AlertTriangle className="w-4 h-4 text-red-600" />}
                  
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    scan.status === 'clean' 
                      ? 'bg-green-100 text-green-800'
                      : scan.status === 'medium-risk'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {scan.riskScore}/100
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-center">
        <button className="text-blue-600 text-sm font-medium hover:text-blue-700">
          View All Scans
        </button>
      </div>
    </div>
  );
}