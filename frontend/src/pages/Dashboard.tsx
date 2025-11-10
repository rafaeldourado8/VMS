import React, { useState } from "react"
import Sidebar from "../components/Sidebar"
import DashboardHome from "../components/DashboardHome"
import Cameras from "../components/Cameras"
import Detections from "../components/Detections"
import Analytics from "../components/Analytics"
import Support from "../components/Support"
import Chat from "../components/Chat"
import Users from "../components/Users"
import Settings from "../components/Settings"

interface DashboardProps {
  setIsAuthenticated: (value: boolean) => void
}

const Dashboard: React.FC<DashboardProps> = ({ setIsAuthenticated }) => {
  const [currentPage, setCurrentPage] = useState("dashboard")

  const renderContent = () => {
    switch (currentPage) {
      case "dashboard":
        return <DashboardHome />
      case "cameras":
        return <Cameras />
      case "detections":
        return <Detections />
      case "analytics":
        return <Analytics />
      case "support":
        return <Support />
      case "chat":
        return <Chat />
      case "users":
        return <Users />
      case "settings":
        return <Settings />
      default:
        return <DashboardHome />
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage}
        setIsAuthenticated={setIsAuthenticated}
      />
      
      <main className="flex-1 overflow-y-auto">
        {renderContent()}
      </main>
    </div>
  )
}

export default Dashboard
