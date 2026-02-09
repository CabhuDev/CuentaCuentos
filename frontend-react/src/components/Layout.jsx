import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="app-background">
      <div className="container">
        <header className="app-header">
          <nav className="header-nav">
            <div className="nav-links">
              <NavLink to="/" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`} end>
                ✨ Generar
              </NavLink>
              <NavLink to="/cuentos" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                📚 Cuentos
              </NavLink>
              <NavLink to="/aprendizaje" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                🧠 Aprendizaje
              </NavLink>
            </div>
            <div className="user-info">
              <NavLink to="/perfil" className="username" title="Mi Perfil">
                👤 {user?.username}
              </NavLink>
              <button onClick={logout} className="btn-logout">Salir</button>
            </div>
          </nav>
          <h1>🌟 CuentaCuentos AI</h1>
          <p className="subtitle">Genera cuentos personalizados con inteligencia artificial</p>
        </header>
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
