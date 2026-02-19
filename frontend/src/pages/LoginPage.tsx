import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Camera, Eye, EyeOff, Loader2 } from 'lucide-react'
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/ui'
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
    <div className="min-h-screen flex items-center justify-center p-4 bg-black relative overflow-hidden">
      <div 
        className="pointer-events-none fixed w-96 h-96 rounded-full blur-3xl opacity-40 transition-all duration-300 ease-out"
        style={{
          background: 'radial-gradient(circle, rgba(168, 85, 247, 0.6) 0%, rgba(139, 92, 246, 0.3) 50%, transparent 70%)',
          left: mousePos.x - 192,
          top: mousePos.y - 192
        }}
      />
      
      <Card className="w-full max-w-md relative z-10 bg-zinc-950/90 border-zinc-800/50 backdrop-blur-sm shadow-2xl group">
        <CardHeader className="text-center pb-2">
          <div className="mx-auto w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-4 group-hover:border-purple-900/50 transition-colors">
            <Camera className="w-8 h-8 text-zinc-400 group-hover:text-purple-400 transition-colors" />
          </div>
          <CardTitle className="text-2xl text-zinc-100">GT-Vision VMS</CardTitle>
          <p className="text-sm text-zinc-500 mt-1">
            Sistema de Videomonitoramento Inteligente
          </p>
        </CardHeader>

        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-950/30 border border-red-900/30 text-sm text-red-400">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-zinc-300">
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
                className="bg-zinc-900/50 border-zinc-800 focus:border-purple-900/50 text-zinc-100 placeholder:text-zinc-600"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-zinc-300">
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
                  className="pr-10 bg-zinc-900/50 border-zinc-800 focus:border-purple-900/50 text-zinc-100 placeholder:text-zinc-600"
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-purple-400 transition-colors"
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
              className="w-full bg-zinc-900 hover:bg-purple-950/50 border border-zinc-800 hover:border-purple-900/50 text-zinc-100 transition-all"
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
        </CardContent>
      </Card>
    </div>
  )
}
