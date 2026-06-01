import {
  createRouter,
  createRoute,
  createRootRoute,
  RouterProvider,
  Outlet,
} from '@tanstack/react-router'
import { Header } from './components/Header'
import { Footer } from './components/Footer'
import { HomePage } from './pages/HomePage'
import { OpCardsPage } from './pages/OpCardsPage'
import { HowItWorksPage } from './pages/HowItWorksPage'
import { PaymentPage } from './pages/PaymentPage'
import { CardDetailPage } from './pages/CardDetailPage'

// Root layout
const rootRoute = createRootRoute({
  component: () => (
    <div className="min-h-screen flex flex-col" style={{ background: 'hsl(var(--background))' }}>
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  ),
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
})

const opCardsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/op-cards',
  component: OpCardsPage,
})

const howItWorksRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/how-it-works',
  component: HowItWorksPage,
})

const paymentRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/payment',
  component: PaymentPage,
})

const cardDetailRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/card/$id',
  component: CardDetailPage,
})

const routeTree = rootRoute.addChildren([
  indexRoute,
  opCardsRoute,
  howItWorksRoute,
  paymentRoute,
  cardDetailRoute,
])

const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

export default function App() {
  return <RouterProvider router={router} />
}
