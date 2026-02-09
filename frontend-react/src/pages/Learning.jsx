import { useState, useEffect, useCallback } from 'react'
import { getLearningStats, getLessons, synthesizeLessons, getRAGStats, getLearningHistory, getStyleProfile } from '../api/client'
import Spinner from '../components/Spinner'
import Pagination from '../components/Pagination'

const CATEGORIES = [
  'pacing',
  'language_choice',
  'narrative_structure',
  'character_development',
  'emotional_depth',
  'sensory_details',
]

export default function Learning() {
  const [stats, setStats] = useState(null)
  const [lessons, setLessons] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [synthesizing, setSynthesizing] = useState(false)
  const [synthesisResult, setSynthesisResult] = useState(null)
  const [filterCategory, setFilterCategory] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [ragStats, setRagStats] = useState(null)
  const [showHistory, setShowHistory] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const [historyData, setHistoryData] = useState(null)
  const [profileData, setProfileData] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 8

  const loadData = useCallback(async () => {
    console.log('[Learning] 🧠 Cargando datos de aprendizaje...');
    console.log('[Learning] Filtros - Categoría:', filterCategory, '| Estado:', filterStatus);
    setCurrentPage(1) // Reset a página 1 cuando cambian filtros
    try {
      const [statsData, lessonsData, ragStatsData] = await Promise.all([
        getLearningStats().catch(() => null),
        getLessons(filterCategory, filterStatus).catch(() => []),
        getRAGStats().catch(() => null),
      ])
      setStats(statsData)
      const lessonsList = Array.isArray(lessonsData) ? lessonsData : lessonsData?.lessons || [];
      setLessons(lessonsList)
      setRagStats(ragStatsData)
      console.log('[Learning] ✅ Stats:', statsData);
      console.log('[Learning] ✅ Lecciones:', lessonsList.length);
      console.log('[Learning] ✅ RAG Stats:', ragStatsData);
    } catch (err) {
      console.error('[Learning] ❌ Error:', err);
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [filterCategory, filterStatus])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleSynthesize = async () => {
    console.log('[Learning] 🧠 Iniciando síntesis de lecciones...');
    setSynthesizing(true)
    setSynthesisResult(null)
    setError('')
    try {
      const result = await synthesizeLessons(5)
      console.log('[Learning] ✅ Síntesis completada:', result);
      setSynthesisResult(result)
      loadData()
    } catch (err) {
      console.error('[Learning] ❌ Error en síntesis:', err);
      setError(err.message)
    } finally {
      setSynthesizing(false)
    }
  }

  const toggleHistory = async () => {
    if (!showHistory && !historyData) {
      try {
        const data = await getLearningHistory()
        setHistoryData(data.history)
      } catch (err) {
        console.error('[Learning] Error cargando history:', err)
      }
    }
    setShowHistory(!showHistory)
  }

  const toggleProfile = async () => {
    if (!showProfile && !profileData) {
      try {
        const data = await getStyleProfile()
        setProfileData(data)
      } catch (err) {
        console.error('[Learning] Error cargando profile:', err)
      }
    }
    setShowProfile(!showProfile)
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
      .then(() => alert('✅ Copiado al portapapeles'))
      .catch(() => alert('❌ Error al copiar'))
  }

  const downloadJSON = (data, filename) => {
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handlePageChange = (page) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Calcular lecciones para la página actual
  const totalPages = Math.ceil(lessons.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentLessons = lessons.slice(startIndex, endIndex)

  if (loading) return <Spinner text="Cargando sistema de aprendizaje..." />

  return (
    <div>
      <h2 style={{ textAlign: 'center', color: '#333', marginBottom: 20 }}>
        🧠 Sistema de Aprendizaje
      </h2>

      {error && <div className="error">{error}</div>}

      {/* Estadísticas */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Score Promedio</div>
            <div className="stat-value">
              {stats.average_score?.toFixed(1) || '—'}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Lecciones</div>
            <div className="stat-value">{stats.total_lessons ?? 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Cuentos Generados</div>
            <div className="stat-value">{stats.total_stories ?? 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Críticas</div>
            <div className="stat-value">{stats.total_critiques ?? 0}</div>
          </div>
        </div>
      )}

      {/* Estadísticas RAG */}
      {ragStats && (
        <div style={{ margin: '30px 0' }}>
          <h2 style={{ textAlign: 'center', color: '#333', marginBottom: 20 }}>
            🔍 Estadísticas del Sistema RAG
          </h2>
          <div className="stats-grid">
            <div className="stat-card" style={{ background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' }}>
              <div className="stat-label">Cuentos Totales</div>
              <div className="stat-value">{ragStats.total_stories ?? 0}</div>
            </div>
            <div className="stat-card" style={{ background: 'linear-gradient(135deg, #3f51b5 0%, #5a55ae 100%)' }}>
              <div className="stat-label">Con Embeddings</div>
              <div className="stat-value">{ragStats.stories_with_embeddings ?? 0}</div>
            </div>
            <div className="stat-card" style={{ background: `linear-gradient(135deg, ${ragStats.coverage_percentage === 100 ? '#28a745' : '#ffc107'} 0%, ${ragStats.coverage_percentage === 100 ? '#20c997' : '#ff9800'} 100%)` }}>
              <div className="stat-label">Cobertura</div>
              <div className="stat-value">{ragStats.coverage_percentage?.toFixed(1) ?? 0}%</div>
            </div>
            <div className="stat-card" style={{ background: `linear-gradient(135deg, ${ragStats.ready_for_rag ? '#28a745' : '#dc3545'} 0%, ${ragStats.ready_for_rag ? '#20c997' : '#c82333'} 100%)` }}>
              <div className="stat-label">Estado RAG</div>
              <div className="stat-value" style={{ fontSize: '2em' }}>
                {ragStats.ready_for_rag ? '✅' : '❌'}
              </div>
              <div style={{ fontSize: '0.8em', marginTop: 5 }}>
                {ragStats.ready_for_rag ? 'Listo' : 'No listo'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Acciones */}
      <div className="action-buttons">
        <button
          className="btn-action btn-synthesize"
          onClick={handleSynthesize}
          disabled={synthesizing}
        >
          {synthesizing ? '⏳ Sintetizando...' : '🧠 Sintetizar Lecciones'}
        </button>
        <button className="btn-action btn-refresh" onClick={loadData}>
          🔄 Actualizar
        </button>
      </div>

      {synthesisResult && (
        <div className="success-message">
          ✅ Síntesis completada: {synthesisResult.lessons_extracted} lecciones
          extraídas de {synthesisResult.critiques_analyzed} críticas.
        </div>
      )}

      {/* Filtros */}
      <div className="filters-section">
        <div className="filter-controls">
          <div className="filter-group">
            <label>Categoría</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
            >
              <option value="">Todas</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label>Estado</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="">Todos</option>
              <option value="active">Activas</option>
              <option value="archived">Archivadas</option>
            </select>
          </div>
        </div>
      </div>

      {/* Lista de lecciones */}
      {lessons.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🧠</div>
          <p>No hay lecciones aprendidas aún.</p>
          <p>Genera cuentos y el sistema aprenderá automáticamente.</p>
        </div>
      ) : (
        <>
        <div className="lessons-list">
          {currentLessons.map((lesson, i) => (
            <div className="lesson-card" key={lesson.lesson_id || i}>
              <div className="lesson-header">
                <span className="lesson-title">
                  {lesson.insight || lesson.title || `Lección ${i + 1}`}
                </span>
                <span
                  className={`lesson-badge badge-${lesson.status || 'active'}`}
                >
                  {lesson.status || 'active'}
                </span>
              </div>
              <div className="lesson-meta">
                {lesson.category && (
                  <span className="lesson-category">
                    {lesson.category.replace(/_/g, ' ')}
                  </span>
                )}
                {lesson.priority && (
                  <span>Prioridad: {lesson.priority}</span>
                )}
                {lesson.applied_count !== undefined && (
                  <span>Aplicada: {lesson.applied_count}×</span>
                )}
              </div>
              {lesson.actionable_guidance && (
                <div className="lesson-description">
                  {lesson.actionable_guidance}
                </div>
              )}
              {lesson.supporting_evidence && (
                <div className="lesson-examples">
                  <h4>Evidencia</h4>
                  <p>{lesson.supporting_evidence}</p>
                </div>
              )}
            </div>
          ))}
        </div>
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          totalItems={lessons.length}
          itemsPerPage={itemsPerPage}
        />
        </>
      )}

      {/* Datos del Sistema */}
      <div style={{ marginTop: 50, paddingTop: 30, borderTop: '2px solid #e0e0e0' }}>
        <h2>📊 Datos del Sistema</h2>
        
        {/* Resumen de Evolución */}
        {stats && (
          <div style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
            color: 'white', 
            padding: 20, 
            borderRadius: 12, 
            marginBottom: 20 
          }}>
            <h3 style={{ margin: '0 0 15px 0' }}>🚀 Resumen de Evolución</h3>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: 15 
            }}>
              <div>
                <div style={{ fontSize: '0.9em', opacity: 0.9 }}>Última Síntesis</div>
                <div style={{ fontSize: '1.3em', fontWeight: 'bold' }}>
                  {stats.last_synthesis || 'Nunca'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.9em', opacity: 0.9 }}>Focos Actuales</div>
                <div style={{ fontSize: '1.1em', fontWeight: 'bold' }}>
                  {stats.current_focus_areas?.slice(0, 2).join(', ') || 'Ninguno'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.9em', opacity: 0.9 }}>Score Promedio</div>
                <div style={{ fontSize: '1.3em', fontWeight: 'bold' }}>
                  {stats.database_stats?.avg_score_last_10 ? `${stats.database_stats.avg_score_last_10}/10` : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Botones para mostrar/ocultar */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
          <button 
            className="btn-action" 
            style={{ background: '#17a2b8', color: 'white' }} 
            onClick={toggleHistory}
          >
            📜 {showHistory ? 'Ocultar' : 'Ver'} Learning History
          </button>
          <button 
            className="btn-action" 
            style={{ background: '#6f42c1', color: 'white' }} 
            onClick={toggleProfile}
          >
            🎨 {showProfile ? 'Ocultar' : 'Ver'} Style Profile
          </button>
        </div>

        {/* Learning History */}
        {showHistory && historyData && (
          <div style={{ marginBottom: 20 }}>
            <h3>📜 Learning History (learning_history.json)</h3>
            <div style={{ background: '#f8f9fa', padding: 20, borderRadius: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginBottom: 10 }}>
                <button 
                  onClick={() => copyToClipboard(JSON.stringify(historyData, null, 2))}
                  style={{ 
                    padding: '5px 15px', 
                    border: 'none', 
                    background: '#28a745', 
                    color: 'white', 
                    borderRadius: 5, 
                    cursor: 'pointer' 
                  }}
                >
                  📋 Copiar
                </button>
                <button 
                  onClick={() => downloadJSON(JSON.stringify(historyData, null, 2), 'learning_history.json')}
                  style={{ 
                    padding: '5px 15px', 
                    border: 'none', 
                    background: '#007bff', 
                    color: 'white', 
                    borderRadius: 5, 
                    cursor: 'pointer' 
                  }}
                >
                  💾 Descargar
                </button>
              </div>
              <pre style={{ 
                background: 'white', 
                padding: 15, 
                borderRadius: 5, 
                overflowX: 'auto', 
                maxHeight: 400, 
                border: '1px solid #ddd' 
              }}>
                {JSON.stringify(historyData, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Style Profile */}
        {showProfile && profileData && (
          <div style={{ marginBottom: 20 }}>
            <h3>🎨 Style Profile (style_profile.json)</h3>
            <div style={{ background: '#f8f9fa', padding: 20, borderRadius: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginBottom: 10 }}>
                <button 
                  onClick={() => copyToClipboard(JSON.stringify(profileData, null, 2))}
                  style={{ 
                    padding: '5px 15px', 
                    border: 'none', 
                    background: '#28a745', 
                    color: 'white', 
                    borderRadius: 5, 
                    cursor: 'pointer' 
                  }}
                >
                  📋 Copiar
                </button>
                <button 
                  onClick={() => downloadJSON(JSON.stringify(profileData, null, 2), 'style_profile.json')}
                  style={{ 
                    padding: '5px 15px', 
                    border: 'none', 
                    background: '#007bff', 
                    color: 'white', 
                    borderRadius: 5, 
                    cursor: 'pointer' 
                  }}
                >
                  💾 Descargar
                </button>
              </div>
              <pre style={{ 
                background: 'white', 
                padding: 15, 
                borderRadius: 5, 
                overflowX: 'auto', 
                maxHeight: 400, 
                border: '1px solid #ddd' 
              }}>
                {JSON.stringify(profileData, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
