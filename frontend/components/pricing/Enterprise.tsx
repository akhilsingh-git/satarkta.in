export function Enterprise() {
  const enterpriseFeatures = [
    {
      icon: "🏢",
      title: "Custom AI Models",
      description: "Tailored fraud detection models trained on your specific industry and business patterns"
    },
    {
      icon: "🔧",
      title: "White-Label Solution",
      description: "Fully branded fraud detection platform with your company's look and feel"
    },
    {
      icon: "🔗",
      title: "Custom Integrations",
      description: "Direct integration with your ERP, accounting systems, and existing workflows"
    },
    {
      icon: "📊",
      title: "Advanced Analytics",
      description: "Comprehensive dashboards, custom reports, and business intelligence insights"
    },
    {
      icon: "🛡️",
      title: "Enhanced Security",
      description: "On-premise deployment, custom security protocols, and compliance certifications"
    },
    {
      icon: "👥",
      title: "Dedicated Support",
      description: "Dedicated account manager, priority support, and custom SLA agreements"
    }
  ];

  const benefits = [
    "Unlimited invoice processing",
    "99.9% uptime SLA guarantee",
    "Custom fraud rule engine",
    "Real-time monitoring & alerts",
    "Multi-tenant architecture",
    "Advanced user management",
    "Custom reporting & analytics",
    "Priority feature requests"
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Enterprise Solutions
          </h2>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            Scalable fraud detection solutions designed for large organizations 
            with complex requirements and high-volume processing needs.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-16 items-center mb-20">
          {/* Features Grid */}
          <div>
            <h3 className="text-3xl font-bold mb-8">Enterprise Features</h3>
            <div className="grid sm:grid-cols-2 gap-6">
              {enterpriseFeatures.map((feature, index) => (
                <div
                  key={index}
                  className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20 hover:bg-white/15 transition-all"
                >
                  <div className="text-3xl mb-3">{feature.icon}</div>
                  <h4 className="text-lg font-semibold mb-2">{feature.title}</h4>
                  <p className="text-blue-100 text-sm">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Benefits List */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
            <h3 className="text-3xl font-bold mb-8">What's Included</h3>
            <div className="space-y-4">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center gap-3">
                  <svg className="w-6 h-6 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="text-lg">{benefit}</span>
                </div>
              ))}
            </div>

            <div className="mt-8 pt-8 border-t border-white/20">
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">Custom Pricing</div>
                <p className="text-blue-100 mb-6">
                  Tailored to your specific needs and volume requirements
                </p>
                <button className="bg-white text-gray-900 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors text-lg">
                  Contact Enterprise Sales
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Case Studies Preview */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold mb-4">Trusted by Industry Leaders</h3>
            <p className="text-blue-100 text-lg">
              See how enterprises are saving millions with our fraud detection platform
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">₹50M+</div>
              <div className="text-lg font-semibold mb-1">Fraud Prevented</div>
              <div className="text-blue-100 text-sm">In the last 12 months</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-400 mb-2">99.7%</div>
              <div className="text-lg font-semibold mb-1">Accuracy Rate</div>
              <div className="text-blue-100 text-sm">Across all enterprise clients</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-400 mb-2">10M+</div>
              <div className="text-lg font-semibold mb-1">Invoices Processed</div>
              <div className="text-blue-100 text-sm">Monthly across all clients</div>
            </div>
          </div>
        </div>

        {/* Contact Form */}
        <div className="mt-16 max-w-2xl mx-auto">
          <div className="bg-white rounded-2xl p-8 shadow-2xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
              Get Enterprise Pricing
            </h3>
            <form className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="John"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Doe"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Email
                </label>
                <input
                  type="email"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="john@company.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Your Company"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Monthly Invoice Volume
                </label>
                <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>1,000 - 5,000</option>
                  <option>5,000 - 10,000</option>
                  <option>10,000 - 50,000</option>
                  <option>50,000+</option>
                </select>
              </div>
              
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors text-lg"
              >
                Get Custom Quote
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}