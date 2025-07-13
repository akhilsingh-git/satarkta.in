import { Hero } from '@/components/home/Hero';
import { Features } from '@/components/home/Features';
import { Stats } from '@/components/home/Stats';
import { Testimonials } from '@/components/home/Testimonials';
import { CTA } from '@/components/home/CTA';
import { TrustBadges } from '@/components/home/TrustBadges';

export default function Home() {
  return (
    <>
      <Hero />
      <TrustBadges />
      <Features />
      <Stats />
      <Testimonials />
      <CTA />
    </>
  );
}