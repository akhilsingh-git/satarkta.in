import { AlertTriangle, CheckCircle, Shield, TrendingUp } from 'lucide-react';

const sampleResults = [
  {
    type: 'legitimate',
    icon: CheckCircle,
    title: 'Legitimate Invoice',
    riskScore: 15,
    riskLevel: 'Low Risk',
    riskColor: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    invoiceNumber: 'INV-2025-001',
    vendor: 'ABC Technologies Pvt Ltd',
    amount: '₹45,000',
    checks: [
      { label: 'GSTIN Verification', status: 'passed', icon: '✓' },
      { label: 'Duplicate Check', status: 'passed', icon: '✓' },
      { label: 'GSTR-2B Match', status: 'passed', icon: '✓' },
      { label: 'Amount Validation', status: 'passed', icon: '✓' }
    ]
  },
  {
    type: 'suspicious',
    icon: AlertTriangle,
    title: 'Suspicious Invoice',
    riskScore: 78,
    riskLevel: 'High Risk',
    riskColor: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    invoiceNumber: 'INV-2025-002',
    vendor: 'XYZ Solutions Ltd',
    amount: '₹1,25,000',
    checks: [
      { label: 'GSTIN Verification', status: 'failed', icon: '✗' },
      { label: 'Duplicate Check', status: 'warning', icon: '⚠' },
      { label: 'GSTR-2B Match', status: 'failed', icon: '✗' },
      { label: 'Amount Validation', status: 'passed', icon: '✓' }
    ]
  }
];

export function ResultsShowcase() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            See Results in Action
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our comprehensive analysis provides detailed insights and actionable recommendations 
            for every invoice processed through our system.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
          {sampleResults.map((result, index) => (
            <div key={index} className={`${result.bgColor} ${result.borderColor} border-2 rounded-xl p-6`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <result.icon className={`w-6 h-6 ${result.riskColor}`} />
                  <h3 className="text-lg font-semibold text-gray-900">{result.title}</h3>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${result.riskColor} bg-white`}>
                  Risk: {result.riskScore}/100
                </div>
              </div>

              <div className="bg-white rounded-lg p-4 mb-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Invoice:</span>
                    <div className="font-medium">{result.invoiceNumber}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Amount:</span>
                    <div className="font-medium">{result.amount}</div>
                  </div>
                  <div className="col-span-2">
                    <span className="text-gray-600">Vendor:</span>
                    <div className="font-medium">{result.vendor}</div>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 mb-3">Verification Checks</h4>
                {result.checks.map((check, checkIndex) => (
                  <div key={checkIndex} className="flex items-center justify-between bg-white rounded-lg p-3">
                    <span className="text-gray-700">{check.label}</span>
                    <span className={`font-medium ${
                      check.status === 'passed' ? 'text-green-600' :
                      check.status === 'warning' ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {check.icon} {check.status.charAt(0).toUpperCase() + check.status.slice(1)}
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-4 p-3 bg-white rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700 font-medium">Overall Risk Level</span>
                  <span className={`font-bold ${result.riskColor}`}>{result.riskLevel}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Key benefits */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Comprehensive Analysis</h3>
            <p className="text-gray-600">
              Multiple verification layers ensure thorough fraud detection with minimal false positives.
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Risk Scoring</h3>
            <p className="text-gray-600">
              Clear risk scores from 0-100 help prioritize which invoices need immediate attention.
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Actionable Insights</h3>
            <p className="text-gray-600">
              Detailed recommendations guide your next steps for each invoice processed.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}