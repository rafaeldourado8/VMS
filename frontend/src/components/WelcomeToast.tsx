import { useEffect, useState } from 'react'
import { X, Bot } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

export function WelcomeToast() {
  const { user, isAuthenticated } = useAuthStore()
  const [show, setShow] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!isAuthenticated || !user) return

    // Verificar se é primeiro login da sessão
    const lastLoginTime = localStorage.getItem('last-login-time')
    const now = Date.now()
    const isFirstLogin = !lastLoginTime || (now - parseInt(lastLoginTime)) > 3600000 // 1 hora

    // Definir mensagem
    const hour = new Date().getHours()
    let greeting = ''
    if (hour < 12) greeting = 'Bom dia'
    else if (hour < 18) greeting = 'Boa tarde'
    else greeting = 'Boa noite'

    if (isFirstLogin) {
      setMessage(`Olá, ${greeting.toLowerCase()} ${user.name}!`)
      localStorage.setItem('last-login-time', now.toString())
    } else {
      setMessage(`Olá, bem-vindo de volta ${user.name}!`)
    }

    // Mostrar toast
    setTimeout(() => setShow(true), 500)
    
    // Auto-fechar após 5 segundos
    const timer = setTimeout(() => setShow(false), 5500)
    
    return () => clearTimeout(timer)
  }, [isAuthenticated, user])

  if (!show || !user) return null

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-in slide-in-from-right duration-300">
      <div className="bg-card border border-border rounded-xl shadow-2xl p-4 pr-12 min-w-[320px] max-w-md backdrop-blur-sm">
        <button
          onClick={() => setShow(false)}
          className="absolute top-3 right-3 text-muted-foreground hover:text-foreground transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
        
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center flex-shrink-0">
            <Bot className="w-5 h-5 text-primary-foreground" />
          </div>
          
          <div>
            <p className="font-semibold text-foreground">
              {message}
            </p>
            <p className="text-sm text-muted-foreground mt-0.5">
              GT-Vision VMS
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
