import { Hero1 } from '@/components/ui/hero-1'

export default function DocsPage() {
  return (
    <main className="min-h-screen p-8">
      <div className="container">
        <h1 className="mb-6 text-2xl font-semibold">Component preview & docs</h1>
        <section className="mb-12">
          <h2 className="mb-4 text-lg font-medium">Hero demo</h2>
          <div className="rounded-lg border bg-card p-4">
            <Hero1 />
          </div>
        </section>
        <section>
          <h2 className="mb-4 text-lg font-medium">How to use</h2>
          <ol className="list-decimal pl-6">
            <li>Install dependencies: <code>npm install lucide-react</code></li>
            <li>Import the component: <code>{`import { Hero1 } from '@/components/ui/hero-1'`}</code></li>
            <li>Use it inside a page or demo component</li>
          </ol>
        </section>
      </div>
    </main>
  )
}
