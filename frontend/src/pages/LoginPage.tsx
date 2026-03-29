import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, Eye, EyeOff, Loader2, Video } from 'lucide-react'
import { Button, Input } from '@/components/ui'
import { authService } from '@/services/api'
import { useAuthStore } from '@/store/authStore'

export function LoginPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [mousePos, setMousePos] = useState({ x: -100, y: -100 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await authService.login({ email, password })
      setAuth(response.user, response.access, response.refresh)
      navigate('/')
    } catch (err) {
      setError('Credenciais inválidas. Verifique seu email e senha.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
      style={{ background: 'hsl(220 20% 4%)' }}
    >
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: 'linear-gradient(hsl(199 89% 48%) 1px, transparent 1px), linear-gradient(90deg, hsl(199 89% 48%) 1px, transparent 1px)',
          backgroundSize: '60px 60px',
        }}
      />

      {/* Mouse-following glow */}
      <div
        className="pointer-events-none fixed w-[500px] h-[500px] rounded-full blur-3xl opacity-20 transition-all duration-500 ease-out"
        style={{
          background: 'radial-gradient(circle, hsl(199 89% 48% / 0.5) 0%, hsl(199 89% 48% / 0.15) 50%, transparent 70%)',
          left: mousePos.x - 250,
          top: mousePos.y - 250,
        }}
      />

      {/* Ambient glow top-right */}
      <div className="absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl opacity-10"
        style={{ background: 'hsl(199 89% 48%)' }}
      />

      {/* Login card */}
      <div className="w-full max-w-md relative z-10 animate-fade-in">
        {/* Logo area */}
        <div className="text-center mb-8">
          <div className="mx-auto w-20 h-20 rounded-2xl flex items-center justify-center mb-5 border border-cyan-500/20 shadow-lg shadow-cyan-500/10"
            style={{ background: 'linear-gradient(135deg, hsl(220 20% 10%), hsl(220 20% 7%))' }}
          >
            <Shield className="w-10 h-10 text-cyan-400" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight" style={{ color: 'hsl(210 20% 95%)' }}>
            GT-Vision
          </h1>
          <p className="text-sm mt-2" style={{ color: 'hsl(215 10% 50%)' }}>
            Sistema de Videomonitoramento Inteligente
          </p>
        </div>

        {/* Form card */}
        <div className="rounded-2xl border backdrop-blur-sm shadow-2xl p-8"
          style={{
            background: 'hsl(220 20% 7% / 0.9)',
            borderColor: 'hsl(215 15% 14%)',
          }}
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="p-3 rounded-lg text-sm flex items-center gap-2"
                style={{
                  background: 'hsl(0 84% 60% / 0.1)',
                  border: '1px solid hsl(0 84% 60% / 0.2)',
                  color: 'hsl(0 84% 70%)',
                }}
              >
                <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium" style={{ color: 'hsl(210 20% 80%)' }}>
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                autoFocus
                className="h-11 bg-[hsl(220_20%_5%)] border-[hsl(215_15%_18%)] focus:border-cyan-500/50 focus:ring-cyan-500/20 text-[hsl(210_20%_95%)] placeholder:text-[hsl(215_10%_35%)]"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium" style={{ color: 'hsl(210 20% 80%)' }}>
                Senha
              </label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  className="h-11 pr-10 bg-[hsl(220_20%_5%)] border-[hsl(215_15%_18%)] focus:border-cyan-500/50 focus:ring-cyan-500/20 text-[hsl(210_20%_95%)] placeholder:text-[hsl(215_10%_35%)]"
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(215_10%_40%)] hover:text-cyan-400 transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full h-11 bg-cyan-600 hover:bg-cyan-500 text-white font-medium shadow-lg shadow-cyan-500/20 transition-all hover:shadow-cyan-500/30"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Entrando...
                </>
              ) : (
                'Entrar'
              )}
            </Button>
          </form>
        </div>

        {/* Footer */}
        <div className="mt-6 flex items-center justify-center gap-2 text-xs" style={{ color: 'hsl(215 10% 35%)' }}>
          <Video className="w-3.5 h-3.5" />
          <span>GTVision VMS v1.0</span>
        </div>
      </div>
    </div>
  )
}
