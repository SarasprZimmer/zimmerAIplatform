import type { AppProps } from 'next/app'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import HeaderAuth from '@/components/HeaderAuth'
import '../styles/globals.css'
import '../styles/responsive.css'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <div dir="rtl" className="font-farhang">
          <header className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex items-center justify-between">
            <div className="font-semibold text-gray-900 dark:text-white">Zimmer</div>
            <HeaderAuth />
          </header>
          <main className="bg-white dark:bg-gray-900">
            <Component {...pageProps} />
          </main>
        </div>
      </AuthProvider>
    </ThemeProvider>
  )
}
