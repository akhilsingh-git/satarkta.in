import { Brain, Database, Cloud, Lock, Zap, Globe } from 'lucide-react';

const technologies = [
  {
    icon: Brain,
    title: 'Artificial Intelligence',
    description: 'Advanced machine learning models trained on millions of invoices to detect fraud patterns.',
    features: ['Neural networks', 'Pattern recognition', 'Anomaly detection', 'Continuous learning']
  },
  {
    icon: Database,
    title: 'Government Integration',
    description: 'Direct integration with official government databases for real-time verification.',
    features: ['GSTIN database', 'GSTR-2B access', 'E-invoice portal', 'Tax authority APIs']
  },
  {
    icon: Cloud,
    title: 'Cloud Infrastructure',
    description: 'Scalable cloud architecture ensuring high availability and fast processing.',
    features: ['Auto-scaling', '99.9% uptime', 'Global CDN', 'Load balancing']
  },
  {
    icon: Lock,
    title: 'Enterprise Security',
    description: 'Bank-grade security with end-to-end encryption and compliance certifications.',
    features: ['SOC 2 certified', 'ISO 27001', 'GDPR compliant', 'Data encryption']
  },
  {
    icon: Zap,
    title: 'Real-time Processing',
    description: 'Optimized algorithms and parallel processing for lightning-fast results.',
    features: ['Sub-3s processing', 'Parallel execution', 'Caching layers', 'Edge computing']
  },
  {
    icon: Globe,
    title: 'API Integration',
    description: 'RESTful APIs and webhooks for seamless integration with existing systems.',
    features: ['REST APIs', 'Webhooks', 'SDKs available', 'Documentation']
  }
];

export function TechnologyStack() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Powered by Advanced Technology
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our platform leverages cutting-edge technology to deliver unparalleled 
            fraud detection capabilities with enterprise-grade security and reliability.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {technologies.map((tech, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-300">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <tech.icon className="w-6 h-6 text-blue-600" />
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {tech.title}
              </h3>
              
              <p className="text-gray-600 mb-4">
                {tech.description}
              </p>
              
              <ul className="space-y-2">
                {tech.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center text-sm text-gray-600">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-2 flex-shrink-0"></div>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Performance metrics */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
            <div className="text-gray-600">Accuracy Rate</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">&lt;3s</div>
            <div className="text-gray-600">Processing Time</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">50M+</div>
            <div className="text-gray-600">Invoices Processed</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
            <div className="text-gray-600">Availability</div>
          </div>
        </div>
      </div>
    </section>
  );
}