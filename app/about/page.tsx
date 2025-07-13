import { Metadata } from 'next';
import { AboutHero } from '@/components/about/AboutHero';
import { Team } from '@/components/about/Team';
import { Mission } from '@/components/about/Mission';
import { Timeline } from '@/components/about/Timeline';

export const metadata: Metadata = {
  title: 'About Us - Invoice Guard Team & Mission',
  description: 'Learn about the Invoice Guard team, our mission to fight invoice fraud, and our journey to protect businesses worldwide.',
  openGraph: {
    title: 'About Us - Invoice Guard Team & Mission',
    description: 'Learn about the Invoice Guard team and our mission to fight invoice fraud.',
  },
};

export default function AboutPage() {
  return (
    <>
      <AboutHero />
      <Mission />
      <Team />
      <Timeline />
    </>
  );
}