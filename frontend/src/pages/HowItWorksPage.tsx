const STEPS = [
  {
    num: '01',
    title: 'Connect your wallet',
    desc: 'Link your Solana wallet — no signups, no KYC. Browse and demo for free.',
  },
  {
    num: '02',
    title: 'Buy a pack for 0.5 SOL',
    desc: 'One click, one signature. Payment settles on-chain instantly to the pack wallet.',
  },
  {
    num: '03',
    title: 'Open the pack',
    desc: 'Tear it open to reveal 3 random cards, each backed by real coin supply.',
  },
  {
    num: '04',
    title: 'Supply is sent automatically',
    desc: 'Exactly 10 seconds after your spin finishes, the coin supply for each card is airdropped straight to your wallet — no manual claim needed.',
  },
  {
    num: '05',
    title: 'Surplus flywheels the chart',
    desc: 'Every pack you open, we buy into the same coins you just won — straight from the pack wallet. Supply meets demand, every single pull.',
  },
]

export function HowItWorksPage() {
  return (
    <section className="py-16">
      <div className="container mx-auto px-6 max-w-4xl">
        <div className="text-xs font-mono uppercase tracking-wider mb-3" style={{ color: 'hsl(var(--primary))' }}>
          Protocol
        </div>
        <h1 className="text-4xl font-bold mb-4">How It Works</h1>
        <p className="text-muted-foreground mb-12">
          Buy a pack, pull 3 cards, win SOL. Every pack you open feeds the flywheel back into the chart.
        </p>
        <div className="space-y-4">
          {STEPS.map((step, i) => (
            <div
              key={step.num}
              className="rounded-lg p-6 flex gap-6 animate-fade-in-up"
              style={{
                border: '1px solid hsl(var(--border) / 0.5)',
                background: 'hsl(var(--card))',
                animationDelay: `${i * 80}ms`,
              }}
            >
              <div
                className="text-3xl font-bold font-mono shrink-0"
                style={{ color: 'hsl(var(--primary) / 0.7)' }}
              >
                {step.num}
              </div>
              <div>
                <h3 className="text-lg font-semibold">{step.title}</h3>
                <p className="text-sm text-muted-foreground mt-1">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
