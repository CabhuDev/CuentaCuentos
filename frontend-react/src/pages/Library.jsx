import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getStories } from '../api/client'
import StoryCard from '../components/StoryCard'
import Spinner from '../components/Spinner'
import Pagination from '../components/Pagination'

export default function Library() {
  const [stories, setStories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 12 // 12 cuentos por página

  useEffect(() => {
    console.log('[Library] 📚 Cargando biblioteca de cuentos...');
    getStories(50)
      .then((data) => {
        setStories(data);
        console.log('[Library] ✅ Biblioteca cargada:', data.length, 'cuentos');
      })
      .catch((err) => {
        console.error('[Library] ❌ Error:', err);
        setError(err.message);
      })
      .finally(() => setLoading(false))
  }, [])

  // Calcular paginación
  const totalPages = Math.ceil(stories.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedStories = stories.slice(startIndex, endIndex)

  const handlePageChange = (page) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (loading) return <Spinner text="Cargando cuentos..." />
  if (error) return <div className="error">{error}</div>

  if (stories.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📚</div>
        <p>No hay cuentos guardados aún.</p>
        <Link to="/" className="btn-primary">
          Crear mi primer cuento ✨
        </Link>
      </div>
    )
  }

  return (
    <>
      <h2 className="page-title">
        Biblioteca de Cuentos ({stories.length})
      </h2>
      <div className="stories-list">
        {paginatedStories.map((story) => (
          <StoryCard key={story.id} story={story} />
        ))}
      </div>
      
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
        totalItems={stories.length}
        itemsPerPage={itemsPerPage}
      />
    </>
  )
}
