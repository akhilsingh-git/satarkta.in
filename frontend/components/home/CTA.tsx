import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight, Shield } from 'lucide-react';

export function CTA() {
  return (
    <section className="py-20 bg-gradient-to-br from-blue-600 to-cyan-600 text-white">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <div className="max-w-3xl mx-auto">
          <Shield className="w-16 h-16 mx-auto mb-6 text-blue-200" />
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Protect Your Business?
          </h2>
          <p className="text-xl text-blue-100 mb-8 leading-relaxed">
            Join thousands of businesses that trust Satarkta to protect them from fraud. 
            Start your free trial today and see the difference AI-powered protection makes.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3 text-lg group" asChild>
              <Link href="/dashboard">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3 text-lg" asChild>
              <Link href="/contact">Schedule Demo</Link>
            </Button>
          </div>

          <div className="text-sm text-blue-200">
            <p>✓ No credit card required  ✓ 14-day free trial  ✓ Cancel anytime</p>
          </div>
        </div>
      </div>
    </section>
  );
}