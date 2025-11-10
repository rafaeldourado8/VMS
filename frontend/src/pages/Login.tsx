// VMS/frontend/src/pages/Login.tsx
import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Mail, Lock, AlertCircle } from 'lucide-react'
import toast, { Toaster } from "react-hot-toast"
import { login, api } from "../lib/api" // Importa nosso cliente de API
import jwtDecode from "jwt-decode" // CORREÇÃO: import default

interface LoginProps {
  setIsAuthenticated: (value: boolean) => void
}

// Interface para o conteúdo do token decodificado
interface DecodedToken {
  user_id: number;
  exp: number;
  iat: number;
}

const Login: React.FC<LoginProps> = ({ setIsAuthenticated }) => {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      // 1. Chamar o endpoint de login
      const tokenData = await login(email, password)
      
      const { access, refresh } = tokenData
      
      if (!access || !refresh) {
        throw new Error("Token não recebido do servidor")
      }

      // 2. Decodificar o token de acesso para pegar o user_id
      const decoded = jwtDecode<DecodedToken>(access)
      const userId = decoded.user_id

      // 3. Salvar tokens no localStorage (necessário para a próxima chamada)
      localStorage.setItem("gt_vision_token", access)
      localStorage.setItem("gt_vision_refresh_token", refresh)

      // 4. Buscar os dados do usuário usando o ID do token
      // O backend em /api/users/{id}/
      const userData = await api.get(`/users/${userId}/`)

      // 5. Salvar dados do usuário no localStorage
      localStorage.setItem("gt_vision_user", JSON.stringify(userData))
      
      // 6. Atualizar estado e navegar
      setIsAuthenticated(true)
      toast.success("Login realizado com sucesso!")
      navigate("/dashboard")

    } catch (err: any) {
      setError(err.message || "Erro desconhecido")
      toast.error(err.message || "Erro ao fazer login")
      // Limpa tokens em caso de falha
      localStorage.removeItem("gt_vision_token")
      localStorage.removeItem("gt_vision_refresh_token")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-8">
      <Toaster position="top-right" />
      
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-800 rounded-xl mb-4">
            <span className="text-2xl font-bold text-white">GT</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">GT Vision</h1>
          <p className="text-gray-500 mt-2">Sistema de Monitoramento e Analytics</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Entrar</h2>
          
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-800 focus:border-transparent transition-all outline-none"
                  placeholder="seu@email.com"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Senha
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-800 focus:border-transparent transition-all outline-none"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-800 text-white py-3 rounded-lg font-medium hover:bg-blue-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Login