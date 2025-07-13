import { Metadata } from 'next';
import { PricingHero } from '@/components/pricing/PricingHero';
import { PricingCards } from '@/components/pricing/PricingCards';
import { FAQ } from '@/components/pricing/FAQ';
import { Enterprise } from '@/components/pricing/Enterprise';

export const metadata: Metadata = {
  title: 'Pricing - Invoice Guard Plans & Packages',
  description: 'Choose the perfect plan for your business. From free trials to enterprise solutions. Transparent pricing with no hidden fees.',
  openGraph: {
    title: 'Pricing - Invoice Guard Plans & Packages',
    description: 'Choose the perfect plan for your business. From free trials to enterprise solutions.',
  },
};

export default function PricingPage() {
  return (
    <>
      <PricingHero />
      <PricingCards />
      <FAQ />
      <Enterprise />
    </>
  );
}