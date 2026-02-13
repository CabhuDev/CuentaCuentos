import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="app-background">
      <header className="app-header">
        <div className="header-brand">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
          </svg>
          CuentaCuentos
        </div>
        <div className="user-info">
          <NavLink to="/perfil" className="username">
            {user?.username}
          </NavLink>
          <button onClick={logout} className="btn-logout">Salir</button>
        </div>
      </header>

      <main className="content-area">
        <Outlet />
      </main>

      <nav className="bottom-nav">
        <NavLink
          to="/"
          className={({ isActive }) => `bottom-nav-link${isActive ? ' active' : ''}`}
          end
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          Generar
        </NavLink>

        <NavLink
          to="/cuentos"
          className={({ isActive }) => `bottom-nav-link${isActive ? ' active' : ''}`}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
          </svg>
          Cuentos
        </NavLink>

        <NavLink
          to="/aprendizaje"
          className={({ isActive }) => `bottom-nav-link${isActive ? ' active' : ''}`}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
          Aprendizaje
        </NavLink>

        <NavLink
          to="/perfil"
          className={({ isActive }) => `bottom-nav-link${isActive ? ' active' : ''}`}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          Perfil
        </NavLink>
      </nav>
    </div>
  )
}
