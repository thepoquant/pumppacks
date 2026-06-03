import { useState, useRef, useCallback } from 'react'
import { useWallet, useConnection } from '@solana/wallet-adapter-react'
import { useWalletModal } from '@solana/wallet-adapter-react-ui'
import { Transaction, SystemProgram, LAMPORTS_PER_SOL, PublicKey } from '@solana/web3.js'
import { CARDS } from '../data/cards'
import { CardTile } from '../components/CardTile'

interface DrawnCard {
  id: string
  name: string
  ticker: string
  image_url: string
}

const PACK_IMAGE = 'https://pumppacks.app/__l5e/assets-v1/d0560df1-81ce-44ff-ae5f-342712a2c5e4/pump-pack.png'
const PACK_LAYERS = [
  { z: -7.5, y: 3, brightness: 0.45, blur: 0.75 },
  { z: -6, y: 2.4, brightness: 0.55, blur: 0.6 },
  { z: -4.5, y: 1.8, brightness: 0.65, blur: 0.45 },
  { z: -3, y: 1.2, brightness: 0.75, blur: 0.3 },
  { z: -1.5, y: 0.6, brightness: 0.85, blur: 0.15 },
]

const PACK_WALLET = import.meta.env.VITE_PACK_WALLET_ADDRESS || 'vEeSPZdVd4S8owp686hhfqwtwZr337zJGd5YqDEDUMM'
const TEST_RECIPIENT = new PublicKey(PACK_WALLET)
const BUY_PACK_AMOUNT = parseFloat(import.meta.env.VITE_SOL_PER_PACK || '0.5')

