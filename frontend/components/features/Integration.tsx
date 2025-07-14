import { Button } from '@/components/ui/button';
import Link from 'next/link';

const integrations = [
  { name: 'SAP', logo: '🏢' },
  { name: 'Oracle', logo: '🔴' },
  { name: 'QuickBooks', logo: '💚' },
  { name: 'Xero', logo: '🔵' },
  { name: 'Tally', logo: '🟡' },
  { name: 'Zoho', logo: '🟠' },
];

export function Integration() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
          Seamless Integration
        </h2>
        <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
          Connect Satarkta with your existing accounting and ERP systems for automated fraud protection.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 mb-12">
          {integrations.map((integration, index) => (
            <div key={index} className="flex flex-col items-center space-y-2">
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center text-2xl">
                {integration.logo}
              </div>
              <span className="text-sm font-medium text-gray-700">{integration.name}</span>
            </div>
          ))}
        </div>

        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl p-8 text-white">
          <h3 className="text-2xl font-bold mb-4">Ready to Get Started?</h3>
          <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
            Start protecting your business with our comprehensive fraud detection platform.
          </p>
          <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100" asChild>
            <Link href="/dashboard">Try It Free</Link>
          </Button>
        </div>
      </div>
    </section>
  );
}