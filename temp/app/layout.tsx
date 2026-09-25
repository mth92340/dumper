import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = { title: "ZS Dumper — Control Center", description: "Modern server resource recovery control center." }

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="fr"><body>{children}</body></html> }
