import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import App from './App'
import './index.css'

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <div className="flex w-full flex-1 flex-col min-h-0">
          <App />
        </div>
      </QueryClientProvider>
  </React.StrictMode>,
)
