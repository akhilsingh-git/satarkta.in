import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/admin/', '/dashboard/private/'],
    },
    sitemap: 'https://invoiceguard.com/sitemap.xml',
  };
}