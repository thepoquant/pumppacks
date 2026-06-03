export function Footer() {
  return (
    <footer className="border-t py-8 mt-12" style={{ borderColor: 'hsl(var(--border) / 0.4)' }}>
      <div className="container mx-auto px-6 text-xs font-mono text-muted-foreground flex flex-wrap items-center justify-between gap-4">
        <span>© PumpPacks</span>
        <span>On-chain verified • Instant SOL payouts</span>
      </div>
    </footer>
  )
}
