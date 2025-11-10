// VMS/frontend/src/components/Support.tsx
import React, { useState, useEffect } from "react"
import { LifeBuoy, Clock, Loader2, AlertCircle, Send } from 'lucide-react'
import { api } from "../lib/api"
import toast from "react-hot-toast"

// Interface para os dados de Mensagem da API
// Baseado em VMS/backend/apps/suporte/serializers.py
interface MessageData {
  id: number;
  autor_email: string;
  autor_id: number;
  conteudo: string;
  timestamp: string;
  respondido_por_admin: boolean;
}

const Support: React.FC = () => {
  const [messages, setMessages] = useState<MessageData[]>([])
  const [newMessage, setNewMessage] = useState("")
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const userDataString = localStorage.getItem("gt_vision_user")
  const currentUser = userDataString ? JSON.parse(userDataString) : null

  const fetchMessages = async () => {
    setLoading(true)
    setError(null)
    try {
      // O endpoint é /api/support/chat/
      const data: MessageData[] = await api.get("/support/chat/")
      setMessages(data.reverse()) // API retorna as mais novas primeiro
    } catch (err: any) {
      setError("Falha ao carregar mensagens.")
      toast.error("Falha ao carregar mensagens.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMessages()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim()) return

    setSending(true)
    try {
      // O endpoint de POST é /api/support/chat/
      // O backend define o autor automaticamente
      const postedMessage: MessageData = await api.post("/support/chat/", { 
        conteudo: newMessage 
      })
      setMessages([...messages, postedMessage]) // Adiciona a nova mensagem no final
      setNewMessage("")
      toast.success("Mensagem enviada!")
    } catch (err: any) {
      toast.error(`Falha ao enviar: ${err.message}`)
    } finally {
      setSending(false)
    }
  }
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    })
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Suporte</h1>
        <p className="text-gray-500 mt-1">Central de ajuda e atendimento</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-2xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <LifeBuoy className="w-5 h-5 text-blue-800" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Mensagens de Suporte</h2>
        </div>

        {/* Área de Mensagens */}
        <div className="h-96 overflow-y-auto space-y-4 p-4 bg-gray-50 rounded-lg mb-4">
          {loading && (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 text-blue-800 animate-spin" />
            </div>
          )}
          
          {error && (
            <div className="flex flex-col items-center justify-center h-full text-red-600">
              <AlertCircle className="w-8 h-8 mb-2" />
              <p>{error}</p>
            </div>
          )}

          {!loading && !error && messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <LifeBuoy className="w-12 h-12 mb-2 text-gray-300" />
              <p>Nenhuma mensagem ainda.</p>
              <p className="text-sm">Envie sua primeira mensagem abaixo.</p>
            </div>
          )}

          {!loading && !error && messages.map((message) => {
            const isMe = message.autor_id === currentUser?.id
            return (
              <div key={message.id} className={`flex ${isMe ? "justify-end" : "justify-start"}`}>
                <div className={`p-3 rounded-lg max-w-xs ${
                  isMe ? "bg-blue-800 text-white" : (message.respondido_por_admin ? "bg-gray-700 text-white" : "bg-gray-200 text-gray-900")
                }`}>
                  <p className="text-sm">{message.conteudo}</p>
                  <p className={`text-xs mt-2 opacity-70 ${isMe ? "text-right" : "text-left"}`}>
                    {message.respondido_por_admin ? "Admin" : (isMe ? "Você" : message.autor_email.split('@')[0])}
                    {' - '}
                    {formatDate(message.timestamp)}
                  </p>
                </div>
              </div>
            )
          })}
        </div>

        {/* Formulário de Envio */}
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            className="flex-1 w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-800 focus:border-transparent transition-all outline-none"
            placeholder="Digite sua mensagem..."
            disabled={sending}
          />
          <button
            type="submit"
            disabled={sending}
            className="w-12 h-12 bg-blue-800 text-white rounded-lg flex items-center justify-center hover:bg-blue-900 transition-colors disabled:opacity-50"
          >
            {sending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Support