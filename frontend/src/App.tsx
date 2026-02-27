import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useTheme } from '@/hooks/useTheme'
import { useSnapshotCleanup } from '@/hooks/useSnapshotCleanup'
import { useInactivityTimeout } from '@/hooks/useInactivityTimeout'
import { Layout } from '@/components/layout/Layout'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { CamerasPage } from '@/pages/CamerasPage'
import { ClipsPage } from '@/pages/ClipsPage'
import { SettingsPage } from '@/pages/SettingsPage'
import TacticalViewPage from '@/pages/TacticalViewPage'
import IAMPage from '@/pages/IAMPage'

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
  
  useTheme()
  useSnapshotCleanup()
  useInactivityTimeout(3)
  
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
          <Route path="/cameras/tactical" element={<TacticalViewPage />} />
          <Route path="/clips" element={<ClipsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/settings/iam" element={<IAMPage />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
