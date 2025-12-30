import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Script from 'next/script';
import './globals.css';
import Providers from '@/components/providers';
import Navbar from '@/components/navbar';
import { Toaster } from '@/components/ui/toaster';
import { KeyboardShortcutsProvider } from '@/components/keyboard-shortcuts-provider';
import { MobileProvider } from '@/components/mobile/MobileProvider';
import { SessionProvider } from '@/components/session-provider';
import TodoMoreIcon from './icon';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'TodoMore - Smart Task Management',
    template: '%s | TodoMore'
  },
  description: 'TodoMore is a powerful task management application that helps you organize, prioritize, and complete your tasks efficiently. Features include recurring tasks, subtasks, tags, calendar view, and more.',
  keywords: ['todo', 'task management', 'productivity', 'tasks', 'todomore', 'task organizer', 'kanban', 'calendar'],
  authors: [{ name: 'TodoMore Team' }],
  creator: 'TodoMore',
  publisher: 'TodoMore',
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'),
  icons: {
    icon: [
      {
        url: '/favicon.svg',
        type: 'image/svg+xml',
      },
      {
        url: '/apple-icon.svg',
        sizes: '180x180',
        type: 'image/svg+xml',
      },
    ],
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'TodoMore - Smart Task Management',
    description: 'Organize, prioritize, and complete your tasks efficiently with TodoMore',
    siteName: 'TodoMore',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TodoMore - Smart Task Management',
    description: 'Organize, prioritize, and complete your tasks efficiently with TodoMore',
    creator: '@todomore',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {/* ChatKit web component - load once globally */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="beforeInteractive"
        />
        <Providers>
          <SessionProvider>
            <KeyboardShortcutsProvider>
              <div className="min-h-screen flex flex-col overflow-x-hidden">
                <Navbar />
                <div className="flex-1 overflow-x-hidden">
                  {children}
                </div>
              </div>
              <MobileProvider />
              <Toaster />
            </KeyboardShortcutsProvider>
          </SessionProvider>
        </Providers>
      </body>
    </html>
  );
}
