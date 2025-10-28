import Link from 'next/link'

export const metadata = {
  title: 'Wisdom AI — Gentle guidance and contextual verses',
  description: 'Ask Wisdom AI for thoughtful, verse-backed guidance. Daily verses, personal reflections, and a calming conversational assistant.',
}


export default function LandingPage() {
  const headline = 'Divine Wisdom for your Soul'
  const subheadline = 'Connect with spiritual guidance through AI-powered conversations and daily verses from the world’s great religious texts.'

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

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#0d1025] via-[#161936] to-[#1f1a36] text-white">
      <div className="mx-auto w-full max-w-6xl px-6 py-10">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-full bg-orange-500 text-lg font-semibold text-white shadow-lg">W</span>
            <span className="text-lg font-semibold tracking-tight">Wisdom AI</span>
          </div>
          <Link href="/login" className="inline-flex items-center rounded-full bg-orange-500 px-5 py-2 text-sm font-medium text-white shadow transition hover:bg-orange-400">Login</Link>
        </header>

        <section className="relative mt-16 rounded-3xl border border-white/10 bg-white/5 px-8 py-16 text-center shadow-[0_40px_90px_-35px_rgba(13,16,37,0.9)] sm:px-14">
          <div className="mx-auto max-w-3xl space-y-8">
            <span className="inline-flex items-center gap-2 rounded-full border border-orange-400/40 bg-orange-400/10 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-orange-200">New • Fall release</span>
            <h1 className="text-4xl font-bold leading-tight sm:text-5xl sm:leading-tight">{headline}</h1>
            <p className="text-base text-white/80 sm:text-lg">{subheadline}</p>

            <div className="mx-auto max-w-lg rounded-3xl border border-white/15 bg-[#121636]/70 p-6 backdrop-blur">
              <span className="inline-flex items-center gap-2 text-sm font-semibold text-orange-200">
                <span className="text-lg">✨</span>
                Wisdom is a text away!
              </span>
              <p className="mt-3 text-sm text-white/70">Receive personalized spiritual guidance whenever you need it.</p>
            </div>

            <div className="flex flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4">
              <Link href="/chat" className="inline-flex items-center justify-center rounded-full bg-orange-500 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-orange-400 min-w-[170px]">Start a New Chat</Link>
              <Link href="/signup" className="inline-flex items-center justify-center rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white/90 transition hover:border-white hover:text-white min-w-[170px]">Create Account</Link>
            </div>

            <div className="mt-10 flex flex-wrap items-center justify-center gap-4 text-xs text-white/50">
              <span>✨ Trusted by small groups</span>
              <span>•</span>
              <span>📿 Crafted with pastoral input</span>
              <span>•</span>
              <span>🔒 Private and secure</span>
            </div>
          </div>
        </section>

        <section className="mt-24 grid gap-6 sm:grid-cols-3">
          {features.map(feature => (
            <div key={feature.title} className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-[0_20px_45px_-30px_rgba(10,10,30,0.9)]">
              <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
              <p className="mt-3 text-sm text-white/70">{feature.description}</p>
            </div>
          ))}
        </section>

        <section className="mt-24 rounded-3xl border border-white/10 bg-[#111430]/70 p-8 backdrop-blur sm:p-12">
          <h2 className="text-2xl font-semibold">How it works</h2>
          <div className="mt-8 grid gap-10 sm:grid-cols-3">
            {steps.map((step, index) => (
              <div key={step.title} className="relative rounded-2xl border border-white/10 bg-white/5 p-6">
                <span className="absolute -top-5 left-6 flex h-10 w-10 items-center justify-center rounded-full bg-orange-500 text-lg font-semibold text-white shadow">0{index + 1}</span>
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-white">{step.title}</h3>
                  <p className="mt-3 text-sm text-white/70">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-24 grid gap-8 rounded-3xl border border-white/10 bg-white/5 p-8 sm:grid-cols-3 sm:p-12">
          <div className="sm:col-span-1">
            <h2 className="text-2xl font-semibold">Voices from the community</h2>
            <p className="mt-4 text-sm text-white/70">Pastors, teachers, and families are weaving Wisdom AI into their rhythms of prayer, teaching, and encouragement.</p>
          </div>
          <div className="sm:col-span-2 grid gap-6">
            {testimonials.map(testimonial => (
              <blockquote key={testimonial.name} className="rounded-2xl border border-white/10 bg-[#121636]/80 p-6 text-sm text-white/80">
                “{testimonial.quote}”
                <footer className="mt-4 text-xs uppercase tracking-wide text-orange-200">{testimonial.name}</footer>
              </blockquote>
            ))}
          </div>
        </section>

        <section className="mt-24 grid gap-6 sm:grid-cols-2">
          {faqs.map(faq => (
            <details key={faq.question} className="group rounded-2xl border border-white/10 bg-white/5 p-6">
              <summary className="cursor-pointer text-sm font-semibold text-white/90 transition group-open:text-orange-200">{faq.question}</summary>
              <p className="mt-3 text-sm text-white/70">{faq.answer}</p>
            </details>
          ))}
        </section>

        <section className="mt-24 rounded-3xl border border-white/10 bg-gradient-to-r from-orange-500/90 to-pink-500/70 p-10 text-center shadow-[0_40px_90px_-30px_rgba(255,140,66,0.3)]">
          <h2 className="text-3xl font-bold text-white">Ready to invite wisdom into your day?</h2>
          <p className="mt-4 text-sm text-white/80">Start a conversation, save verses that speak to you, and share peace with the people you love.</p>
          <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4">
            <Link href="/signup" className="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-orange-600 transition hover:bg-white/90">Create your account</Link>
            <Link href="/chat" className="inline-flex items-center justify-center rounded-full border border-white/60 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/20">Try a sample chat</Link>
          </div>
        </section>

        <footer className="mt-24 mb-6 text-center text-xs text-white/60">
          <p>Wisdom AI offers spiritual guidance rooted in scripture. Always consult trusted advisors for important decisions.</p>
          <div className="mt-4 flex items-center justify-center gap-4">
            <Link href="/docs" className="hover:text-white">Docs</Link>
            <Link href="/profile" className="hover:text-white">Profile</Link>
            <Link href="/admin" className="hover:text-white">Admin</Link>
          </div>
        </footer>
      </div>
    </main>
  )
}

