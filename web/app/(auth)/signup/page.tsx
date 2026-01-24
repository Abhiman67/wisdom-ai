"use client"
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { useMemo, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Eye, EyeOff, Loader2 } from 'lucide-react'

const SignupSchema = z.object({
  name: z.string().min(2, 'At least 2 characters'),
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'At least 8 characters').regex(/[A-Z]/, 'Add an uppercase letter').regex(/[0-9]/, 'Add a number').regex(/[^A-Za-z0-9]/, 'Add a symbol'),
  confirmPassword: z.string().min(1, 'Confirm your password'),
  acceptTerms: z.literal(true, {
    errorMap: () => ({ message: 'You must accept the terms' })
  })
}).refine((data) => data.password === data.confirmPassword, {
  path: ['confirmPassword'],
  message: 'Passwords must match'
})

type SignupForm = z.infer<typeof SignupSchema>

export default function SignupPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const supabase = createClient()
  
  const { register, handleSubmit, watch, formState: { errors } } = useForm<SignupForm>({
    resolver: zodResolver(SignupSchema)
  })

  const onSubmit = async (data: SignupForm) => {
    try {
      setLoading(true)
      setError(null)
      
      const { error } = await supabase.auth.signUp({
        email: data.email,
        password: data.password,
        options: {
          data: {
            name: data.name,
          },
        },
      })
      
      if (error) {
        setError(error.message)
        return
      }
      
      setSuccess(true)
      // Auto redirect after signup
      setTimeout(() => {
        router.push('/dashboard')
        router.refresh()
      }, 1500)
    } catch (e: any) {
      setError(e?.message ?? 'Signup failed')
    } finally {
      setLoading(false)
    }
  }

  const passwordValue = watch('password') || ''
  const strength = useMemo(() => {
    let score = 0
    if (passwordValue.length >= 8) score++
    if (/[A-Z]/.test(passwordValue)) score++
    if (/[0-9]/.test(passwordValue)) score++
    if (/[^A-Za-z0-9]/.test(passwordValue)) score++
    return score // 0-4
  }, [passwordValue])

  return (
    <main className="relative flex min-h-screen items-center justify-center bg-gradient-to-br from-[#0d1025] via-[#161936] to-[#1f1a36]">
      {/* Animated background orbs */}
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div className="absolute top-20 right-20 h-96 w-96 rounded-full bg-orange-500/30 blur-3xl animate-pulse" />
        <div className="absolute bottom-20 left-20 h-96 w-96 rounded-full bg-purple-500/30 blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>
      
      <div className="container relative z-10 flex items-center justify-center py-8">
      <Card className="w-full max-w-md border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl">
        <CardHeader className="space-y-2">
          <div className="flex items-center justify-center mb-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500 to-pink-500 text-xl font-bold text-white shadow-lg">
              W
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">Create your account</CardTitle>
          <CardDescription className="text-center text-white/60">Join Wisdom AI and start your journey</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <Label htmlFor="name" className="text-white/90">Name</Label>
              <Input 
                id="name" 
                type="text" 
                autoComplete="name" 
                placeholder="Your full name"
                aria-invalid={!!errors.name} 
                {...register('name')} 
                className="mt-2 bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-orange-500/50 focus:ring-orange-500/20" 
              />
              {errors.name && <p className="mt-1.5 text-sm text-red-400">{errors.name.message}</p>}
            </div>
            <div>
              <Label htmlFor="email" className="text-white/90">Email</Label>
              <Input 
                id="email" 
                type="email" 
                autoComplete="email" 
                placeholder="you@example.com"
                aria-invalid={!!errors.email} 
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
                  autoComplete="new-password" 
                  placeholder="••••••••"
                  aria-invalid={!!errors.password} 
                  {...register('password')} 
                  className="pr-10 bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-orange-500/50 focus:ring-orange-500/20" 
                />
                <button type="button" aria-label={showPassword ? 'Hide password' : 'Show password'} onClick={() => setShowPassword((s) => !s)} className="absolute inset-y-0 right-2 flex items-center text-white/40 hover:text-white/70 transition">
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && <p className="mt-1.5 text-sm text-red-400">{errors.password.message}</p>}
              <div className="mt-2">
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
                  <div 
                    className={`h-full transition-all ${
                      strength === 0 ? 'bg-red-500' :
                      strength === 1 ? 'bg-orange-500' :
                      strength === 2 ? 'bg-yellow-500' :
                      strength === 3 ? 'bg-lime-500' :
                      'bg-green-500'
                    }`} 
                    style={{ width: `${(strength/4)*100}%` }} 
                  />
                </div>
                <p className="mt-1.5 text-xs text-white/50">Use 8+ chars with uppercase, numbers, and symbols.</p>
              </div>
            </div>
            <div>
              <Label htmlFor="confirmPassword" className="text-white/90">Confirm password</Label>
              <div className="relative mt-2">
                <Input 
                  id="confirmPassword" 
                  type={showConfirm ? 'text' : 'password'} 
                  autoComplete="new-password" 
                  placeholder="••••••••"
                  aria-invalid={!!errors.confirmPassword} 
                  {...register('confirmPassword')} 
                  className="pr-10 bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-orange-500/50 focus:ring-orange-500/20" 
                />
                <button type="button" aria-label={showConfirm ? 'Hide password' : 'Show password'} onClick={() => setShowConfirm((s) => !s)} className="absolute inset-y-0 right-2 flex items-center text-white/40 hover:text-white/70 transition">
                  {showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.confirmPassword && <p className="mt-1.5 text-sm text-red-400">{errors.confirmPassword.message}</p>}
            </div>
            <label className="inline-flex items-start gap-2.5 text-sm text-white/80 cursor-pointer">
              <input type="checkbox" className="mt-0.5 h-4 w-4 rounded border-white/20 bg-white/5 text-orange-500 focus:ring-orange-500/20" {...register('acceptTerms')} />
              <span>I agree to the <a className="text-orange-400 hover:text-orange-300 transition underline" href="#" target="_blank" rel="noreferrer">Terms</a> and <a className="text-orange-400 hover:text-orange-300 transition underline" href="#" target="_blank" rel="noreferrer">Privacy Policy</a></span>
            </label>
            {errors.acceptTerms && <p className="text-sm text-red-400">{errors.acceptTerms.message}</p>}
            <Button disabled={loading} className="w-full bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white font-semibold py-6 shadow-lg hover:shadow-xl transition-all">
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" /> Creating…
                </span>
              ) : 'Create account'}
            </Button>
          </form>
          <p className="mt-6 text-center text-sm text-white/60">Already have an account? <Link className="text-orange-400 hover:text-orange-300 font-semibold transition" href="/login">Sign in</Link></p>
        </CardContent>
      </Card>
      </div>
    </main>
  )
}
