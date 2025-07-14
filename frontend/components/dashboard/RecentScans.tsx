import React from 'react';
import { RefreshCw, AlertCircle, FileText, Calendar, TrendingUp } from 'lucide-react';
import { useRecentScans } from '../../hooks/useRecentScans';

interface RecentScansProps {
  refreshTrigger?: number;
}

const RecentScans: React.FC<RecentScansProps> = ({ refreshTrigger }) => {
  const { data, loading, error, refetch } = useRecentScans(10);

  React.useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      refetch();
    }
  }, [refreshTrigger, refetch]);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'HIGH':
        return 'text-red-600 bg-red-100';
      case 'MEDIUM':
        return 'text-yellow-600 bg-yellow-100';
      case 'LOW':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  if (loading && !data) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Scans</h3>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Scans</h3>
          <button
            onClick={() => refetch()}
            className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <AlertCircle className="w-12 h-12 mb-2 text-red-500" />
          <p className="text-center">Error loading recent scans</p>
          <p className="text-sm text-center mt-1">{error}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const scans = data?.scans || [];

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Recent Scans</h3>
            {data && (
              <p className="text-sm text-gray-500 mt-1">
                {data.summary.total} scans in the last 7 days
              </p>
            )}
          </div>
          <button
            onClick={() => refetch()}
            disabled={loading}
            className={`p-2 text-gray-500 hover:text-gray-700 transition-colors ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            title="Refresh"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {scans.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No recent scans found</p>
            <p className="text-sm mt-1">Upload an invoice to get started</p>
          </div>
        ) : (
          scans.map((scan) => (
            <div key={scan.id} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium text-gray-900">
                      Invoice #{scan.invoiceNumber}
                    </h4>
                    <span
                      className={`px-2 py-1 text-xs font-semibold rounded-full ${getRiskColor(
                        scan.riskLevel
                      )}`}
                    >
                      {scan.riskLevel} RISK
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{scan.vendorName}</p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(scan.processedAt)}
                    </span>
                    <span className="flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      Score: {scan.fraudScore}/100
                    </span>
                  </div>
                  {scan.fraudReasons && scan.fraudReasons.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs text-gray-500">Risk factors:</p>
                      <ul className="text-xs text-gray-600 mt-1">
                        {scan.fraudReasons.slice(0, 2).map((reason, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="mr-1">•</span>
                            <span>{reason}</span>
                          </li>
                        ))}
                        {scan.fraudReasons.length > 2 && (
                          <li className="text-gray-400">
                            +{scan.fraudReasons.length - 2} more
                          </li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
                <div className="text-right ml-4">
                  <p className="font-semibold text-gray-900">{scan.amount}</p>
                  <p className="text-xs text-gray-500">{scan.date}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {data && data.scans.length > 0 && (
        <div className="p-4 bg-gray-50 border-t">
          <div className="flex justify-between items-center text-sm">
            <div className="flex gap-4">
              <span className="text-green-600">
                Low Risk: {data.summary.lowRisk}
              </span>
              <span className="text-yellow-600">
                Medium Risk: {data.summary.mediumRisk}
              </span>
              <span className="text-red-600">
                High Risk: {data.summary.highRisk}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecentScans;