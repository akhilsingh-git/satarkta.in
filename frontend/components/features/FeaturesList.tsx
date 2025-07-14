import { Shield, FileSearch, TrendingUp, Zap, AlertTriangle, CheckCircle, Database, Lock } from 'lucide-react';

const features = [
  {
    icon: Shield,
    title: 'GSTIN Verification',
    description: 'Real-time verification of vendor GSTIN numbers against government databases with instant validation.',
    details: [
      'Government database integration',
      'Real-time status checking',
      'Historical verification logs',
      'Bulk verification support'
    ]
  },
  {
    icon: FileSearch,
    title: 'AI-Powered Duplicate Detection',
    description: 'Advanced machine learning algorithms detect duplicate invoices with 99.9% accuracy.',
    details: [
      'Machine learning algorithms',
      'Pattern recognition',
      'Historical data analysis',
      'False positive reduction'
    ]
  },
  {
    icon: TrendingUp,
    title: 'Intelligent Risk Scoring',
    description: 'Comprehensive risk assessment providing detailed fraud probability scores for every invoice.',
    details: [
      'Multi-factor risk analysis',
      'Dynamic scoring models',
      'Risk trend analysis',
      'Customizable thresholds'
    ]
  },
  {
    icon: Zap,
    title: 'Lightning Fast Processing',
    description: 'Get comprehensive fraud analysis results in under 3 seconds with our optimized pipeline.',
    details: [
      'Sub-3 second processing',
      'Parallel verification',
      'Optimized algorithms',
      'Real-time results'
    ]
  },
  {
    icon: AlertTriangle,
    title: 'Compliance Checking',
    description: 'Automated verification against GSTR-2B, e-invoice requirements, and regulatory standards.',
    details: [
      'GSTR-2B reconciliation',
      'E-invoice IRN validation',
      'Regulatory compliance',
      'Audit trail maintenance'
    ]
  },
  {
    icon: CheckCircle,
    title: 'Complete Audit Trail',
    description: 'Maintain detailed records of all processed invoices and fraud checks for compliance.',
    details: [
      'Complete transaction logs',
      'Compliance reporting',
      'Data retention policies',
      'Export capabilities'
    ]
  },
  {
    icon: Database,
    title: 'Advanced Analytics',
    description: 'Comprehensive dashboards and reports to monitor fraud patterns and trends.',
    details: [
      'Real-time dashboards',
      'Fraud pattern analysis',
      'Custom reports',
      'Trend visualization'
    ]
  },
  {
    icon: Lock,
    title: 'Enterprise Security',
    description: 'Bank-grade security with SOC 2 compliance and end-to-end encryption.',
    details: [
      'SOC 2 Type II certified',
      'End-to-end encryption',
      'Role-based access',
      'Security monitoring'
    ]
  }
];

export function FeaturesList() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid gap-16">
          {features.map((feature, index) => (
            <div key={index} className={`grid lg:grid-cols-2 gap-8 items-center ${
              index % 2 === 1 ? 'lg:grid-flow-col-dense' : ''
            }`}>
              <div className={index % 2 === 1 ? 'lg:col-start-2' : ''}>
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <feature.icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900">{feature.title}</h3>
                </div>
                <p className="text-lg text-gray-600 mb-6">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.details.map((detail, detailIndex) => (
                    <li key={detailIndex} className="flex items-center text-gray-700">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-3 flex-shrink-0" />
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
              <div className={`bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-8 ${
                index % 2 === 1 ? 'lg:col-start-1' : ''
              }`}>
                <div className="aspect-video bg-white rounded-lg shadow-lg flex items-center justify-center">
                  <feature.icon className="w-24 h-24 text-blue-300" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}