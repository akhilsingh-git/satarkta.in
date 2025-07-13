import { Metadata } from 'next';
import { ProcessHero } from '@/components/how-it-works/ProcessHero';
import { ProcessSteps } from '@/components/how-it-works/ProcessSteps';
import { TechnologyStack } from '@/components/how-it-works/TechnologyStack';
import { ResultsShowcase } from '@/components/how-it-works/ResultsShowcase';

export const metadata: Metadata = {
  title: 'How It Works - Invoice Guard Fraud Detection Process',
  description: 'Learn how our AI-powered system detects invoice fraud in 4 simple steps. From upload to analysis in seconds.',
  openGraph: {
    title: 'How It Works - Invoice Guard Fraud Detection Process',
    description: 'Learn how our AI-powered system detects invoice fraud in 4 simple steps. From upload to analysis in seconds.',
  },
};

export default function HowItWorksPage() {
  return (
    <>
      <ProcessHero />
      <ProcessSteps />
      <TechnologyStack />
      <ResultsShowcase />
    </>
  );
}