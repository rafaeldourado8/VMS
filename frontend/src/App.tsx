import React, { useState, useEffect } from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
import CamerasPage from "./pages/Cameras" // nova rota - ajuste o caminho se necessário

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check if user is authenticated on mount
    const token = localStorage.getItem("gt_vision_token")
    setIsAuthenticated(!!token)
  }, [])

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={
            isAuthenticated ? <Navigate to="/dashboard" /> : <Login setIsAuthenticated={setIsAuthenticated} />
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            isAuthenticated ? <Dashboard setIsAuthenticated={setIsAuthenticated} /> : <Navigate to="/login" />
          } 
        />
        <Route
          path="/cameras"
          element={
            isAuthenticated ? <CamerasPage /> : <Navigate to="/login" />
          }
        />
        <Route 
          path="/" 
          element={isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} 
        />
      </Routes>
    </Router>
  )
}

export default App