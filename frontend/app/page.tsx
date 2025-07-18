"use client";

//import EnhancedDashboard from '@/components/dashboard/EnhancedDashboard';
// app/page.tsx
import {Hero} from '@/components/home/Hero';
import {Features} from '@/components/home/Features';
import {Stats} from '@/components/home/Stats';

export default function HomePage() {
  return (
    <>
      <Hero />
      <Features />
      <Stats />
      {/* Add other home components as needed */}
    </>
  );
}

//export default function HomePage() {
 // return (
 //   <EnhancedDashboard />
 // );
//..}
