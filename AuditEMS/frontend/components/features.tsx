'use client';

import {
  Zap,
  Shield,
  BarChart3,
  Clock,
  Brain,
  FileSearch,
} from 'lucide-react';

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Analysis',
    description:
      'Advanced machine learning algorithms analyze and extract key insights from your documents automatically.',
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description:
      'Process multiple documents in seconds with our optimized cloud infrastructure.',
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    description:
      'Bank-level encryption and compliance with international security standards.',
  },
  {
    icon: BarChart3,
    title: 'Detailed Reports',
    description:
      'Comprehensive audit reports with visualizations and actionable insights.',
  },
  {
    icon: Clock,
    title: 'Real-Time Processing',
    description:
      'Get instant results with live progress tracking for every document.',
  },
  {
    icon: FileSearch,
    title: 'Smart Search',
    description:
      'Find specific information across all documents with intelligent search.',
  },
];

export default function Features() {
  return (
    <section
      id="features"
      className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden"
    >
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-primary/10 rounded-full filter blur-3xl opacity-50"></div>
        <div className="absolute top-1/2 right-0 w-96 h-96 bg-accent/10 rounded-full filter blur-3xl opacity-40"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
            Powerful Features Built for Auditors
          </h2>
          <p className="text-lg text-foreground/60 max-w-2xl mx-auto">
            Everything you need to streamline your audit process with artificial
            intelligence
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="animate-fade-in-scale group"
                style={{
                  animationDelay: `${index * 50}ms`,
                }}
              >
                <div className="bg-card border border-border rounded-xl p-8 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 h-full">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center mb-4 group-hover:from-primary/30 group-hover:to-accent/30 transition-colors">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold text-foreground mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-foreground/60 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
