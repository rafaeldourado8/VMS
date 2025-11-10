// frontend/src/main.tsx
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './index.css'

// Log simples para depuração (aparece no console)
console.log('Inicializando app React...')

const container = document.getElementById('root')
if (!container) {
  console.error('Elemento #root não encontrado')
} else {
  const root = createRoot(container)
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  )
}