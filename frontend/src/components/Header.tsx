import { useCallback } from 'react'
import { Link, useLocation } from '@tanstack/react-router'
import { useWallet } from '@solana/wallet-adapter-react'
import { useWalletModal } from '@solana/wallet-adapter-react-ui'

const NAV_LINKS = [
  { to: '/', label: 'Marketplace' },
  { to: '/op-cards', label: 'Pump Cards' },
  { to: '/how-it-works', label: 'How It Works' },
  { to: '/payment', label: 'Payment/Payout' },
]

function truncatePubkey(pk: string) {
  return `${pk.slice(0, 4)}...${pk.slice(-4)}`
}

export function Header() {
  const location = useLocation()
  const { publicKey, disconnect } = useWallet()
  const { setVisible } = useWalletModal()

  const handleConnect = useCallback(() => {
    if (publicKey) {
      disconnect()
    } else {
      setVisible(true)
    }
  }, [publicKey, disconnect, setVisible])

  return (
    <header className="border-b sticky top-0 z-50 backdrop-blur-sm" style={{ borderColor: 'hsl(var(--border) / 0.4)', background: 'hsl(var(--background) / 0.8)' }}>
      <div className="container mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <img
            src="https://pumppacks.app/__l5e/assets-v1/ed57e0c6-00a9-46e2-9f8b-c8b37d143749/pump-logo-transparent.png"
            alt="PumpPacks"
            className="h-10 w-10 object-contain"
          />
          <div className="leading-tight">
            <div className="font-bold tracking-wide text-foreground">PUMPPACKS</div>
          </div>
        </Link>

        {/* Nav */}
        <nav className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
          {NAV_LINKS.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`hover:text-foreground transition-colors ${location.pathname === link.to ? 'text-foreground' : ''}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <a
            href="https://x.com/pumppackspf"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="X"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor">
              <path d="M18.244 2H21l-6.49 7.41L22 22h-6.797l-4.78-6.262L4.8 22H2l6.94-7.93L2 2h6.91l4.32 5.71L18.244 2Zm-2.385 18h1.876L7.227 4H5.214l10.645 16Z" />
            </svg>
          </a>
          <button
            onClick={handleConnect}
            className="inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors"
            style={{ border: '1px solid hsl(var(--primary) / 0.5)', background: 'hsl(var(--primary) / 0.1)', color: 'hsl(var(--primary))' }}
            onMouseEnter={e => (e.currentTarget.style.background = 'hsl(var(--primary) / 0.2)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'hsl(var(--primary) / 0.1)')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1" />
              <path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4" />
            </svg>
            {publicKey ? truncatePubkey(publicKey.toBase58()) : 'Connect'}
          </button>
        </div>
      </div>
    </header>
  )
}
