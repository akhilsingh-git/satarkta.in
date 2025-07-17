import { useState, useEffect, useCallback } from 'react';



interface Scan {
  id: string;
  invoiceNumber: string;
  vendorName: string;
  amount: string;
  date: string;
  fraudScore: number;
  riskLevel: 'HIGH' | 'MEDIUM' | 'LOW';
  processedAt: string;
  fraudReasons: string[];
}

interface RecentScansData {
  scans: Scan[];
  summary: {
    total: number;
    highRisk: number;
    mediumRisk: number;
    lowRisk: number;
  };
}

interface UseRecentScansReturn {
  data: RecentScansData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useRecentScans = (limit: number = 10): UseRecentScansReturn => {
  const [data, setData] = useState<RecentScansData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchScans = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/recent-scans?limit=${limit}`);
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        setData(result.data);
      } else {
        throw new Error(result.error || 'Failed to fetch scans');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Error fetching recent scans:', err);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchScans();
  }, [fetchScans]);

  return {
    data,
    loading,
    error,
    refetch: fetchScans
  };
};
