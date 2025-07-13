import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Invoice Guard - AI-Powered Fraud Detection Platform',
  description: 'Protect your business with advanced AI fraud detection for invoices. Real-time GSTIN verification, duplicate detection, and compliance checking.',
  keywords: 'invoice fraud detection, AI fraud prevention, GSTIN verification, invoice compliance, business security',
  authors: [{ name: 'Invoice Guard Team' }],
  creator: 'Invoice Guard',
  publisher: 'Invoice Guard',
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://invoiceguard.com',
    title: 'Invoice Guard - AI-Powered Fraud Detection Platform',
    description: 'Protect your business with advanced AI fraud detection for invoices. Real-time GSTIN verification, duplicate detection, and compliance checking.',
    siteName: 'Invoice Guard',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Invoice Guard - AI-Powered Fraud Detection',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Invoice Guard - AI-Powered Fraud Detection Platform',
    description: 'Protect your business with advanced AI fraud detection for invoices.',
    images: ['/og-image.jpg'],
  },
  verification: {
    google: 'your-google-verification-code',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="canonical" href="https://invoiceguard.com" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="theme-color" content="#3b82f6" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'SoftwareApplication',
              name: 'Invoice Guard',
              description: 'AI-powered fraud detection platform for invoices',
              applicationCategory: 'BusinessApplication',
              operatingSystem: 'Web',
              offers: {
                '@type': 'Offer',
                price: '0',
                priceCurrency: 'USD',
              },
              aggregateRating: {
                '@type': 'AggregateRating',
                ratingValue: '4.8',
                reviewCount: '250',
              },
            }),
          }}
        />
      </head>
      <body className={inter.className}>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}