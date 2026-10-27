'use client';

import { Star } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

const testimonials = [
  {
    name: 'Sarah Johnson',
    role: 'Audit Director',
    company: 'Global Finance Inc',
    image: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah',
    text: 'AuditAI has reduced our audit processing time by 80%. The accuracy is remarkable and the team loves the intuitive interface.',
    rating: 5,
  },
  {
    name: 'Michael Chen',
    role: 'Compliance Officer',
    company: 'Enterprise Solutions',
    image: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Michael',
    text: 'The AI-powered insights have helped us identify compliance issues we would have missed. Game-changer for our organization.',
    rating: 5,
  },
  {
    name: 'Emma Rodriguez',
    role: 'CFO',
    company: 'Tech Innovations Ltd',
    image: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Emma',
    text: 'Implementation was seamless and the ROI was immediate. AuditAI is now a critical part of our financial operations.',
    rating: 5,
  },
];

export default function Testimonials() {
  return (
    <section
      id="testimonials"
      className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden"
    >
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/2 right-0 w-96 h-96 bg-accent/15 rounded-full filter blur-3xl opacity-50"></div>
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full filter blur-3xl opacity-40"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
            Loved by Audit Teams Worldwide
          </h2>
          <p className="text-lg text-foreground/60">
            See what industry leaders say about AuditAI
          </p>
        </div>

        {/* Testimonials grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div
              key={testimonial.name}
              className="animate-fade-in-scale group"
              style={{
                animationDelay: `${index * 100}ms`,
              }}
            >
              <div className="bg-card border border-border rounded-xl p-8 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 h-full flex flex-col">
                {/* Stars */}
                <div className="flex gap-1 mb-4">
                  {Array.from({ length: testimonial.rating }).map((_, i) => (
                    <Star
                      key={i}
                      className="w-5 h-5 fill-yellow-400 text-yellow-400"
                    />
                  ))}
                </div>

                {/* Quote */}
                <p className="text-foreground/80 leading-relaxed mb-6 flex-1">
                  "{testimonial.text}"
                </p>

                {/* Author */}
                <div className="flex items-center gap-4 pt-6 border-t border-border/50">
                  <Avatar>
                    <AvatarImage src={testimonial.image || "/placeholder.svg"} alt={testimonial.name} />
                    <AvatarFallback>{testimonial.name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold text-foreground">
                      {testimonial.name}
                    </p>
                    <p className="text-sm text-foreground/60">
                      {testimonial.role} at {testimonial.company}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
