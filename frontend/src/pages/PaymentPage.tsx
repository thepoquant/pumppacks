const PAYMENT_ITEMS = [
  {
    title: 'Buyer pays',
    desc: 'SOL pulled at checkout via wallet signature, sent straight to the pack wallet.',
  },
  {
    title: 'Payout',
    desc: 'You get the SOL value you won — delivered as supply of the coin on the card you pulled, airdropped to your wallet 10 seconds after the spin ends.',
  },
  {
    title: 'Same wallet flywheel',
    desc: 'The pack wallet buys into the same coins you won, so your payout supply comes from real on-chain demand.',
  },
  {
    title: 'Refunds',
    desc: 'Returns initiate an on-chain reverse transfer.',
  },
]

export function PaymentPage() {
  return (
    <section className="py-16">
      <div className="container mx-auto px-6 max-w-3xl">
        <div className="text-xs font-mono uppercase tracking-wider mb-3" style={{ color: 'hsl(var(--primary))' }}>
          Settlement
        </div>
        <h1 className="text-4xl font-bold mb-4">Payment / Payout</h1>
        <p className="text-muted-foreground mb-10">
          All settlements happen on-chain in SOL. You receive the SOL amount you won — paid out as supply of the exact coin you pulled.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {PAYMENT_ITEMS.map((item, i) => (
            <div
              key={item.title}
              className="rounded-lg p-6 animate-fade-in-up"
              style={{
                border: '1px solid hsl(var(--border) / 0.5)',
                background: 'hsl(var(--card))',
                animationDelay: `${i * 80}ms`,
              }}
            >
              <h3 className="font-semibold">{item.title}</h3>
              <p className="text-sm text-muted-foreground mt-1">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