function PackDemo() {
  const { publicKey, sendTransaction } = useWallet()
  const { connection } = useConnection()
  const { setVisible } = useWalletModal()
  const [isOpening, setIsOpening] = useState(false)
  const [drawnCards, setDrawnCards] = useState<DrawnCard[]>([])
  const [showCards, setShowCards] = useState(false)
  const [error, setError] = useState('')
  const packRef = useRef<HTMLButtonElement>(null)

  const handleBuyPack = useCallback(async () => {
    setError('')
    if (!publicKey) {
      setVisible(true)
      return
    }
    setIsOpening(true)
    setShowCards(false)
    setDrawnCards([])

    try {
      const { blockhash } = await connection.getLatestBlockhash()

      const tx = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: publicKey,
          toPubkey: TEST_RECIPIENT,
          lamports: BUY_PACK_AMOUNT * LAMPORTS_PER_SOL,
        }),
      )
      tx.recentBlockhash = blockhash
      tx.feePayer = publicKey

      const signature = await sendTransaction(tx, connection)

      await connection.confirmTransaction(signature, 'confirmed')

      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/buy-pack`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          buyer_wallet: publicKey.toString(),
          tx_signature: signature,
        }),
      })

      if (!res.ok) throw new Error('Backend request failed')

      const data = await res.json()
      setDrawnCards(data.cards)
      setShowCards(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Transaction failed')
    } finally {
      setIsOpening(false)
    }
  }, [publicKey, sendTransaction, connection, setVisible])

  return (
    <div className="relative w-full max-w-md mx-auto">
      {/* Glow */}
      <div
        className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-3/4 h-16 rounded-full pointer-events-none"
        style={{ background: 'hsl(var(--primary) / 0.3)', filter: 'blur(24px)' }}
      />

      {/* Pack */}
      <div className="relative aspect-[3/4] flex items-center justify-center">
        <button
          ref={packRef}
          aria-label="Open pack (demo)"
          onClick={() => setIsOpening(o => !o)}
          className="group relative w-full h-full flex items-center justify-center focus:outline-none"
        >
          {/* BG glow */}
          <div
            className="absolute inset-0 rounded-3xl blur-2xl transition-opacity duration-500"
            style={{
              background: 'radial-gradient(circle at center, hsl(145 60% 55% / 0.55), transparent 65%)',
              opacity: isOpening ? 0.9 : 0.6,
            }}
          />
          {/* Stacked pack layers */}
          <div
            className={`relative max-h-full max-w-[85%] transition-all ${isOpening ? 'scale-110' : 'animate-[packSpin3D_8s_ease-in-out_infinite]'}`}
            style={{ transformStyle: 'preserve-3d' }}
          >
            {PACK_LAYERS.map((layer, i) => (
              <img
                key={i}
                src={PACK_IMAGE}
                alt=""
                aria-hidden="true"
                draggable={false}
                className="absolute inset-0 w-full h-full object-contain pointer-events-none"
                style={{
                  transform: `translateZ(${layer.z}px) translateY(${layer.y}px)`,
                  filter: `brightness(${layer.brightness}) blur(${layer.blur}px)`,
                  opacity: 0.85,
                }}
              />
            ))}
            <img
              src={PACK_IMAGE}
              alt="Pump Pack"
              draggable={false}
              className="relative w-full h-full object-contain"
              style={{
                transform: 'translateZ(2px)',
                filter: 'drop-shadow(0 20px 40px rgba(0,0,0,0.6))',
              }}
            />
          </div>
        </button>
      </div>

      {/* Card pull result */}
      {showCards && drawnCards.length > 0 && (
        <div className="mt-4 grid grid-cols-3 gap-3">
          {drawnCards.map((card, i) => (
            <div
              key={card.id}
              className="card-reveal flex flex-col items-center gap-1"
              style={{ animationDelay: `${i * 120}ms` }}
            >
              <img
                src={card.image_url}
                alt={card.name}
                className="w-full object-contain rounded-lg"
                style={{ filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.5))' }}
              />
              <span className="text-[10px] font-mono text-muted-foreground text-center leading-tight">{card.ticker}</span>
            </div>
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-3 text-xs font-mono text-center" style={{ color: 'hsl(var(--destructive))' }}>
          {error}
        </div>
      )}

      {/* Buy UI */}
      <div className="mt-6 space-y-3">
        <div className="flex items-center justify-between rounded-md px-4 py-3" style={{ background: 'hsl(var(--background) / 0.6)', border: '1px solid hsl(var(--border))' }}>
          <span className="font-mono text-xs tracking-[0.25em] text-muted-foreground uppercase">Price</span>
          <span className="font-mono font-semibold text-lg" style={{ color: 'hsl(var(--primary))' }}>{BUY_PACK_AMOUNT} SOL</span>
        </div>
        <button
          onClick={handleBuyPack}
          disabled={isOpening}
          className="w-full rounded-md py-3.5 text-sm font-semibold tracking-[0.2em] transition-all disabled:opacity-50 hover:opacity-90 hover:-translate-y-0.5 active:translate-y-0"
          style={{
            background: 'hsl(var(--primary))',
            color: 'hsl(var(--primary-foreground))',
            boxShadow: '0 3px 0 hsl(145 50% 35%), 0 6px 14px hsl(var(--primary) / 0.3)',
          }}
        >
          {isOpening ? 'BUYING...' : publicKey ? `BUY PACK · ${BUY_PACK_AMOUNT} SOL` : 'CONNECT WALLET'}
        </button>
        <button
          onClick={() => {
            if (isOpening) return
            setIsOpening(true)
            setShowCards(false)
            setDrawnCards([])
            setTimeout(() => {
              const shuffled = [...CARDS].sort(() => Math.random() - 0.5)
              const picked = shuffled.slice(0, 3).map(c => ({ id: c.id, name: c.name, ticker: c.ticker, image_url: c.image }))
              setDrawnCards(picked)
              setShowCards(true)
              setIsOpening(false)
            }, 800)
          }}
          disabled={isOpening}
          className="w-full rounded-md py-3 text-xs font-mono uppercase tracking-[0.25em] text-muted-foreground hover:text-foreground transition-all disabled:opacity-50"
          style={{ border: '1px solid hsl(var(--border))', background: 'hsl(var(--background) / 0.4)' }}
          onMouseEnter={e => (e.currentTarget.style.borderColor = 'hsl(var(--primary) / 0.4)')}
          onMouseLeave={e => (e.currentTarget.style.borderColor = 'hsl(var(--border))')}
        >
          {isOpening ? 'Opening...' : 'Try a free demo pull'}
        </button>
        <div className="flex items-center justify-between font-mono text-xs tracking-[0.2em] text-muted-foreground uppercase pt-1">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ background: 'hsl(var(--primary))' }} />
            On-chain
          </span>
          <span>Variable RTP</span>
          <span>3 Cards</span>
        </div>
      </div>
    </div>
  )
}

export function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="container mx-auto px-6 pt-20 pb-24">
        <div className="grid lg:grid-cols-2 gap-16 items-center max-w-6xl mx-auto">
          {/* Left */}
          <div className="text-center lg:text-left animate-fade-in-up">
            <span className="font-mono text-[11px] uppercase tracking-[0.3em]" style={{ color: 'hsl(var(--primary))' }}>
              PumpPacks
            </span>
            <h1 className="mt-4 text-5xl md:text-6xl font-semibold tracking-tight text-foreground leading-[1.05]">
              Open a pack.<br />
              <span style={{ color: 'hsl(var(--primary))' }}>Win supply.</span>
            </h1>
            <p className="mt-6 text-base text-muted-foreground leading-relaxed max-w-md mx-auto lg:mx-0">
              Pay <span className="text-foreground font-medium">{BUY_PACK_AMOUNT} SOL</span> per pack and pull{' '}
              <span className="text-foreground font-medium">3 random cards</span>. Each card grants real supply of the coin it represents.
            </p>
            <div className="mt-8 flex flex-wrap gap-6 justify-center lg:justify-start font-mono text-xs text-muted-foreground uppercase tracking-[0.2em]">
              <div>
                <div className="text-base font-semibold" style={{ color: 'hsl(var(--primary))' }}>{BUY_PACK_AMOUNT} SOL</div>
                <div className="mt-1">Per pack</div>
              </div>
              <div className="w-px bg-border" />
              <div>
                <div className="text-base font-semibold" style={{ color: 'hsl(var(--primary))' }}>3 Cards</div>
                <div className="mt-1">Per pull</div>
              </div>
              <div className="w-px bg-border" />
              <div>
                <div className="text-base font-semibold" style={{ color: 'hsl(var(--primary))' }}>Variable</div>
                <div className="mt-1">RTP</div>
              </div>
              <p className="mt-4 text-xs text-muted-foreground font-mono uppercase tracking-[0.15em] w-full">
                All surplus is flywheeled directly into the chart.
              </p>
            </div>
          </div>

          {/* Right — Pack */}
          <div className="flex justify-center animate-fade-in-up" style={{ animationDelay: '150ms' }}>
            <PackDemo />
          </div>
        </div>
      </section>

      {/* Cards grid */}
      <section className="container mx-auto px-6 pb-24">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-end justify-between mb-10 pb-6" style={{ borderBottom: '1px solid hsl(var(--border))' }}>
            <div>
              <span className="font-mono text-[11px] uppercase tracking-[0.3em]" style={{ color: 'hsl(var(--primary))' }}>
                Collection
              </span>
              <h2 className="mt-2 text-3xl font-semibold tracking-tight">Available cards</h2>
            </div>
            <span className="font-mono text-[11px] text-muted-foreground uppercase tracking-[0.2em]">
              {CARDS.length} cards
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {CARDS.map((card, i) => (
              <div key={card.id} className="animate-fade-in-up" style={{ animationDelay: `${i * 50}ms` }}>
                <CardTile card={card} loading={i < 4 ? 'eager' : 'lazy'} />
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
