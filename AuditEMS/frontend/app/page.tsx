'use client';

import Header from '@/components/header';
import Hero from '@/components/hero';
import DocumentUpload from '@/components/document-upload';
import Features from '@/components/features';
import Stats from '@/components/stats';
import Testimonials from '@/components/testimonials';
import CTA from '@/components/cta';
import Footer from '@/components/footer';

export default function Page() {
  return (
    <div className="overflow-hidden bg-gradient-to-br from-background via-background to-primary/5 dark:from-background dark:via-background dark:to-primary/10">
      <Header />
      <main>
        <Hero />
        <DocumentUpload />
        <Features />
        <Stats />
        <Testimonials />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}
