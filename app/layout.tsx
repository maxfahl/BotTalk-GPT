import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BotTalk-GPT - Modern AI Persona Chat",
  description: "Create and simulate conversations between AI personas with modern UI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
