import { Metadata } from 'next';
import { FeaturesHero } from '@/components/features/FeaturesHero';
import { FeaturesList } from '@/components/features/FeaturesList';
import { TechStack } from '@/components/features/TechStack';
import { Integration } from '@/components/features/Integration';

export const metadata: Metadata = {
  title: 'Features - Invoice Guard AI Fraud Detection',
  description: 'Discover powerful features including GSTIN verification, duplicate detection, compliance checking, and real-time fraud scoring.',
  openGraph: {
    title: 'Features - Invoice Guard AI Fraud Detection',
    description: 'Discover powerful features including GSTIN verification, duplicate detection, compliance checking, and real-time fraud scoring.',
  },
};

export default function FeaturesPage() {
  return (
    <>
      <FeaturesHero />
      <FeaturesList />
      <TechStack />
      <Integration />
    </>
  );
}