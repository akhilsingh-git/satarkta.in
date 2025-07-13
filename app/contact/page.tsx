import { Metadata } from 'next';
import { ContactHero } from '@/components/contact/ContactHero';
import { ContactForm } from '@/components/contact/ContactForm';
import { ContactInfo } from '@/components/contact/ContactInfo';

export const metadata: Metadata = {
  title: 'Contact Us - Invoice Guard Support & Sales',
  description: 'Get in touch with our team for support, sales inquiries, or partnership opportunities. We\'re here to help protect your business.',
  openGraph: {
    title: 'Contact Us - Invoice Guard Support & Sales',
    description: 'Get in touch with our team for support, sales inquiries, or partnership opportunities.',
  },
};

export default function ContactPage() {
  return (
    <>
      <ContactHero />
      <div className="grid lg:grid-cols-2 gap-12 max-w-7xl mx-auto px-4 py-16">
        <ContactForm />
        <ContactInfo />
      </div>
    </>
  );
}