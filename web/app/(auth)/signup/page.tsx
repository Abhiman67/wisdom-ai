"use client"
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { useMemo, useState } from 'react'
import { apiClient } from '@/lib/api'
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
  const { register, handleSubmit, watch, formState: { errors } } = useForm<SignupForm>({
    resolver: zodResolver(SignupSchema)
  })

  const onSubmit = async (data: SignupForm) => {
    try {
      setLoading(true)
      await apiClient.post('/signup', { name: data.name, email: data.email, password: data.password })
      router.push('/daily-verse')
    } catch (e: any) {
      alert(e?.message ?? 'Signup failed')
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
    <main className="relative flex min-h-screen items-center justify-center">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-violet-500/20 via-transparent to-transparent" />
      <div className="container flex items-center justify-center py-8">
      <Card className="w-full max-w-md backdrop-blur supports-[backdrop-filter]:bg-background/80">
        <CardHeader>
          <CardTitle>Create your account</CardTitle>
          <CardDescription>Join Wisdom AI</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input id="name" type="text" autoComplete="name" aria-invalid={!!errors.name} {...register('name')} className="mt-1" />
              {errors.name && <p className="mt-1 text-sm text-red-500">{errors.name.message}</p>}
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" autoComplete="email" aria-invalid={!!errors.email} {...register('email')} className="mt-1" />
              {errors.email && <p className="mt-1 text-sm text-red-500">{errors.email.message}</p>}
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <div className="relative mt-1">
                <Input id="password" type={showPassword ? 'text' : 'password'} autoComplete="new-password" aria-invalid={!!errors.password} {...register('password')} className="pr-10" />
                <button type="button" aria-label={showPassword ? 'Hide password' : 'Show password'} onClick={() => setShowPassword((s) => !s)} className="absolute inset-y-0 right-2 flex items-center text-muted-foreground hover:text-foreground">
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && <p className="mt-1 text-sm text-red-500">{errors.password.message}</p>}
              <div className="mt-2">
                <div className="h-1 w-full overflow-hidden rounded bg-muted">
                  <div className={`h-full transition-all ${strength>=1?'bg-red-500':''}`} style={{ width: `${(strength/4)*100}%` }} />
                </div>
                <p className="mt-1 text-xs text-muted-foreground">Use 8+ chars with a mix of uppercase, numbers, and symbols.</p>
              </div>
            </div>
            <div>
              <Label htmlFor="confirmPassword">Confirm password</Label>
              <div className="relative mt-1">
                <Input id="confirmPassword" type={showConfirm ? 'text' : 'password'} autoComplete="new-password" aria-invalid={!!errors.confirmPassword} {...register('confirmPassword')} className="pr-10" />
                <button type="button" aria-label={showConfirm ? 'Hide password' : 'Show password'} onClick={() => setShowConfirm((s) => !s)} className="absolute inset-y-0 right-2 flex items-center text-muted-foreground hover:text-foreground">
                  {showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.confirmPassword && <p className="mt-1 text-sm text-red-500">{errors.confirmPassword.message}</p>}
            </div>
            <label className="inline-flex items-center gap-2 text-sm">
              <input type="checkbox" className="h-4 w-4 rounded border" {...register('acceptTerms')} />
              I agree to the <a className="text-primary hover:underline" href="#" target="_blank" rel="noreferrer">Terms</a> and <a className="text-primary hover:underline" href="#" target="_blank" rel="noreferrer">Privacy</a>
            </label>
            <Button disabled={loading} className="w-full">
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" /> Creating…
                </span>
              ) : 'Create account'}
            </Button>
          </form>
          <p className="mt-4 text-sm">Already have an account? <Link className="text-primary" href="/login">Sign in</Link></p>
        </CardContent>
      </Card>
      </div>
    </main>
  )
}
