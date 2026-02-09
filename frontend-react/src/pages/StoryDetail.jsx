import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  getStory,
  getStoryCritiques,
  generateAudio,
  checkAudioExists,
  deleteAudio,
  getFullAudioUrl,
} from '../api/client'
import Spinner from '../components/Spinner'

export default function StoryDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const audioRef = useRef(null)

  const [story, setStory] = useState(null)
  const [critiques, setCritiques] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Audio
  const [audioUrl, setAudioUrl] = useState(null)
  const [audioLoading, setAudioLoading] = useState(false)
  const [audioStatus, setAudioStatus] = useState('')

  // Illustration template
  const [showTemplate, setShowTemplate] = useState(false)

  useEffect(() => {
    console.log('[StoryDetail] 📝 Cargando cuento ID:', id);
    async function load() {
      try {
        const [storyData, audioState] = await Promise.all([
          getStory(id),
          checkAudioExists(id),
        ])
        console.log('[StoryDetail] ✅ Cuento cargado:', storyData.title);
        console.log('[StoryDetail] Estado de audio:', audioState.existe ? 'existe' : 'no existe');
        setStory(storyData)
        if (audioState.existe) {
          setAudioUrl(getFullAudioUrl(audioState.audio_url))
        }
        // Cargar críticas en segundo plano
        getStoryCritiques(id)
          .then((crit) => {
            setCritiques(crit);
            console.log('[StoryDetail] ✅ Críticas cargadas:', crit.critique_count);
          })
          .catch(() => {})
      } catch (err) {
        console.error('[StoryDetail] ❌ Error:', err);
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  const handleGenerateAudio = async () => {
    if (!story) return
    console.log('[StoryDetail] 🎵 Iniciando generación de audio...');
    setAudioLoading(true)
    setAudioStatus('Generando narración con ElevenLabs...')
    try {
      const data = await generateAudio(story.id, story.content)
      setAudioUrl(getFullAudioUrl(data.audio_url))
      const statusMsg = `✅ Audio generado (${data.characters_used} chars, ~${data.duration}s)`;
      console.log('[StoryDetail]', statusMsg);
      setAudioStatus(statusMsg)
      setTimeout(() => setAudioStatus(''), 5000)
    } catch (err) {
      console.error('[StoryDetail] ❌ Error generando audio:', err);
      setAudioStatus(`❌ Error: ${err.message}`)
    } finally {
      setAudioLoading(false)
    }
  }

  const handleDeleteAudio = async () => {
    if (!window.confirm('¿Estás seguro de eliminar el audio?')) return
    try {
      await deleteAudio(id)
      setAudioUrl(null)
      setAudioStatus('Audio eliminado')
      setTimeout(() => setAudioStatus(''), 3000)
    } catch (err) {
      setAudioStatus(`❌ Error: ${err.message}`)
    }
  }

  const copyTemplate = () => {
    if (!story?.illustration_template) return
    navigator.clipboard
      .writeText(JSON.stringify(story.illustration_template, null, 2))
      .then(() => {
        // feedback visual breve
        setShowTemplate(true)
      })
  }

  if (loading) return <Spinner text="Cargando cuento..." />
  if (error) return <div className="error">{error}</div>
  if (!story) return null

  const date = new Date(story.created_at).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  const hasTemplate =
    story.illustration_template &&
    Object.keys(story.illustration_template).length > 0

  return (
    <div className="story-detail">
      <button className="back-button" onClick={() => navigate('/cuentos')}>
        ← Volver a la lista
      </button>

      <div className="result-content">
        <h3 className="story-title">{story.title}</h3>
        <div className="story-meta">
          <span>📅 {date}</span>
          <span>Versión {story.version}</span>
        </div>

        {/* Controles de Audio */}
        <div className="audio-controls-container">
          {!audioUrl ? (
            <button
              className="btn-audio-generate"
              onClick={handleGenerateAudio}
              disabled={audioLoading}
            >
              {audioLoading
                ? '⏳ Generando audio...'
                : '🎵 Generar Narración en Audio'}
            </button>
          ) : (
            <div className="audio-player">
              <audio ref={audioRef} controls src={audioUrl} />
              <button className="btn-delete-audio" onClick={handleDeleteAudio}>
                🗑️ Eliminar Audio
              </button>
            </div>
          )}
          {audioStatus && (
            <div
              className={`audio-status ${
                audioStatus.startsWith('✅')
                  ? 'success'
                  : audioStatus.startsWith('❌')
                  ? 'error'
                  : 'info'
              }`}
            >
              {audioStatus}
            </div>
          )}
        </div>

        <div className="story-text">{story.content}</div>

        {/* Plantilla de Ilustraciones */}
        {hasTemplate && (
          <>
            <button
              className="btn-illustration-template"
              onClick={() => setShowTemplate(!showTemplate)}
            >
              🎨{' '}
              {showTemplate
                ? 'Ocultar Plantilla'
                : 'Ver Plantilla de Ilustraciones'}
            </button>
            {showTemplate && (
              <div className="illustration-template-container">
                <h4>📐 Plantilla de Ilustraciones (JSON)</h4>
                <p className="template-description">
                  Esta plantilla contiene prompts listos para generar
                  ilustraciones con IA (Midjourney, DALL-E, etc.)
                </p>
                <pre className="json-display">
                  {JSON.stringify(story.illustration_template, null, 2)}
                </pre>
                <div className="template-actions">
                  <button className="btn-secondary" onClick={copyTemplate}>
                    📋 Copiar JSON
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Críticas */}
      {critiques && critiques.critique_count > 0 && (
        <div className="critique-content">
          <h4 className="critique-title">
            📝 Críticas automáticas ({critiques.critique_count})
          </h4>
          {critiques.critiques.map((c) => (
            <div key={c.id} className="critique-item">
              <div className="critique-score">Score: {c.score}/10</div>
              <div className="critique-text">{c.critique_text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
