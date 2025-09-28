import type { AppProps } from 'next/app'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import '../styles/globals.css'
import '../styles/responsive.css'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <div dir="rtl" className="font-farhang">
          <Component {...pageProps} />
        </div>
      </AuthProvider>
    </ThemeProvider>
  )
}
