import { Shield, Zap, FileSearch, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

const features = [
  {
    icon: Shield,
    title: 'GSTIN Verification',
    description: 'Real-time verification of vendor GSTIN numbers against government databases.',
    color: 'text-blue-600',
    bg: 'bg-blue-100',
  },
  {
    icon: FileSearch,
    title: 'Duplicate Detection',
    description: 'AI-powered detection of duplicate invoices using machine learning algorithms.',
    color: 'text-green-600',
    bg: 'bg-green-100',
  },
  {
    icon: TrendingUp,
    title: 'Risk Scoring',
    description: 'Intelligent risk assessment with detailed fraud probability scores.',
    color: 'text-purple-600',
    bg: 'bg-purple-100',
  },
  {
    icon: Zap,
    title: 'Instant Processing',
    description: 'Get results in seconds with our optimized processing pipeline.',
    color: 'text-yellow-600',
    bg: 'bg-yellow-100',
  },
  {
    icon: AlertTriangle,
    title: 'Compliance Checking',
    description: 'Automated verification against GSTR-2B and e-invoice requirements.',
    color: 'text-red-600',
    bg: 'bg-red-100',
  },
  {
    icon: CheckCircle,
    title: 'Audit Trail',
    description: 'Complete audit trail for all processed invoices and fraud checks.',
    color: 'text-teal-600',
    bg: 'bg-teal-100',
  },
];

export function Features() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Comprehensive Fraud Protection
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our AI-powered platform provides multiple layers of protection to keep your business safe from invoice fraud.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group bg-gray-50 rounded-xl p-6 hover:bg-white hover:shadow-lg transition-all duration-300 border border-transparent hover:border-gray-200"
            >
              <div className={`w-12 h-12 ${feature.bg} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className={`w-6 h-6 ${feature.color}`} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* CTA section */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">Ready to Protect Your Business?</h3>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Join thousands of businesses that trust Satarkta to protect them from fraud.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                Start Free Trial
              </button>
              <button className="border border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
                Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}