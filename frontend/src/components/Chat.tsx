import React from "react"
import {MessageSquare} from 'lucide-react'

const Chat: React.FC = () => {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Chat</h1>
        <p className="text-gray-500 mt-1">Comunicação em tempo real</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-[600px] flex flex-col items-center justify-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
          <MessageSquare className="w-8 h-8 text-blue-800" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Chat em Desenvolvimento</h3>
        <p className="text-gray-500 text-center max-w-md">
          A funcionalidade de chat em tempo real será implementada em breve.
        </p>
      </div>
    </div>
  )
}

export default Chat
