const companies = [
  { name: 'TechCorp', logo: 'https://images.pexels.com/photos/4792509/pexels-photo-4792509.jpeg?auto=compress&cs=tinysrgb&w=200&h=100&dpr=1' },
  { name: 'GlobalManufacturing', logo: 'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=200&h=100&dpr=1' },
  { name: 'RetailMax', logo: 'https://images.pexels.com/photos/3184360/pexels-photo-3184360.jpeg?auto=compress&cs=tinysrgb&w=200&h=100&dpr=1' },
  { name: 'FinanceFirst', logo: 'https://images.pexels.com/photos/3184338/pexels-photo-3184338.jpeg?auto=compress&cs=tinysrgb&w=200&h=100&dpr=1' },
  { name: 'InnovateInc', logo: 'https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=200&h=100&dpr=1' },
];

export function TrustBadges() {
  return (
    <section className="py-12 bg-white border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-8">
          <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold">
            Trusted by leading companies worldwide
          </p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 items-center justify-items-center opacity-60">
          {companies.map((company, index) => (
            <div key={index} className="grayscale hover:grayscale-0 transition-all duration-300">
              <img
                src={company.logo}
                alt={company.name}
                className="h-12 w-auto object-contain"
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}