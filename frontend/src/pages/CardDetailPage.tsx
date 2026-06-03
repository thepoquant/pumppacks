import { Link, useParams } from '@tanstack/react-router'
import { CARDS } from '../data/cards'

export function CardDetailPage() {
  const { id } = useParams({ from: '/card/$id' })
  const card = CARDS.find(c => c.id === id)

  if (!card) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center px-4">
        <div className="max-w-md text-center">
          <h1 className="text-7xl font-bold text-foreground">404</h1>
          <h2 className="mt-4 text-xl font-semibold">Card not found</h2>
          <div className="mt-6">
            <Link
              to="/"
              className="inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors"
              style={{ background: 'hsl(var(--primary))', color: 'hsl(var(--primary-foreground))' }}
            >
              Go home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <section className="py-16">
      <div className="container mx-auto px-6 max-w-5xl">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-10 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="m12 19-7-7 7-7" />
            <path d="M19 12H5" />
          </svg>
          Back to collection
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.2fr] gap-12 items-start animate-fade-in-up">
          {/* Card image */}
          <div
            className="rounded-xl p-6 flex items-center justify-center"
            style={{ border: '1px solid hsl(var(--border))', background: 'hsl(var(--card) / 0.4)' }}
          >
            <img
              src={card.image}
              alt={card.name}
              className="max-w-full object-contain"
              style={{
                maxHeight: '560px',
                filter: 'drop-shadow(0 20px 40px rgba(0,0,0,0.5))',
              }}
            />
          </div>

          {/* Card info */}
          <div className="flex flex-col gap-8">
            <div>
              <span className="font-mono text-[11px] uppercase tracking-[0.3em]" style={{ color: 'hsl(var(--primary))' }}>
                Card
              </span>
              <h1 className="mt-2 text-4xl md:text-5xl font-semibold tracking-tight">{card.name}</h1>
              <p className="mt-3 text-lg text-muted-foreground italic">{card.tagline}</p>
            </div>

            <div className="space-y-6">
              <div>
                <h2 className="font-mono text-[11px] uppercase tracking-[0.3em] mb-3" style={{ color: 'hsl(var(--primary))' }}>
                  Origin
                </h2>
                <div className="text-foreground/90 leading-relaxed">
                  <p>{card.origin}</p>
                </div>
              </div>
              <div>
                <h2 className="font-mono text-[11px] uppercase tracking-[0.3em] mb-3" style={{ color: 'hsl(var(--primary))' }}>
                  On-chain narrative
                </h2>
                <div className="text-foreground/90 leading-relaxed">
                  <p>{card.onchain}</p>
                </div>
              </div>
            </div>

            <div className="pt-4" style={{ borderTop: '1px solid hsl(var(--border))' }}>
              <p className="font-mono text-[11px] text-muted-foreground uppercase tracking-[0.25em]">
                Pull this card from a Pump Pack to earn supply of {card.ticker}.
              </p>
            </div>

            {/* Buy CTA */}
            <div className="space-y-3">
              <button
                className="w-full rounded-md py-3.5 text-sm font-semibold tracking-[0.2em] transition-all hover:opacity-90 hover:-translate-y-0.5 active:translate-y-0"
                style={{
                  background: 'hsl(var(--primary))',
                  color: 'hsl(var(--primary-foreground))',
                  boxShadow: '0 3px 0 hsl(145 50% 35%), 0 6px 14px hsl(var(--primary) / 0.3)',
                }}
              >
                BUY PACK · 0.5 SOL
              </button>
              <p className="text-xs text-muted-foreground text-center font-mono">
                Connect wallet to purchase · Demo available without wallet
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
