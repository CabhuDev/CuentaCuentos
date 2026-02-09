import { useState } from 'react'
import { Link } from 'react-router-dom'
import { forgotPassword } from '../api/client'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setLoading(true)

    try {
      await forgotPassword(email)
      setSuccess(true)
    } catch (err) {
      setError(err.message || 'Error al procesar la solicitud')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-background">
      <div className="auth-container">
        <h1>🌟 CuentaCuentos AI</h1>
        <p className="subtitle">Recuperar contraseña</p>

        {success ? (
          <div className="reset-success">
            <div className="reset-success-icon">📧</div>
            <h3>¡Revisa tu email!</h3>
            <p>
              Si el email <strong>{email}</strong> está registrado en nuestra plataforma,
              recibirás un enlace para restablecer tu contraseña.
            </p>
            <p className="reset-hint">
              El enlace expirará en <strong>1 hora</strong>.
              Revisa también la carpeta de spam.
            </p>
            <Link to="/login" className="btn-back-login">
              ← Volver al inicio de sesión
            </Link>
          </div>
        ) : (
          <>
            {error && <div className="error">{error}</div>}

            <p className="forgot-description">
              Introduce el email asociado a tu cuenta y te enviaremos
              un enlace para restablecer tu contraseña.
            </p>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="tu@email.com"
                  required
                  autoFocus
                />
              </div>

              <button type="submit" disabled={loading}>
                {loading ? '⏳ Enviando...' : '📧 Enviar enlace de recuperación'}
              </button>
            </form>

            <p className="auth-switch">
              <Link to="/login">← Volver al inicio de sesión</Link>
            </p>
          </>
        )}
      </div>
    </div>
  )
}
