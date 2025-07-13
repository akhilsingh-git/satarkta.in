const stats = [
  {
    value: '10,000+',
    label: 'Businesses Protected',
    description: 'Companies worldwide trust our platform',
  },
  {
    value: '50M+',
    label: 'Invoices Processed',
    description: 'Fraud checks completed successfully',
  },
  {
    value: '99.9%',
    label: 'Accuracy Rate',
    description: 'Precision in fraud detection',
  },
  {
    value: '$500M+',
    label: 'Fraud Prevented',
    description: 'Total fraud amount blocked',
  },
];

export function Stats() {
  return (
    <section className="py-20 bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Trusted by Industry Leaders
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Our platform has helped thousands of businesses protect themselves from fraud.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-blue-400 mb-2">
                {stat.value}
              </div>
              <div className="text-xl font-semibold mb-2">
                {stat.label}
              </div>
              <div className="text-gray-400">
                {stat.description}
              </div>
            </div>
          ))}
        </div>

        {/* Trust indicators */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 opacity-60">
          <div className="text-center">
            <div className="text-sm font-semibold">SOC 2 Type II</div>
            <div className="text-xs text-gray-400">Certified</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-semibold">ISO 27001</div>
            <div className="text-xs text-gray-400">Compliant</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-semibold">GDPR</div>
            <div className="text-xs text-gray-400">Ready</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-semibold">99.9%</div>
            <div className="text-xs text-gray-400">Uptime SLA</div>
          </div>
        </div>
      </div>
    </section>
  );
}