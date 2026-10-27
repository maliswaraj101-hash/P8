'use client';

import { ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden px-4 sm:px-6 lg:px-8 pt-20 pb-10">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full filter blur-3xl animate-float opacity-30"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/20 rounded-full filter blur-3xl animate-float opacity-30 animation-delay-2000"></div>
        <div className="absolute top-1/2 right-0 w-96 h-96 bg-primary/10 rounded-full filter blur-3xl animate-pulse-slow opacity-20"></div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto text-center space-y-8 animate-fade-in-up">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full">
          <Sparkles className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-primary">
            AI-Powered Intelligence
          </span>
        </div>

        {/* Main Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold text-foreground leading-tight">
          <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
            Audit Management
          </span>
          <br />
          <span className="text-foreground">Reimagined for the AI Era</span>
        </h1>

        {/* Subheadline */}
        <p className="text-lg sm:text-xl text-foreground/60 max-w-2xl mx-auto leading-relaxed">
          Submit multiple documents and let our intelligent AI system analyze,
          categorize, and provide comprehensive audit reports in seconds. Security,
          speed, and precision combined.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
          <Button
            size="lg"
            className="bg-gradient-to-r from-primary to-accent hover:opacity-90 text-white font-semibold px-8 w-full sm:w-auto group"
          >
            Start Free Trial
            <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-border hover:bg-secondary px-8 w-full sm:w-auto bg-transparent"
          >
            Watch Demo
          </Button>
        </div>

        {/* Trust indicators */}
        <div className="pt-12 border-t border-border/50">
          <p className="text-sm text-foreground/50 mb-6">
            Trusted by leading organizations worldwide
          </p>
          <div className="flex flex-wrap items-center justify-center gap-8">
            {['Acme Corp', 'Enterprise Co', 'Global Inc'].map((company) => (
              <div
                key={company}
                className="text-foreground/40 font-semibold text-sm sm:text-base"
              >
                {company}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-primary/30 rounded-full flex items-center justify-center">
          <div className="w-1 h-2 bg-primary/50 rounded-full animate-pulse"></div>
        </div>
      </div>
    </section>
  );
}
