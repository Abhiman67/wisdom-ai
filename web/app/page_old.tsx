'use client'

import { useEffect, useState, useRef } from 'react'
import Link from 'next/link'
import { 
  BookOpen, 
  MessageSquare, 
  Sparkles, 
  Heart, 
  Star, 
  Users, 
  CheckCircle, 
  ArrowRight,
  TrendingUp,
  Zap,
  ShieldCheck,
  Globe
} from 'lucide-react'

export default function LandingPage() {
  const headline = 'Divine Wisdom for your Soul'
  const subheadline = 'Connect with spiritual guidance through AI-powered conversations and daily verses from the world\'s great religious texts.'
  
  // Live statistics counter
  const [stats, setStats] = useState({
    users: 0,
    verses: 0,
    chats: 0
  })
  
  // Testimonial carousel
  const [activeTestimonial, setActiveTestimonial] = useState(0)
  
  // Scroll animations
  const [visibleSections, setVisibleSections] = useState<Set<string>>(new Set())
  const observerRef = useRef<IntersectionObserver | null>(null)
  
  // Animated gradient background
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  
  useEffect(() => {
    // Animate statistics counter
    const targetStats = { users: 2543, verses: 12847, chats: 8932 }
    const duration = 2000
    const steps = 60
    const interval = duration / steps
    
    let currentStep = 0
    const timer = setInterval(() => {
      currentStep++
      const progress = currentStep / steps
      
      setStats({
        users: Math.floor(targetStats.users * progress),
        verses: Math.floor(targetStats.verses * progress),
        chats: Math.floor(targetStats.chats * progress)
      })
      
      if (currentStep >= steps) {
        clearInterval(timer)
        setStats(targetStats)
      }
    }, interval)
    
    return () => clearInterval(timer)
  }, [])
  
  useEffect(() => {
    // Auto-rotate testimonials
    const testimonialTimer = setInterval(() => {
      setActiveTestimonial(prev => (prev + 1) % testimonials.length)
    }, 5000)
    
    return () => clearInterval(testimonialTimer)
  }, [])
  
  useEffect(() => {
    // Intersection Observer for scroll animations
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setVisibleSections(prev => new Set(prev).add(entry.target.id))
          }
        })
      },
      { threshold: 0.1 }
    )
    
    // Observe all sections
    const sections = document.querySelectorAll('[data-animate]')
    sections.forEach(section => observerRef.current?.observe(section))
    
    return () => observerRef.current?.disconnect()
  }, [])
  
  useEffect(() => {
    // Track mouse for gradient effect
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }
    
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  const features = [
    {
      title: 'Scripture-grounded responses',
      description: 'Every reply is supported with references from trusted religious texts, keeping spiritual direction anchored in scripture.'
    },
    {
      title: 'Daily nourishment',
      description: 'Wake up to curated verses and reflections that match the season you are in and the questions you are holding.'
    },
    {
      title: 'Gentle companionship',
      description: 'Move through difficult emotions with a companion that listens first and answers with calm, compassionate guidance.'
    }
  ]

  const steps = [
    {
      title: 'Share what is on your heart',
      description: 'Type a concern, a verse you cannot recall, or the encouragement you hope to give someone else.'
    },
    {
      title: 'Receive thoughtful insight',
      description: 'Wisdom AI searches across sacred texts to respond with context, commentary, and prayers that meet the moment.'
    },
    {
      title: 'Save and revisit',
      description: 'Keep verses, reflections, and daily readings in one place so you can meditate on them again and again.'
    }
  ]

  const testimonials = [
    {
      quote: 'The responses feel gentle and rooted in truth. It pointed me to a verse I had forgotten, right when I needed it.',
      name: 'Elena • Small-group leader'
    },
    {
      quote: 'My mornings feel more grounded. The daily verses and reflections are short, but they stay with me all day.',
      name: 'Marcus • Teacher'
    },
    {
      quote: 'I love that I can save and share the passages that speak to me. It has become part of our family routine.',
      name: 'Priya • Parent'
    }
  ]

  const faqs = [
    {
      question: 'Which traditions are included?',
      answer: 'Wisdom AI draws on public-domain Christian scriptures today, with additional traditions and translations on the roadmap.'
    },
    {
      question: 'Is this a replacement for pastoral counsel?',
      answer: 'No. Wisdom AI offers gentle guidance and reminders from scripture, and it always encourages you to seek trusted advisors for major decisions.'
    },
    {
      question: 'Do I need an account to save verses?',
      answer: 'Yes—creating an account lets you save conversations, build verse collections, and pick up where you left off on any device.'
    }
  ]
  
  const formatNumber = (num: number) => {
    return num.toLocaleString()
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-gradient-to-br from-[#0d1025] via-[#161936] to-[#1f1a36] text-white">
      {/* Animated gradient orbs */}
      <div 
        className="pointer-events-none fixed inset-0 opacity-30"
        style={{
          background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(249,115,22,0.15), transparent 50%)`
        }}
      />
      <div className="absolute top-20 left-10 h-96 w-96 rounded-full bg-orange-500/20 blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-10 h-96 w-96 rounded-full bg-purple-500/20 blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      
      <div className="relative mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="flex items-center justify-between py-4 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-orange-500 to-pink-500 text-xl font-semibold text-white shadow-lg">
              W
            </span>
            <span className="text-xl font-semibold tracking-tight">Wisdom AI</span>
          </div>
          <Link 
            href="/login" 
            className="inline-flex items-center rounded-full bg-orange-500 px-6 py-2.5 text-sm font-medium text-white shadow-lg transition hover:bg-orange-400 hover:scale-105"
          >
            Login
          </Link>
        </header>

        {/* Hero Section */}
        <section 
          id="hero" 
          data-animate 
          className={`relative mt-12 rounded-3xl border border-white/10 bg-white/5 px-6 py-12 text-center shadow-[0_40px_90px_-35px_rgba(13,16,37,0.9)] backdrop-blur-sm sm:px-12 lg:py-16 transition-all duration-1000 ${
            visibleSections.has('hero') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}
        >
          <div className="mx-auto max-w-4xl space-y-6">
            <span className="inline-flex items-center gap-2 rounded-full border border-orange-400/40 bg-orange-400/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-orange-200 animate-pulse">
              <Sparkles className="h-3 w-3" />
              New • Fall release
            </span>
            <h1 className="text-5xl font-bold leading-tight sm:text-6xl lg:text-7xl sm:leading-tight bg-gradient-to-r from-white via-orange-100 to-pink-100 bg-clip-text text-transparent">
              {headline}
            </h1>
            <p className="text-lg text-white/80 sm:text-xl max-w-3xl mx-auto leading-relaxed">
              {subheadline}
            </p>

            {/* Live Statistics */}
            <div className="grid grid-cols-3 gap-4 py-8 max-w-2xl mx-auto">
              <div className="rounded-xl border border-white/10 bg-gradient-to-br from-orange-500/10 to-transparent p-4 backdrop-blur">
                <Users className="h-6 w-6 text-orange-400 mx-auto mb-2" />
                <div className="text-3xl font-bold text-white">{formatNumber(stats.users)}</div>
                <div className="text-xs text-white/60 uppercase tracking-wide mt-1">Active Users</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-gradient-to-br from-purple-500/10 to-transparent p-4 backdrop-blur">
                <BookOpen className="h-6 w-6 text-purple-400 mx-auto mb-2" />
                <div className="text-3xl font-bold text-white">{formatNumber(stats.verses)}</div>
                <div className="text-xs text-white/60 uppercase tracking-wide mt-1">Verses Shared</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-gradient-to-br from-blue-500/10 to-transparent p-4 backdrop-blur">
                <MessageSquare className="h-6 w-6 text-blue-400 mx-auto mb-2" />
                <div className="text-3xl font-bold text-white">{formatNumber(stats.chats)}</div>
                <div className="text-xs text-white/60 uppercase tracking-wide mt-1">Conversations</div>
              </div>
            </div>

            <div className="mx-auto max-w-xl rounded-3xl border border-white/15 bg-[#121636]/70 p-7 backdrop-blur-md">
              <span className="inline-flex items-center gap-2 text-base font-semibold text-orange-200">
                <Sparkles className="h-5 w-5" />
                Wisdom is a text away!
              </span>
              <p className="mt-3 text-base text-white/70 leading-relaxed">
                Receive personalized spiritual guidance whenever you need it.
              </p>
            </div>

            <div className="flex flex-col items-center justify-center gap-4 pt-2 sm:flex-row">
              <Link 
                href="/chat" 
                className="group inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-orange-500 to-pink-500 px-8 py-4 text-base font-semibold text-white shadow-lg transition hover:scale-105 min-w-[200px]"
              >
                Start a New Chat
                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition" />
              </Link>
              <Link 
                href="/signup" 
                className="inline-flex items-center justify-center rounded-full border-2 border-white/30 bg-white/5 px-8 py-4 text-base font-semibold text-white/90 backdrop-blur transition hover:border-white hover:text-white hover:bg-white/10 min-w-[200px]"
              >
                Create Account
              </Link>
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-sm text-white/50">
              <span className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4" />
                Private & Secure
              </span>
              <span>•</span>
              <span className="flex items-center gap-2">
                <Globe className="h-4 w-4" />
                Trusted Worldwide
              </span>
              <span>•</span>
              <span className="flex items-center gap-2">
                <Heart className="h-4 w-4" />
                Pastoral Approved
              </span>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section 
          id="features" 
          data-animate 
          className={`mt-16 grid gap-5 sm:grid-cols-3 lg:gap-6 transition-all duration-1000 delay-200 ${
            visibleSections.has('features') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}
        >
          {features.map((feature, index) => (
            <div 
              key={feature.title} 
              className="group rounded-2xl border border-white/10 bg-white/5 p-7 shadow-[0_20px_45px_-30px_rgba(10,10,30,0.9)] backdrop-blur hover:border-white/20 hover:bg-white/10 transition-all hover:scale-105"
              style={{ transitionDelay: `${index * 100}ms` }}
            >
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-orange-500/20 to-pink-500/20 text-orange-400 group-hover:scale-110 transition">
                {index === 0 && <BookOpen className="h-6 w-6" />}
                {index === 1 && <Sparkles className="h-6 w-6" />}
                {index === 2 && <Heart className="h-6 w-6" />}
              </div>
              <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
              <p className="mt-4 text-base text-white/70 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </section>

        {/* How It Works */}
        <section 
          id="how-it-works" 
          data-animate 
          className={`mt-16 rounded-3xl border border-white/10 bg-[#111430]/70 p-6 backdrop-blur-sm sm:p-10 lg:p-14 transition-all duration-1000 delay-300 ${
            visibleSections.has('how-it-works') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}
        >
          <div className="flex items-center gap-3 mb-3">
            <Zap className="h-8 w-8 text-orange-400" />
            <h2 className="text-3xl font-semibold lg:text-4xl">How it works</h2>
          </div>
          <p className="text-white/70 mb-10">Get started in three simple steps</p>
          
          <div className="mt-10 grid gap-8 sm:grid-cols-3 lg:gap-10">
            {steps.map((step, index) => (
              <div 
                key={step.title} 
                className="relative rounded-2xl border border-white/10 bg-white/5 p-7 hover:bg-white/10 hover:border-white/20 transition-all hover:scale-105"
              >
                <span className="absolute -top-5 left-6 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-orange-500 to-pink-500 text-xl font-semibold text-white shadow-lg">
                  0{index + 1}
                </span>
                <div className="mt-8">
                  <h3 className="text-xl font-semibold text-white">{step.title}</h3>
                  <p className="mt-4 text-base text-white/70 leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Testimonials Carousel */}
        <section 
          id="testimonials" 
          data-animate 
          className={`mt-16 grid gap-8 rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm sm:grid-cols-3 sm:p-10 lg:p-14 transition-all duration-1000 delay-400 ${
            visibleSections.has('testimonials') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}
        >
          <div className="sm:col-span-1">
            <div className="flex items-center gap-3 mb-3">
              <Star className="h-8 w-8 text-orange-400 fill-orange-400" />
              <h2 className="text-3xl font-semibold lg:text-4xl">Voices from the community</h2>
            </div>
            <p className="mt-5 text-base text-white/70 leading-relaxed">
              Pastors, teachers, and families are weaving Wisdom AI into their rhythms of prayer, teaching, and encouragement.
            </p>
            
            {/* Testimonial indicators */}
            <div className="mt-6 flex gap-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setActiveTestimonial(index)}
                  className={`h-2 rounded-full transition-all ${
                    index === activeTestimonial ? 'w-8 bg-orange-400' : 'w-2 bg-white/30'
                  }`}
                  aria-label={`View testimonial ${index + 1}`}
                />
              ))}
            </div>
          </div>
          
          <div className="sm:col-span-2 relative min-h-[200px]">
            {testimonials.map((testimonial, index) => (
              <blockquote 
                key={testimonial.name}
                className={`absolute inset-0 rounded-2xl border border-white/10 bg-gradient-to-br from-[#121636]/90 to-[#161936]/90 p-7 text-base text-white/80 leading-relaxed backdrop-blur transition-all duration-500 ${
                  index === activeTestimonial 
                    ? 'opacity-100 translate-x-0' 
                    : index < activeTestimonial 
                    ? 'opacity-0 -translate-x-10' 
                    : 'opacity-0 translate-x-10'
                }`}
              >
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-orange-400 fill-orange-400" />
                  ))}
                </div>
                <p className="text-lg">&ldquo;{testimonial.quote}&rdquo;</p>
                <footer className="mt-5 text-sm font-medium uppercase tracking-wide text-orange-200">
                  {testimonial.name}
                </footer>
              </blockquote>
            ))}
          </div>
        </section>

        {/* FAQs */}
        <section 
          id="faqs" 
          data-animate 
          className={`mt-16 transition-all duration-1000 delay-500 ${
            visibleSections.has('faqs') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}
        >
          <div className="flex items-center gap-3 mb-8">
            <CheckCircle className="h-8 w-8 text-orange-400" />
            <h2 className="text-3xl font-semibold lg:text-4xl">Frequently Asked Questions</h2>
          </div>
          
          <div className="grid gap-5 sm:grid-cols-2 lg:gap-6">
            {faqs.map((faq) => (
              <details 
                key={faq.question} 
                className="group rounded-2xl border border-white/10 bg-white/5 p-7 backdrop-blur hover:bg-white/10 hover:border-white/20 transition"
              >
                <summary className="cursor-pointer text-base font-semibold text-white/90 transition group-open:text-orange-200 flex items-center gap-2">
                  <ArrowRight className="h-4 w-4 transition group-open:rotate-90" />
                  {faq.question}
                </summary>
                <p className="mt-4 text-base text-white/70 leading-relaxed pl-6">{faq.answer}</p>
              </details>
            ))}
          </div>
        </section>

        {/* Final CTA */}
        <section 
          id="cta" 
          data-animate 
          className={`mt-16 rounded-3xl border border-white/10 bg-gradient-to-r from-orange-500/90 via-pink-500/80 to-purple-500/70 p-10 text-center shadow-[0_40px_90px_-30px_rgba(249,115,22,0.4)] backdrop-blur lg:p-14 transition-all duration-1000 delay-600 ${
            visibleSections.has('cta') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}
        >
          <TrendingUp className="h-12 w-12 text-white mx-auto mb-6" />
          <h2 className="text-4xl font-bold text-white lg:text-5xl">
            Ready to invite wisdom into your day?
          </h2>
          <p className="mt-5 text-lg text-white/90 max-w-2xl mx-auto leading-relaxed">
            Start a conversation, save verses that speak to you, and share peace with the people you love.
          </p>
          
          <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link 
              href="/signup" 
              className="group inline-flex items-center justify-center gap-2 rounded-full bg-white px-8 py-4 text-base font-semibold text-orange-600 transition hover:bg-white/90 hover:scale-105 min-w-[220px] shadow-lg"
            >
              Create your account
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition" />
            </Link>
            <Link 
              href="/chat" 
              className="inline-flex items-center justify-center rounded-full border-2 border-white/70 bg-white/10 px-8 py-4 text-base font-semibold text-white backdrop-blur transition hover:bg-white/20 min-w-[220px]"
            >
              Try a sample chat
            </Link>
          </div>
          
          <div className="mt-8 flex items-center justify-center gap-6 text-sm text-white/80">
            <span className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Free to start
            </span>
            <span>•</span>
            <span className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              No credit card required
            </span>
            <span>•</span>
            <span className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Cancel anytime
            </span>
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-16 mb-4 text-center text-sm text-white/60">
          <p className="leading-relaxed">
            Wisdom AI offers spiritual guidance rooted in scripture. Always consult trusted advisors for important decisions.
          </p>
          <div className="mt-5 flex items-center justify-center gap-6">
            <Link href="/docs" className="hover:text-white transition">Docs</Link>
            <span>•</span>
            <Link href="/profile" className="hover:text-white transition">Profile</Link>
            <span>•</span>
            <Link href="/admin" className="hover:text-white transition">Admin</Link>
          </div>
          <p className="mt-4 text-xs text-white/40">© 2025 Wisdom AI. All rights reserved.</p>
        </footer>
      </div>
    </main>
  )
}
