import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useTheme } from '@/hooks/useTheme'
import { useSnapshotCleanup } from '@/hooks/useSnapshotCleanup'
import { Layout } from '@/components/layout/Layout'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { CamerasPage } from '@/pages/CamerasPage'
import { DetectionsPage } from '@/pages/DetectionsPage'
import { ClipsPage } from '@/pages/ClipsPage'
import { MosaicosPage } from '@/pages/MosaicosPage'
import { SettingsPage } from '@/pages/SettingsPage'
import LiveDetectionsPage from '@/pages/LiveDetectionsPage'

// Protected Route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

// Public Route wrapper (redirects to home if already authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }
  
  return <>{children}</>
}

export default function App() {
  const { isAuthenticated } = useAuthStore()
  
  // Always call useTheme hook
  useTheme()
  
  // Cleanup old snapshots periodically
  useSnapshotCleanup()
  
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />

        {/* Protected routes */}
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/cameras" element={<CamerasPage />} />
          <Route path="/detections" element={<DetectionsPage />} />
          <Route path="/live" element={<LiveDetectionsPage />} />
          <Route path="/clips" element={<ClipsPage />} />
          <Route path="/mosaicos" element={<MosaicosPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
