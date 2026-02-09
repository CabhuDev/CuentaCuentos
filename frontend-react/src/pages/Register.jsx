import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden')
      return
    }
    if (password.length < 4) {
      setError('La contraseña debe tener al menos 4 caracteres')
      return
    }

    setLoading(true)
    try {
      await register(username, password, email || undefined)
      navigate('/')
    } catch (err) {
      setError(err.message || 'Error al registrar usuario')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-background">
      <div className="auth-container">
        <h1>🌟 CuentaCuentos AI</h1>
        <p className="subtitle">Crea tu cuenta</p>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Usuario</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Elige un nombre de usuario"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email <span style={{ color: '#999', fontWeight: 'normal' }}>(opcional, para recuperar contraseña)</span></label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@email.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Elige una contraseña"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmar contraseña</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repite tu contraseña"
              required
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Registrando...' : 'Crear Cuenta'}
          </button>
        </form>

        <p className="auth-switch">
          ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
        </p>
      </div>
    </div>
  )
}
