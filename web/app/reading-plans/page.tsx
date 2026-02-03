'use client'
import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/shell/sidebar'
import { apiClient } from '@/lib/api'
import { ReadingPlan, UserReadingPlan } from '@/types/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import dynamic from 'next/dynamic'

const BookOpenIcon = dynamic(() => import('lucide-react').then(m => m.BookOpen), { ssr: false })
const CheckCircleIcon = dynamic(() => import('lucide-react').then(m => m.CheckCircle), { ssr: false })
const ClockIcon = dynamic(() => import('lucide-react').then(m => m.Clock), { ssr: false })

export default function ReadingPlansPage() {
  const [availablePlans, setAvailablePlans] = useState<ReadingPlan[]>([])
  const [myPlans, setMyPlans] = useState<UserReadingPlan[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [plans, enrolled] = await Promise.all([
        apiClient.get<ReadingPlan[]>('/reading-plans'),
        apiClient.get<UserReadingPlan[]>('/my-reading-plans')
      ])
      setAvailablePlans(plans)
      setMyPlans(enrolled)
    } catch (error) {
      console.error('Failed to load reading plans:', error)
    } finally {
      setLoading(false)
    }
  }

  const enrollInPlan = async (planId: number) => {
    try {
      await apiClient.post(`/reading-plans/${planId}/enroll`, {})
      loadData()
    } catch (error) {
      console.error('Failed to enroll:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-white/60">Loading reading plans...</div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#1a1b2e] via-[#1e1f35] to-[#1a1b2e] text-white overflow-hidden">
      <Sidebar />
      
      <main className="flex flex-1 flex-col min-w-0 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
        
        <div className="flex-1 overflow-y-auto px-6 py-8 relative z-10">
          <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent mb-2">
              Reading Plans
            </h1>
            <p className="text-white/60 mb-8">Structured spiritual reading journeys</p>

            {myPlans.length > 0 && (
              <div className="mb-12">
                <h2 className="text-xl font-semibold mb-4">My Active Plans</h2>
                <div className="grid md:grid-cols-2 gap-6">
                  {myPlans.map((plan) => (
                    <Card key={plan.enrollment_id} className="bg-white/5 border-white/10 p-6">
                      <div className="flex items-start gap-3 mb-4">
                        <BookOpenIcon className="w-6 h-6 text-purple-400 flex-shrink-0" />
                        <div className="flex-1">
                          <h3 className="font-semibold text-white">{plan.plan_name}</h3>
                          <p className="text-sm text-white/60 mt-1">{plan.plan_description}</p>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-white/60">Progress</span>
                          <span className="text-white font-medium">
                            Day {plan.current_day} of {plan.duration_days}
                          </span>
                        </div>
                        <div className="w-full bg-white/10 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-orange-500 to-purple-600 h-2 rounded-full transition-all"
                            style={{ width: `${(plan.current_day / plan.duration_days) * 100}%` }}
                          />
                        </div>
                        {plan.completed && (
                          <div className="flex items-center gap-2 text-green-400 text-sm mt-2">
                            <CheckCircleIcon className="w-4 h-4" />
                            <span>Completed!</span>
                          </div>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            <div>
              <h2 className="text-xl font-semibold mb-4">Available Reading Plans</h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {availablePlans.map((plan) => {
                  const isEnrolled = myPlans.some(p => p.plan_name === plan.name)
                  
                  return (
                    <Card key={plan.id} className="bg-white/5 border-white/10 p-6">
                      <div className="flex items-start gap-3 mb-4">
                        <ClockIcon className="w-6 h-6 text-orange-400 flex-shrink-0" />
                        <div className="flex-1">
                          <h3 className="font-semibold text-white">{plan.name}</h3>
                          <p className="text-sm text-white/60 mt-1">{plan.description}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-white/60">{plan.duration_days} days</span>
                        <Button
                          size="sm"
                          disabled={isEnrolled}
                          onClick={() => enrollInPlan(plan.id)}
                          className={isEnrolled ? 'opacity-50' : 'bg-gradient-to-r from-orange-500 to-purple-600'}
                        >
                          {isEnrolled ? 'Enrolled' : 'Start Plan'}
                        </Button>
                      </div>
                    </Card>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
