import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { login as apiLogin, register as apiRegister, getMe } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Verificar token al montar
  const checkAuth = useCallback(async () => {
    console.log('[AuthContext] 🔐 Verificando sesión...');
    const token = localStorage.getItem('cuentacuentos_token')
    if (!token) {
      console.log('[AuthContext] No hay token guardado');
      setLoading(false)
      return
    }
    try {
      const me = await getMe()
      console.log('[AuthContext] ✅ Sesión válida para:', me.username);
      setUser(me)
    } catch {
      console.warn('[AuthContext] ❌ Token inválido, limpiando sesión');
      localStorage.removeItem('cuentacuentos_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const login = async (username, password) => {
    console.log('[AuthContext] 🔐 Intentando login...');
    const data = await apiLogin(username, password)
    localStorage.setItem('cuentacuentos_token', data.access_token)
    const me = await getMe()
    setUser(me)
    console.log('[AuthContext] ✅ Login exitoso:', me.username);
    return me
  }

  const registerUser = async (username, password, email) => {
    console.log('[AuthContext] 📝 Registrando nuevo usuario...');
    await apiRegister(username, password, email)
    // Auto-login después del registro
    console.log('[AuthContext] ✅ Registro exitoso, iniciando auto-login...');
    return login(username, password)
  }

  const logout = () => {
    console.log('[AuthContext] 🚪 Cerrando sesión...');
    localStorage.removeItem('cuentacuentos_token')
    setUser(null)
    console.log('[AuthContext] ✅ Sesión cerrada');
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register: registerUser, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return ctx
}
