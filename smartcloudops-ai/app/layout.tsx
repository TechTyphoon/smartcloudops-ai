import type React from "react"
import type { Metadata } from "next"
import { Inter, IBM_Plex_Sans } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider } from "@/hooks/use-auth"

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
})

const ibmPlex = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
  variable: "--font-ibm-plex",
})

export const metadata: Metadata = {
  title: "SmartCloudOps AI - Enterprise Cloud Operations Platform",
  description: "AI-Powered CloudOps Intelligence for Enterprise Infrastructure Management",
  generator: "SmartCloudOps AI",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <style>{`
html {
  font-family: ${inter.style.fontFamily};
  --font-inter: ${inter.variable};
  --font-ibm-plex: ${ibmPlex.variable};
}
        `}</style>
      </head>
      <body className={`${inter.variable} ${ibmPlex.variable} antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange={false}>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
