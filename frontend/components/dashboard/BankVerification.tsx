import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, XCircle, AlertCircle, Loader2, CreditCard } from 'lucide-react';

interface BankVerificationResult {
  success: boolean;
  account_exists?: boolean;
  account_holder_name?: string;
  name_match?: boolean;
  bank_name?: string;
  branch_name?: string;
  account_type?: string;
  verification_id?: string;
  verified_at?: string;
  status?: string;
  error?: string;
}

const BankVerification: React.FC = () => {
  const [formData, setFormData] = useState({
    account_number: '',
    ifsc_code: '',
    account_holder_name: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BankVerificationResult | null>(null);
  const [ifscDetails, setIfscDetails] = useState<any>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Auto-verify IFSC when it's 11 characters
    if (name === 'ifsc_code' && value.length === 11) {
      verifyIfsc(value);
    }
  };

  const verifyIfsc = async (ifscCode: string) => {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/verify-ifsc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ifsc_code: ifscCode }),
      });

      const data = await response.json();
      if (data.success) {
        setIfscDetails(data);
      } else {
        setIfscDetails(null);
      }
    } catch (error) {
      console.error('IFSC verification error:', error);
      setIfscDetails(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.account_number || !formData.ifsc_code) {
      return;
    }
    
    // Validate IFSC format
    if (formData.ifsc_code.length !== 11) {
      setResult({
        success: false,
        error: 'IFSC code must be 11 characters long'
      });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:5001/api/verify-bank-account', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Bank verification error:', error);
      setResult({
        success: false,
        error: 'Network error. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'VERIFIED':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'ACCOUNT_NOT_FOUND':
      case 'NOT_FOUND':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'VERIFIED':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'ACCOUNT_NOT_FOUND':
      case 'NOT_FOUND':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="w-6 h-6 text-blue-600" />
          Bank Account Verification
        </CardTitle>
        <CardDescription>
          Verify bank account details using penny-less verification
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="account_number">Account Number *</Label>
              <Input
                id="account_number"
                name="account_number"
                type="text"
                value={formData.account_number}
                onChange={handleInputChange}
                placeholder="Enter account number"
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="ifsc_code">IFSC Code *</Label>
              <Input
                id="ifsc_code"
                name="ifsc_code"
                type="text"
                value={formData.ifsc_code}
                onChange={handleInputChange}
                placeholder="e.g., SBIN0001234"
                maxLength={11}
                minLength={11}
                style={{ textTransform: 'uppercase' }}
                required
              />
              {ifscDetails && (
                <div className="text-sm text-green-600 mt-1">
                  ✓ {ifscDetails.bank_name} - {ifscDetails.branch_name}
                </div>
              )}
              {formData.ifsc_code.length > 0 && formData.ifsc_code.length !== 11 && (
                <div className="text-sm text-red-600 mt-1">
                  IFSC code must be exactly 11 characters
                </div>
              )}
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="account_holder_name">Account Holder Name (Optional)</Label>
            <Input
              id="account_holder_name"
              name="account_holder_name"
              type="text"
              value={formData.account_holder_name}
              onChange={handleInputChange}
              placeholder="Enter account holder name for name matching"
            />
          </div>
          
          <Button 
            type="submit" 
            className="w-full" 
            disabled={loading || !formData.account_number || !formData.ifsc_code}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Verifying...
              </>
            ) : (
              'Verify Account'
            )}
          </Button>
        </form>

        {result && (
          <div className="mt-6 space-y-4">
            <div className={`p-4 rounded-lg border ${getStatusColor(result.status)}`}>
              <div className="flex items-center gap-2 mb-2">
                {getStatusIcon(result.status)}
                <h3 className="font-semibold">
                  Verification {result.success ? 'Complete' : 'Failed'}
                </h3>
              </div>
              
              {result.success ? (
                <div className="space-y-2 text-sm">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="font-medium">Account Status:</span>
                      <div className={result.account_exists ? 'text-green-600' : 'text-red-600'}>
                        {result.account_exists ? 'Active' : 'Not Found'}
                      </div>
                    </div>
                    
                    {result.account_holder_name && (
                      <div>
                        <span className="font-medium">Account Holder:</span>
                        <div>{result.account_holder_name}</div>
                      </div>
                    )}
                    
                    {result.bank_name && (
                      <div>
                        <span className="font-medium">Bank:</span>
                        <div>{result.bank_name}</div>
                      </div>
                    )}
                    
                    {formData.account_holder_name && result.name_match !== undefined && (
                      <div>
                        <span className="font-medium">Name Match:</span>
                        <div className={result.name_match ? 'text-green-600' : 'text-red-600'}>
                          {result.name_match ? 'Matched' : 'Not Matched'}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {result.verification_id && (
                    <div className="mt-3 pt-3 border-t">
                      <span className="text-xs text-gray-500">
                        Transaction ID: {result.verification_id}
                      </span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-sm">
                  <p className="text-red-600">{result.error}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default BankVerification;