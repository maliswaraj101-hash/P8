'use client';

import { ArrowRight, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function CTA() {
  return (
    <section className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-accent/20 to-primary/20 filter blur-3xl opacity-30"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent/30 rounded-full filter blur-3xl opacity-40 animate-float"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-primary/30 rounded-full filter blur-3xl opacity-40 animate-float"></div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto text-center">
        <div className="bg-card border border-primary/30 rounded-2xl p-8 sm:p-16 backdrop-blur-sm animate-fade-in-scale">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full mb-6">
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary">
              Ready to Transform Your Audits?
            </span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-bold text-foreground mb-4 leading-tight">
            Start Your Free Trial Today
          </h2>

          <p className="text-lg text-foreground/60 max-w-2xl mx-auto mb-8">
            No credit card required. Get instant access to all premium features.
            Join thousands of satisfied audit professionals.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              size="lg"
              className="bg-gradient-to-r from-primary to-accent hover:opacity-90 text-white font-semibold px-10 w-full sm:w-auto group"
            >
              Get Started Free
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-border hover:bg-secondary px-10 w-full sm:w-auto bg-transparent"
            >
              Schedule Demo
            </Button>
          </div>

          <p className="text-sm text-foreground/50 mt-6">
            ✓ 14 days free trial • ✓ Full access to all features • ✓ Cancel anytime
          </p>
        </div>
      </div>
    </section>
  );
}
