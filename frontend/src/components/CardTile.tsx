import { Link } from '@tanstack/react-router'
import { Card } from '../data/cards'

interface CardTileProps {
  card: Card
  loading?: 'eager' | 'lazy'
}

export function CardTile({ card, loading = 'lazy' }: CardTileProps) {
  return (
    <Link
      to="/card/$id"
      params={{ id: card.id }}
      aria-label={card.name}
      className="group flex flex-col items-center gap-2 transition-all duration-300 hover:-translate-y-1"
    >
      <div className="relative aspect-[3/4] flex items-center justify-center w-full rounded-xl overflow-hidden">
        <img
          src={card.image}
          alt={card.name}
          loading={loading}
          className="max-w-full max-h-full object-contain transition-transform duration-300 group-hover:scale-[1.03]"
          style={{ filter: 'drop-shadow(0 8px 24px rgba(0,0,0,0.5))' }}
        />
      </div>
      <span className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors text-center">
        {card.name}
      </span>
    </Link>
  )
}
