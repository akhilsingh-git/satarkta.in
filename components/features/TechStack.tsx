const technologies = [
  { name: 'Machine Learning', description: 'Advanced AI models for fraud detection' },
  { name: 'Government APIs', description: 'Direct integration with official databases' },
  { name: 'Cloud Infrastructure', description: 'Scalable and reliable processing' },
  { name: 'Real-time Processing', description: 'Instant results with parallel computing' },
  { name: 'Blockchain Security', description: 'Immutable audit trails and security' },
  { name: 'Big Data Analytics', description: 'Pattern recognition across millions of records' },
];

export function TechStack() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Powered by Cutting-Edge Technology
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our platform leverages the latest advancements in AI, machine learning, and cloud computing 
            to deliver unparalleled fraud detection capabilities.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {technologies.map((tech, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{tech.name}</h3>
              <p className="text-gray-600">{tech.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}