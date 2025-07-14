import { Mail, Phone, MapPin, Clock } from 'lucide-react';

const contactMethods = [
  {
    icon: Mail,
    title: 'Email Us',
    details: 'support@satarkta.in',
    description: 'Send us an email and we\'ll respond within 24 hours.',
  },
  {
    icon: Phone,
    title: 'Call Us',
    details: '+91 7977439809',
    description: 'Speak directly with our support team.',
  },
  {
    icon: MapPin,
    title: 'Visit Us',
    details: 'Mumbai, Maharashtra',
    description: 'Come visit our headquarters.',
  },
  {
    icon: Clock,
    title: 'Support Hours',
    details: 'Mon-Fri: 9AM-6PM PST',
    description: '24/7 support available for enterprise customers.',
  },
];

export function ContactInfo() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Other ways to reach us</h2>
        <p className="text-gray-600">
          Choose the contact method that works best for you. Our team is standing by to help.
        </p>
      </div>

      <div className="space-y-6">
        {contactMethods.map((method, index) => (
          <div key={index} className="flex space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <method.icon className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{method.title}</h3>
              <p className="text-blue-600 font-medium">{method.details}</p>
              <p className="text-gray-600 text-sm">{method.description}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-gray-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Enterprise Support</h3>
        <p className="text-gray-600 mb-4">
          Need dedicated support for your organization? Our enterprise team provides:
        </p>
        <ul className="space-y-2 text-sm text-gray-600">
          <li>• Dedicated account manager</li>
          <li>• 24/7 priority support</li>
          <li>• Custom integration assistance</li>
          <li>• Training and onboarding</li>
        </ul>
      </div>
    </div>
  );
}