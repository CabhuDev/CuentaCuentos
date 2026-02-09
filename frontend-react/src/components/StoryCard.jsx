import { useNavigate } from 'react-router-dom'

export default function StoryCard({ story }) {
  const navigate = useNavigate()

  const preview =
    story.content?.substring(0, 150) + (story.content?.length > 150 ? '...' : '')

  const date = new Date(story.created_at).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div className="story-card" onClick={() => navigate(`/cuentos/${story.id}`)}>
      <div className="story-card-title">{story.title}</div>
      <div className="story-card-meta">
        <span>📅 {date}</span>
        <span>v{story.version}</span>
      </div>
      <div className="story-card-preview">{preview}</div>
    </div>
  )
}
