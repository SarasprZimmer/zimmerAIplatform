import type { AppProps } from 'next/app';
import '../styles/globals.css';
import '../styles/mobile.css';
import { AuthProvider } from '../contexts/AuthContext';
import { ToastProvider } from '../components/Toast';
import AppErrorBoundary from '../components/AppErrorBoundary';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AppErrorBoundary>
      <AuthProvider>
        <ToastProvider>
          <Component {...pageProps} />
        </ToastProvider>
              </AuthProvider>
    </AppErrorBoundary>
  );
} 