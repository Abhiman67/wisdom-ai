"use client"
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Link from 'next/link'

const Schema = z.object({
  email: z.string().email('Enter a valid email')
})

type FormData = z.infer<typeof Schema>

export default function ForgotPasswordPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({ resolver: zodResolver(Schema) })
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const onSubmit = async (data: FormData) => {
    try {
      setLoading(true)
      await fetch('/api/forgot-password', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
      setSubmitted(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-violet-500/20 via-transparent to-transparent" />
      <div className="container flex items-center justify-center py-8">
        <div className="w-full max-w-md rounded-lg border bg-background/80 p-6 backdrop-blur supports-[backdrop-filter]:bg-background/80">
          <h1 className="text-xl font-semibold tracking-tight">Forgot password</h1>
          <p className="mt-1 text-sm text-muted-foreground">Enter your email and well send you a reset link if it exists.</p>

          {submitted ? (
            <div className="mt-6 rounded-md border bg-muted/40 p-4 text-sm">
              If an account exists for that email, youll receive instructions shortly.
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
              <div>
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" autoComplete="email" aria-invalid={!!errors.email} {...register('email')} className="mt-1" />
                {errors.email && <p className="mt-1 text-sm text-red-500">{errors.email.message}</p>}
              </div>
              <Button disabled={loading} className="w-full">{loading ? 'Sending…' : 'Send reset link'}</Button>
            </form>
          )}

          <p className="mt-6 text-center text-sm"><Link className="text-primary hover:underline" href="/login">Back to login</Link></p>
        </div>
      </div>
    </main>
  )
}
