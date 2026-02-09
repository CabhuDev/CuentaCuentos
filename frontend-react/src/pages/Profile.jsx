import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { changePassword } from '../api/client'

export default function Profile() {
  const { user } = useAuth()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChangePassword = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (newPassword !== confirmPassword) {
      setError('Las nuevas contraseñas no coinciden')
      return
    }
    if (newPassword.length < 6) {
      setError('La nueva contraseña debe tener al menos 6 caracteres')
      return
    }
    if (currentPassword === newPassword) {
      setError('La nueva contraseña debe ser diferente a la actual')
      return
    }

    setLoading(true)
    try {
      await changePassword(currentPassword, newPassword)
      setSuccess('✅ Contraseña actualizada correctamente')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      setError(err.message || 'Error al cambiar la contraseña')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 style={{ textAlign: 'center', color: '#333', marginBottom: 30 }}>
        👤 Mi Perfil
      </h2>

      {/* Info del usuario */}
      <div className="profile-card">
        <div className="profile-avatar">
          {user?.username?.charAt(0).toUpperCase()}
        </div>
        <div className="profile-info">
          <h3>{user?.username}</h3>
          <p className="profile-email">
            {user?.email ? `📧 ${user.email}` : '📧 Sin email configurado'}
          </p>
          {!user?.email && (
            <p className="profile-hint">
              💡 Configura un email en tu cuenta para poder recuperar tu contraseña si la olvidas.
            </p>
          )}
        </div>
      </div>

      {/* Cambiar contraseña */}
      <div className="profile-section">
        <h3>🔑 Cambiar Contraseña</h3>

        {error && <div className="error">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <form onSubmit={handleChangePassword} className="profile-form">
          <div className="form-group">
            <label htmlFor="currentPassword">Contraseña actual</label>
            <input
              type="password"
              id="currentPassword"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="Introduce tu contraseña actual"
              required
            />
          </div>

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
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmNewPassword">Confirmar nueva contraseña</label>
            <input
              type="password"
              id="confirmNewPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repite la nueva contraseña"
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

          <button type="submit" disabled={loading} className="btn-change-password">
            {loading ? '⏳ Cambiando...' : '🔑 Cambiar Contraseña'}
          </button>
        </form>
      </div>
    </div>
  )
}
