import { Upload, Search, Shield, CheckCircle } from 'lucide-react';

const steps = [
  {
    icon: Upload,
    title: 'Upload Invoice',
    description: 'Simply upload your PDF invoice through our secure platform or API integration.',
    details: [
      'Drag & drop interface',
      'Bulk upload support',
      'API integration available',
      'Secure file handling'
    ]
  },
  {
    icon: Search,
    title: 'AI Analysis',
    description: 'Our advanced AI algorithms analyze the invoice for fraud indicators and patterns.',
    details: [
      'OCR text extraction',
      'Pattern recognition',
      'Historical data comparison',
      'Machine learning models'
    ]
  },
  {
    icon: Shield,
    title: 'Verification',
    description: 'Real-time verification against government databases and compliance checks.',
    details: [
      'GSTIN verification',
      'GSTR-2B reconciliation',
      'E-invoice IRN validation',
      'Duplicate detection'
    ]
  },
  {
    icon: CheckCircle,
    title: 'Results',
    description: 'Get comprehensive fraud analysis results with risk scores and recommendations.',
    details: [
      'Risk score (0-100)',
      'Detailed fraud indicators',
      'Actionable recommendations',
      'Audit trail generation'
    ]
  }
];

export function ProcessSteps() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Simple 4-Step Process
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            From upload to analysis in under 3 seconds. Our streamlined process ensures 
            quick and accurate fraud detection every time.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              {/* Step number */}
              <div className="absolute -top-4 -left-4 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm z-10">
                {index + 1}
              </div>
              
              {/* Card */}
              <div className="bg-gray-50 rounded-xl p-6 h-full hover:bg-white hover:shadow-lg transition-all duration-300 border border-transparent hover:border-gray-200">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <step.icon className="w-6 h-6 text-blue-600" />
                </div>
                
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {step.title}
                </h3>
                
                <p className="text-gray-600 mb-4">
                  {step.description}
                </p>
                
                <ul className="space-y-2">
                  {step.details.map((detail, detailIndex) => (
                    <li key={detailIndex} className="flex items-center text-sm text-gray-600">
                      <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-2 flex-shrink-0"></div>
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
              
              {/* Arrow connector */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-0">
                  <svg className="w-8 h-8 text-blue-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Processing time highlight */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center space-x-2 bg-green-100 text-green-800 px-6 py-3 rounded-full font-semibold">
            <CheckCircle className="w-5 h-5" />
            <span>Complete analysis in under 3 seconds</span>
          </div>
        </div>
      </div>
    </section>
  );
}