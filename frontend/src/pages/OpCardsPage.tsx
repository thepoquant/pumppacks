import { CARDS } from '../data/cards'
import { CardTile } from '../components/CardTile'

export function OpCardsPage() {
  return (
    <section className="py-12">
      <div className="container mx-auto px-6">
        <div className="text-xs font-mono uppercase tracking-wider mb-3" style={{ color: 'hsl(var(--primary))' }}>
          Catalog
        </div>
        <h1 className="text-4xl font-bold mb-8">Pump Cards</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {CARDS.map((card, i) => (
            <div key={card.id} className="animate-fade-in-up" style={{ animationDelay: `${i * 50}ms` }}>
              <CardTile card={card} />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
