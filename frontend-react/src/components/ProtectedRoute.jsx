import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="app-background">
        <div className="container" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div className="spinner" />
          <p style={{ color: '#666', marginTop: 15 }}>Verificando sesión...</p>
        </div>
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />

  return <Outlet />
}
