export default function Pagination({ currentPage, totalPages, onPageChange, totalItems, itemsPerPage }) {
  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  // Generar array de números de página a mostrar
  const getPageNumbers = () => {
    const pages = []
    const maxVisible = 7 // Máximo de números visibles

    if (totalPages <= maxVisible) {
      // Si hay pocas páginas, mostrar todas
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Lógica con elipsis para muchas páginas
      if (currentPage <= 4) {
        // Cerca del inicio: 1 2 3 4 5 ... 10
        for (let i = 1; i <= 5; i++) pages.push(i)
        pages.push('ellipsis')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 3) {
        // Cerca del final: 1 ... 6 7 8 9 10
        pages.push(1)
        pages.push('ellipsis')
        for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i)
      } else {
        // En medio: 1 ... 4 5 6 ... 10
        pages.push(1)
        pages.push('ellipsis')
        pages.push(currentPage - 1)
        pages.push(currentPage)
        pages.push(currentPage + 1)
        pages.push('ellipsis')
        pages.push(totalPages)
      }
    }

    return pages
  }

  const pageNumbers = getPageNumbers()

  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1)
    }
  }

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1)
    }
  }

  const handlePageClick = (page) => {
    if (page !== 'ellipsis') {
      onPageChange(page)
    }
  }

  // Si solo hay una página, no mostrar paginación
  if (totalPages <= 1) return null

  return (
    <div className="pagination-container">
      <div className="pagination-info">
        Mostrando <strong>{startItem}-{endItem}</strong> de <strong>{totalItems}</strong>
      </div>
      
      <div className="pagination">
        <button
          className="pagination-btn"
          onClick={handlePrevious}
          disabled={currentPage === 1}
          aria-label="Página anterior"
        >
          ← Anterior
        </button>

        {pageNumbers.map((page, index) => (
          page === 'ellipsis' ? (
            <span key={`ellipsis-${index}`} className="pagination-ellipsis">
              ...
            </span>
          ) : (
            <button
              key={page}
              className={`pagination-btn ${currentPage === page ? 'active' : ''}`}
              onClick={() => handlePageClick(page)}
              aria-label={`Ir a página ${page}`}
              aria-current={currentPage === page ? 'page' : undefined}
            >
              {page}
            </button>
          )
        ))}

        <button
          className="pagination-btn"
          onClick={handleNext}
          disabled={currentPage === totalPages}
          aria-label="Página siguiente"
        >
          Siguiente →
        </button>
      </div>
    </div>
  )
}
