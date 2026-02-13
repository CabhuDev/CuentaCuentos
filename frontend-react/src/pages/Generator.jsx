import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getCharacters, generateStory } from '../api/client'
import Spinner from '../components/Spinner'

export default function Generator() {
  const [characters, setCharacters] = useState([])
  const [selectedChars, setSelectedChars] = useState([])
  const [theme, setTheme] = useState('')
  const [moralLesson, setMoralLesson] = useState('')
  const [targetAge, setTargetAge] = useState('')
  const [length, setLength] = useState('medium')
  const [specialElements, setSpecialElements] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    console.log('[Generator] 🎭 Cargando personajes disponibles...');
    getCharacters()
      .then((chars) => {
        setCharacters(chars);
        console.log('[Generator] ✅ Personajes cargados:', chars.length);
      })
      .catch((err) => {
        console.error('[Generator] ❌ Error cargando personajes:', err);
        setCharacters([]);
      })
  }, [])

  const toggleCharacter = (nombre) => {
    setSelectedChars((prev) =>
      prev.includes(nombre)
        ? prev.filter((n) => n !== nombre)
        : [...prev, nombre]
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!theme.trim()) {
      setError('Por favor, escribe un tema para el cuento.')
      return
    }
    console.log('[Generator] 🚀 Iniciando generación de cuento...');
    console.log('[Generator] Tema:', theme);
    console.log('[Generator] Personajes seleccionados:', selectedChars);
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const story = await generateStory({
        theme,
        character_names: selectedChars.length > 0 ? selectedChars : null,
        moral_lesson: moralLesson || null,
        target_age: targetAge ? parseInt(targetAge) : 6,
        length,
        special_elements: specialElements || null,
      })
      console.log('[Generator] ✅ Cuento generado exitosamente');
      setResult(story)
    } catch (err) {
      console.error('[Generator] ❌ Error:', err);
      setError(err.message || 'Error al generar el cuento.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="theme">
            Tema o escena del cuento * (único campo obligatorio)
          </label>
          <input
            type="text"
            id="theme"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            placeholder="Ej: Una aventura en el bosque mágico"
            required
          />
        </div>

        <div className="form-group">
          <label>Personajes (opcional – selecciona uno o varios)</label>
          <div className="checkbox-group">
            {characters.length === 0 ? (
              <p className="text-muted">
                No hay personajes disponibles
              </p>
            ) : (
              characters.map((char) => (
                <div className="checkbox-item" key={char.id}>
                  <input
                    type="checkbox"
                    id={`char_${char.id}`}
                    checked={selectedChars.includes(char.nombre)}
                    onChange={() => toggleCharacter(char.nombre)}
                  />
                  <label htmlFor={`char_${char.id}`}>
                    {char.nombre} – {char.edad_aparente || 'Personaje'}
                  </label>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="moral_lesson">Lección moral (opcional)</label>
          <input
            type="text"
            id="moral_lesson"
            value={moralLesson}
            onChange={(e) => setMoralLesson(e.target.value)}
            placeholder="Ej: La importancia de la amistad"
          />
        </div>

        <div className="form-row">
          <div className="form-group form-group--flex">
            <label htmlFor="target_age">Edad objetivo</label>
            <input
              type="number"
              id="target_age"
              value={targetAge}
              onChange={(e) => setTargetAge(e.target.value)}
              min="3"
              max="12"
              placeholder="6"
            />
          </div>
          <div className="form-group form-group--flex">
            <label htmlFor="length">Longitud</label>
            <select
              id="length"
              value={length}
              onChange={(e) => setLength(e.target.value)}
            >
              <option value="short">Corto (2-3 párrafos)</option>
              <option value="medium">Medio (4-6 párrafos)</option>
              <option value="long">Largo (7+ párrafos)</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="special_elements">
            Elementos especiales (opcional)
          </label>
          <textarea
            id="special_elements"
            value={specialElements}
            onChange={(e) => setSpecialElements(e.target.value)}
            placeholder="Ej: Incluye animales que hablan, magia, aventuras..."
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Generando...' : 'Generar Cuento ✨'}
        </button>
      </form>

      {loading && <Spinner text="Creando tu cuento mágico..." />}

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="result-section">
          <div className="result-content">
            <h3 className="story-title">{result.title}</h3>
            <div className="story-text">{result.content}</div>
            <Link
              to={`/cuentos/${result.id}`}
              className="btn-primary btn-primary--spaced"
            >
              Ver en la biblioteca →
            </Link>
          </div>
        </div>
      )}
    </>
  )
}
