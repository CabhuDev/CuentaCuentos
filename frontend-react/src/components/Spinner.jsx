export default function Spinner({ text }) {
  return (
    <div className="loading-indicator">
      <div className="spinner" />
      {text && <p>{text}</p>}
    </div>
  )
}
