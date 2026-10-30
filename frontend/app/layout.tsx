import type { Metadata } from 'next';
import Link from 'next/link';
import '@/app/global.css';

export const metadata: Metadata = {
  title: {
    template: '%s | Profiles',
    default: 'Profiles',
  },
  description: 'Consultant profiles: career, education, skills and projects.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="sticky top-0 z-10 border-b border-border bg-header-bg backdrop-blur-md">
          <div className="mx-auto flex h-[78px] max-w-5xl items-center justify-between px-[18px] sm:px-8">
            <Link href="/" className="font-head text-lg font-semibold tracking-tight text-ink">
              Profiles
            </Link>
            <nav className="font-head text-[0.92rem] font-medium text-ink-soft">
              <Link href="/" className="hover:text-ink">
                All profiles
              </Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-[18px] py-10 sm:px-8 sm:py-14">{children}</main>
      </body>
    </html>
  );
}
