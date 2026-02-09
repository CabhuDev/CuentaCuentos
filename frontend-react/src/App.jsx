import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Generator from './pages/Generator'
import Library from './pages/Library'
import StoryDetail from './pages/StoryDetail'
import Learning from './pages/Learning'
import Profile from './pages/Profile'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Register />} />
      <Route path="/olvide-contrasena" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Generator />} />
          <Route path="/cuentos" element={<Library />} />
          <Route path="/cuentos/:id" element={<StoryDetail />} />
          <Route path="/aprendizaje" element={<Learning />} />
          <Route path="/perfil" element={<Profile />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
