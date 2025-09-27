import type { AppProps } from 'next/app'
import { AuthProvider } from '@/contexts/AuthContext'
import HeaderAuth from '@/components/HeaderAuth'
import '../styles/globals.css'
import '../styles/responsive.css'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <div dir="rtl" className="font-farhang">
        <header className="p-4 border-b flex items-center justify-between">
          <div className="font-semibold">Zimmer</div>
          <HeaderAuth />
        </header>
        <main>
          <Component {...pageProps} />
        </main>
      </div>
    </AuthProvider>
  )
}
