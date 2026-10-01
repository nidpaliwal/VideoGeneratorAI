import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ArrowRight, Video, Sparkles, Zap, Shield, Users, Film } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border sticky top-0 z-50 bg-background/95 backdrop-blur-sm">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 font-display font-bold text-xl text-primary">
            <Video className="w-6 h-6" />
            <span>VideoGen AI</span>
          </Link>
          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Features
            </Link>
            <Link href="#pricing" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
            <Link href="#how-it-works" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              How it Works
            </Link>
            <Link href="/media" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Media Library
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/auth/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Sign In
            </Link>
            <Link href="/auth/register">
              <Button size="sm">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 md:py-32 overflow-hidden">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6 animate-fade-in">
              <Sparkles className="w-4 h-4" />
              <span>New: AI-powered vertical video generation</span>
            </div>
            <h1 className="font-display text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6 animate-slide-up">
              Create Viral Shorts & Reels
              <br />
              <span className="text-primary">in Minutes, Not Hours</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto animate-slide-up" style={{ animationDelay: '100ms' }}>
              Turn any topic into engaging vertical videos for YouTube Shorts, Instagram Reels, and TikTok.
              AI script, voiceover, visuals, and captions — fully automated.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: '200ms' }}>
              <Link href="/auth/register">
                <Button size="lg" className="w-full sm:w-auto gap-2" style={{ padding: '1rem 2rem' }}>
                  Start Free — 3 Videos/Month
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link href="#how-it-works">
                <Button size="lg" variant="outline" className="w-full sm:w-auto" style={{ padding: '1rem 2rem' }}>
                  See How It Works
                </Button>
              </Link>
            </div>
            <p className="mt-6 text-sm text-muted-foreground animate-fade-in" style={{ animationDelay: '300ms' }}>
              No credit card required • Cancel anytime • 1000+ creators joined this month
            </p>
          </div>

          {/* Trust indicators */}
          <div className="mt-16 grid grid-cols-3 gap-8 max-w-4xl mx-auto animate-fade-in" style={{ animationDelay: '400ms' }}>
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-foreground">2min</div>
              <div className="text-sm text-muted-foreground mt-1">Avg Generation Time</div>
            </div>
            <div className="text-center p-4 border-x border-border">
              <div className="text-3xl font-bold text-foreground">9:16</div>
              <div className="text-sm text-muted-foreground mt-1">Perfect Vertical Format</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl font-bold text-foreground">$0.02</div>
              <div className="text-sm text-muted-foreground mt-1">Cost per Video (Stock)</div>
            </div>
          </div>
        </div>

        {/* Background decoration */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1.5s' }} />
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 md:py-28 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">Everything You Need</h2>
            <p className="text-lg text-muted-foreground">
              Complete pipeline from idea to published video — all in one workflow.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Sparkles,
                title: 'AI Script Generation',
                description: 'Enter a topic, get a structured short-form script with visual keywords and timing estimates. Edit or regenerate any section.',
              },
              {
                icon: Video,
                title: 'Pro Voiceovers',
                description: 'Choose from 50+ AI voices (ElevenLabs & Google). Adjust pace, preview per segment, regenerate instantly.',
              },
              {
                icon: Zap,
                title: 'Smart Visual Matching',
                description: 'Auto-search Pexels/Pixabay for vertical stock footage. Or generate AI scenes (premium). Drag to reorder.',
              },
              {
                icon: Shield,
                title: 'Animated Captions',
                description: 'Word-level karaoke highlighting, 4 animation styles, 4 fonts. Auto-synced from Whisper timestamps.',
              },
              {
                icon: Users,
                title: 'Background Music',
                description: 'Curated royalty-free library. Auto-ducking under voiceover. Volume control per track.',
              },
              {
                icon: ArrowRight,
                title: 'One-Click Export',
                description: '1080x1920 MP4, H.264, 30fps. Watermark-free on paid plans. Direct publish to YouTube/IG (v1.1).',
              },
            ].map((feature, i) => (
              <div key={i} className="group p-6 bg-card rounded-xl border border-border hover:border-primary/50 transition-all duration-300">
                <div className="w-12 h-12 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-4 group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                  <feature.icon className="w-6 h-6" />
                </div>
                <h3 className="font-display font-semibold text-lg mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">From Idea to Video in 4 Steps</h2>
            <p className="text-lg text-muted-foreground">
              Our streamlined workflow gets you from topic to published short in under 5 minutes.
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8 relative">
            {/* Connecting line */}
            <div className="hidden md:block absolute top-10 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-primary to-transparent -z-10" />

            {[
              { step: '01', title: 'Enter Topic', desc: 'Type any topic or paste your own script. AI generates a structured short-form script with segments.' },
              { step: '02', title: 'Choose Voice', desc: 'Pick from 50+ AI voices. Adjust speaking pace. Preview and regenerate per segment.' },
              { step: '03', title: 'Select Visuals', desc: 'Auto-matched stock footage or AI-generated scenes. Swap, reorder, choose style template.' },
              { step: '04', title: 'Export & Share', desc: 'Auto-captions with animations. Add music. Render 9:16 MP4. Download or publish directly.' },
            ].map((item, i) => (
              <div key={i} className="relative text-center">
                <div className="relative z-10 w-20 h-20 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary text-xl">
                  {item.step}
                </div>
                <h3 className="font-display font-semibold text-lg mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo/Preview */}
      <section className="py-20 md:py-28 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">See It in Action</h2>
            <p className="text-lg text-muted-foreground">
              Watch a 30-second demo of a faceless motivation short generated entirely by AI.
            </p>
          </div>
          <div className="max-w-md mx-auto aspect-[9/16] bg-dark-900 rounded-xl overflow-hidden border border-border shadow-2xl relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center p-8">
                <Video className="w-16 h-16 mx-auto mb-4 text-muted-foreground/50" />
                <p className="text-muted-foreground">Demo video player</p>
                <p className="text-xs text-muted-foreground/50 mt-2">Click to play generated short</p>
              </div>
            </div>
            {/* Play button overlay */}
            <button className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/50 transition-colors">
              <div className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center group-hover:bg-white/30 transition-colors">
                <ArrowRight className="w-8 h-8 text-white ml-1" />
              </div>
            </button>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
            <p className="text-lg text-muted-foreground">
              Start free. Upgrade when you're ready. No hidden fees.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: 'Free',
                price: '$0',
                period: '/month',
                credits: 3,
                features: [
                  '3 videos/month',
                  'Stock visuals only',
                  'Standard voices (Google TTS)',
                  'Basic caption styles',
                  'Watermarked exports',
                  'Community support',
                ],
                cta: 'Start Free',
                popular: false,
              },
              {
                name: 'Pro',
                price: '$19',
                period: '/month',
                credits: 50,
                features: [
                  '50 videos/month',
                  'Stock + AI visuals',
                  'Premium voices (ElevenLabs)',
                  'All caption animations',
                  'No watermark',
                  'Priority rendering',
                  'Email support',
                ],
                cta: 'Get Pro',
                popular: true,
              },
              {
                name: 'Creator',
                price: '$49',
                period: '/month',
                credits: 200,
                features: [
                  '200 videos/month',
                  'Unlimited AI visuals',
                  'Voice cloning (coming soon)',
                  'Custom caption fonts',
                  'No watermark',
                  'Highest priority',
                  'Dedicated support',
                  'API access (beta)',
                ],
                cta: 'Go Creator',
                popular: false,
              },
            ].map((plan) => (
              <div
                key={plan.name}
                className={`relative p-6 rounded-2xl border ${
                  plan.popular
                    ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10'
                    : 'border-border bg-card'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-primary text-primary-foreground text-xs font-medium rounded-full">
                    Most Popular
                  </div>
                )}
                <div className="text-center mb-6">
                  <h3 className="font-display font-semibold text-lg mb-2">{plan.name}</h3>
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="font-display text-4xl font-bold">{plan.price}</span>
                    <span className="text-muted-foreground">{plan.period}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">{plan.credits} credits/month</p>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm">
                      <span className="w-5 h-5 flex-shrink-0 flex items-center justify-center text-primary">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </span>
                      <span className="text-muted-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link href={`/auth/register?plan=${plan.name.toLowerCase()}`}>
                  <Button className="w-full" variant={plan.popular ? 'default' : 'outline'}>
                    {plan.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 md:py-28 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4 text-center">
          <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">Ready to Create Your First Video?</h2>
          <p className="text-lg text-primary-foreground/80 mb-8 max-w-2xl mx-auto">
            Join 1000+ creators making faceless shorts at scale. Your first 3 videos are free — no credit card needed.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/register">
              <Button size="lg" variant="secondary" className="w-full sm:w-auto gap-2" style={{ padding: '1rem 2rem' }}>
                Start Creating Free
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link href="/media">
              <Button size="lg" variant="outline" className="w-full sm:w-auto gap-2" style={{ padding: '1rem 2rem', borderColor: "rgba(255,255,255,0.3)", color: "white" }}>
                <Film className="w-4 h-4" />
                Try Media Library
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 bg-background">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-2">
              <Link href="/" className="flex items-center gap-2 font-display font-bold text-xl text-primary mb-4">
                <Video className="w-6 h-6" />
                <span>VideoGen AI</span>
              </Link>
              <p className="text-muted-foreground text-sm max-w-xs">
                The fastest way to create vertical short-form videos for YouTube Shorts, Instagram Reels, and TikTok using AI.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="#features" className="hover:text-foreground transition-colors">Features</Link></li>
                <li><Link href="#pricing" className="hover:text-foreground transition-colors">Pricing</Link></li>
                <li><Link href="/media" className="hover:text-foreground transition-colors">Media Library</Link></li>
                <li><Link href="/docs" className="hover:text-foreground transition-colors">Documentation</Link></li>
                <li><Link href="/api-docs" className="hover:text-foreground transition-colors">API Reference</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/about" className="hover:text-foreground transition-colors">About</Link></li>
                <li><Link href="/blog" className="hover:text-foreground transition-colors">Blog</Link></li>
                <li><Link href="/careers" className="hover:text-foreground transition-colors">Careers</Link></li>
                <li><Link href="/contact" className="hover:text-foreground transition-colors">Contact</Link></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-border flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">
              © 2024 VideoGen AI. All rights reserved.
            </p>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <Link href="/privacy" className="hover:text-foreground transition-colors">Privacy</Link>
              <Link href="/terms" className="hover:text-foreground transition-colors">Terms</Link>
              <Link href="/cookies" className="hover:text-foreground transition-colors">Cookies</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}