export function FAQ() {
  const faqs = [
    {
      question: "How does the fraud detection work?",
      answer: "Our AI-powered system analyzes multiple data points including GSTIN verification, invoice patterns, vendor history, and compliance checks against government databases like GSTR-2B and E-invoice systems to identify potential fraud indicators."
    },
    {
      question: "What file formats do you support?",
      answer: "We currently support PDF invoices. Our OCR technology can extract data from both digital and scanned PDF documents with high accuracy."
    },
    {
      question: "How accurate is the fraud detection?",
      answer: "Our system achieves over 95% accuracy in fraud detection with less than 2% false positives. The AI model is continuously trained on new fraud patterns to improve accuracy."
    },
    {
      question: "Can I integrate this with my existing accounting software?",
      answer: "Yes! We provide REST APIs and webhooks for easy integration with popular accounting software like Tally, QuickBooks, SAP, and custom ERP systems."
    },
    {
      question: "What happens if I exceed my monthly invoice limit?",
      answer: "You'll receive notifications when approaching your limit. Additional invoices can be processed at ₹10 per invoice, or you can upgrade to a higher plan anytime."
    },
    {
      question: "Is my data secure?",
      answer: "Absolutely. We use bank-grade encryption, comply with data protection regulations, and never store sensitive financial data longer than necessary for processing."
    },
    {
      question: "Do you offer custom fraud rules?",
      answer: "Yes, Professional and Enterprise plans include custom risk rules. You can set specific thresholds, vendor blacklists, and industry-specific fraud patterns."
    },
    {
      question: "What kind of support do you provide?",
      answer: "Starter plans get email support, Professional plans get priority support with faster response times, and Enterprise customers get dedicated account managers with phone support."
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-600">
            Everything you need to know about Invoice Guard
          </p>
        </div>

        <div className="space-y-6">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
            >
              <details className="group">
                <summary className="flex items-center justify-between p-6 cursor-pointer list-none">
                  <h3 className="text-lg font-semibold text-gray-900 pr-4">
                    {faq.question}
                  </h3>
                  <svg
                    className="w-5 h-5 text-gray-500 transition-transform group-open:rotate-180"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                <div className="px-6 pb-6">
                  <p className="text-gray-700 leading-relaxed">
                    {faq.answer}
                  </p>
                </div>
              </details>
            </div>
          ))}
        </div>

        {/* Contact CTA */}
        <div className="text-center mt-16">
          <div className="bg-blue-50 rounded-2xl p-8 border border-blue-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Still have questions?
            </h3>
            <p className="text-gray-600 mb-6">
              Our team is here to help you choose the right plan for your business.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                Contact Sales
              </button>
              <button className="border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
                Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}