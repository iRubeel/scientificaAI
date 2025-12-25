'use client';

import Link from 'next/link';
import { ThemeToggle } from './theme-toggle';
import { Sparkles } from 'lucide-react';
import { Button } from './ui/button';

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 max-w-7xl items-center justify-between px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2 group">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-brand-600 to-purple-600 group-hover:scale-110 transition-transform">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-brand-600 to-purple-600">
            Revly
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-8">
          <Link
            href="/documentation"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Documentation
          </Link>
          <Link
            href="/methodology"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Methodology
          </Link>
          <Link
            href="/about"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            About
          </Link>
        </nav>

        {/* Right side actions */}
        <div className="flex items-center space-x-4">
          <ThemeToggle />
          <Button asChild size="sm" variant="default">
            <Link href="/upload">Upload Paper</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
