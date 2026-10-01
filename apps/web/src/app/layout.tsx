import type { Metadata, Viewport } from 'next'
import { Inter, Montserrat } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const montserrat = Montserrat({
  subsets: ['latin'],
  variable: '--font-montserrat',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'VideoGen AI - Create Shorts & Reels with AI',
  description: 'Generate vertical short-form videos for YouTube Shorts, Instagram Reels, and TikTok using AI. Script → Voiceover → Visuals → Captions → Done.',
  keywords: ['AI video generator', 'shorts', 'reels', 'tiktok', 'text to video', 'faceless videos'],
  authors: [{ name: 'VideoGen AI' }],
  creator: 'VideoGen AI',
  publisher: 'VideoGen AI',
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://videogen.ai',
    siteName: 'VideoGen AI',
    title: 'VideoGen AI - Create Shorts & Reels with AI',
    description: 'Generate vertical short-form videos for YouTube Shorts, Instagram Reels, and TikTok using AI.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'VideoGen AI',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VideoGen AI - Create Shorts & Reels with AI',
    description: 'Generate vertical short-form videos for YouTube Shorts, Instagram Reels, and TikTok using AI.',
    images: ['/og-image.png'],
  },
  verification: {
    google: 'google-site-verification-code',
  },
}

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: '#0f172a' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${montserrat.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}