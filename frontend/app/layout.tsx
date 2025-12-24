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

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'Todoly - Smart Task Management',
    template: '%s | Todoly'
  },
  description: 'Todoly is a powerful task management application that helps you organize, prioritize, and complete your tasks efficiently. Features include recurring tasks, subtasks, tags, calendar view, and more.',
  keywords: ['todo', 'task management', 'productivity', 'tasks', 'todoly', 'task organizer', 'kanban', 'calendar'],
  authors: [{ name: 'Todoly Team' }],
  creator: 'Todoly',
  publisher: 'Todoly',
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'Todoly - Smart Task Management',
    description: 'Organize, prioritize, and complete your tasks efficiently with Todoly',
    siteName: 'Todoly',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Todoly - Smart Task Management',
    description: 'Organize, prioritize, and complete your tasks efficiently with Todoly',
    creator: '@todoly',
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