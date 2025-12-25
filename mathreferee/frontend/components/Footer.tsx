'use client';

import Link from 'next/link';
import { Separator } from '@/components/ui/separator';

export default function Footer() {
  return (
    <footer className="border-t border-border bg-card mt-auto">
      <div className="container max-w-screen-2xl py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="font-semibold text-foreground mb-3">Revly</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Autonomous AI referee for mathematical and statistical research.
              Rigorous peer review with transparent epistemic tracking.
            </p>
          </div>

          {/* Resources */}
          <div>
            <h3 className="font-semibold text-foreground mb-3">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/documentation" className="text-muted-foreground hover:text-foreground transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link href="/methodology" className="text-muted-foreground hover:text-foreground transition-colors">
                  Methodology
                </Link>
              </li>
              <li>
                <Link href="https://github.com" target="_blank" rel="noreferrer" className="text-muted-foreground hover:text-foreground transition-colors">
                  GitHub
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold text-foreground mb-3">Contact</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="mailto:contact@revly.ai" className="text-muted-foreground hover:text-foreground transition-colors">
                  contact@revly.ai
                </Link>
              </li>
              <li>
                <Link href="/about" className="text-muted-foreground hover:text-foreground transition-colors">
                  About Us
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <Separator className="my-6" />

        <div className="text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} Revly. All rights reserved.
        </div>
      </div>
    </footer>
  );
}