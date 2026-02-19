import { useEffect, useRef } from 'react'
import { useAuthStore } from '@/store/authStore'

export function useInactivityTimeout(timeoutMinutes: number = 3) {
  const { logout, isAuthenticated } = useAuthStore()
  const timeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    if (!isAuthenticated) return

    const resetTimer = () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      
      timeoutRef.current = setTimeout(() => {
        logout()
        window.location.href = '/login'
      }, timeoutMinutes * 60 * 1000)
    }

    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'mousemove']
    events.forEach(event => window.addEventListener(event, resetTimer))
    
    resetTimer()

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      events.forEach(event => window.removeEventListener(event, resetTimer))
    }
  }, [isAuthenticated, timeoutMinutes, logout])
}
