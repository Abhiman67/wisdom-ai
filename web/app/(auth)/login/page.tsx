"use client"
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const LoginSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(6, 'At least 6 characters'),
  remember: z.boolean().optional().default(false)
})

type LoginForm = z.infer<typeof LoginSchema>

export default function LoginPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(LoginSchema)
  })

  const onSubmit = async (data: LoginForm) => {
    try {
      setLoading(true)
      // Call Next API route which sets httpOnly auth cookie
      await apiClient.post('/login', { email: data.email, password: data.password, remember: data.remember })
      router.push('/dashboard')
    } catch (e: any) {
      alert(e?.message ?? 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center bg-gradient-to-br from-[#0d1025] via-[#161936] to-[#1f1a36]">
      {/* Animated background orbs */}
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div className="absolute top-20 left-20 h-96 w-96 rounded-full bg-orange-500/30 blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 h-96 w-96 rounded-full bg-purple-500/30 blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>
      
      <div className="container relative z-10 flex items-center justify-center py-8">
      <Card className="w-full max-w-md border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl">
        <CardHeader className="space-y-2">
          <div className="flex items-center justify-center mb-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500 to-pink-500 text-xl font-bold text-white shadow-lg">
              W
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">Welcome Back</CardTitle>
          <CardDescription className="text-center text-white/60">Sign in to continue your spiritual journey</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <Label htmlFor="email" className="text-white/90">Email</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                aria-invalid={!!errors.email}
                aria-describedby={errors.email ? 'email-error' : undefined}
                {...register('email')}
                className="mt-2 bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-orange-500/50 focus:ring-orange-500/20"
              />
              {errors.email && <p className="mt-1.5 text-sm text-red-400">{errors.email.message}</p>}
            </div>
            <div>
              <Label htmlFor="password" className="text-white/90">Password</Label>
              <div className="relative mt-2">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  aria-invalid={!!errors.password}
                  aria-describedby={errors.password ? 'password-error' : undefined}
                  {...register('password')}
                  className="pr-10 bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-orange-500/50 focus:ring-orange-500/20"
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  onClick={() => setShowPassword((s) => !s)}
                  className="absolute inset-y-0 right-2 flex items-center text-white/40 hover:text-white/70 transition"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && <p className="mt-1.5 text-sm text-red-400">{errors.password.message}</p>}
            </div>
            <div className="flex items-center justify-between">
              <label className="inline-flex items-center gap-2 text-sm text-white/80 cursor-pointer">
                <input type="checkbox" className="h-4 w-4 rounded border-white/20 bg-white/5 text-orange-500 focus:ring-orange-500/20" {...register('remember')} />
                Remember me
              </label>
              <Link href="/forgot-password" className="text-sm text-orange-400 hover:text-orange-300 transition">Forgot password?</Link>
            </div>
            <Button disabled={loading} className="w-full bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white font-semibold py-6 shadow-lg hover:shadow-xl transition-all">
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" /> Signing in…
                </span>
              ) : 'Sign in'}
            </Button>
          </form>
          <p className="mt-6 text-center text-sm text-white/60">Don&apos;t have an account? <Link className="text-orange-400 hover:text-orange-300 font-semibold transition" href="/signup">Sign up</Link></p>
        </CardContent>
      </Card>
      </div>
    </main>
  )
}
