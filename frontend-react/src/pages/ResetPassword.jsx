import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { resetPassword } from '../api/client'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (newPassword !== confirmPassword) {
      setError('Las contraseñas no coinciden')
      return
    }
    if (newPassword.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres')
      return
    }

    setLoading(true)
    try {
      await resetPassword(token, newPassword)
      setSuccess(true)
    } catch (err) {
      setError(err.message || 'Error al restablecer la contraseña')
    } finally {
      setLoading(false)
    }
  }

  // Sin token en la URL
  if (!token) {
    return (
      <div className="app-background">
        <div className="auth-container">
          <h1>🌟 CuentaCuentos AI</h1>
          <div className="reset-error">
            <div className="reset-success-icon">⚠️</div>
            <h3>Enlace inválido</h3>
            <p>El enlace de recuperación no es válido o ha expirado.</p>
            <Link to="/olvide-contrasena" className="btn-back-login">
              Solicitar nuevo enlace
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app-background">
      <div className="auth-container">
        <h1>🌟 CuentaCuentos AI</h1>
        <p className="subtitle">Restablecer contraseña</p>

        {success ? (
          <div className="reset-success">
            <div className="reset-success-icon">✅</div>
            <h3>¡Contraseña actualizada!</h3>
            <p>Tu contraseña ha sido restablecida correctamente.</p>
            <p>Ya puedes iniciar sesión con tu nueva contraseña.</p>
            <Link to="/login" className="btn-back-login">
              Iniciar sesión
            </Link>
          </div>
        ) : (
          <>
            {error && <div className="error">{error}</div>}

            <p className="forgot-description">
              Introduce tu nueva contraseña.
            </p>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="newPassword">Nueva contraseña</label>
                <input
                  type="password"
                  id="newPassword"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Mínimo 6 caracteres"
                  required
                  minLength={6}
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirmar contraseña</label>
                <input
                  type="password"
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repite tu nueva contraseña"
                  required
                  minLength={6}
                />
              </div>

              {/* Indicador de fortaleza */}
              {newPassword && (
                <div className="password-strength">
                  <div className="strength-bar">
                    <div
                      className={`strength-fill ${
                        newPassword.length >= 12 ? 'strong' :
                        newPassword.length >= 8 ? 'medium' : 'weak'
                      }`}
                      style={{
                        width: `${Math.min(100, (newPassword.length / 12) * 100)}%`
                      }}
                    />
                  </div>
                  <span className="strength-text">
                    {newPassword.length >= 12 ? '🟢 Fuerte' :
                     newPassword.length >= 8 ? '🟡 Media' : '🔴 Débil'}
                  </span>
                </div>
              )}

              <button type="submit" disabled={loading}>
                {loading ? '⏳ Restableciendo...' : '🔐 Restablecer contraseña'}
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
