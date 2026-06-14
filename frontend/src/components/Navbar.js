"use client";

import Link from "next/link";
import { ThemeToggle } from "./ThemeToggle";
import { Briefcase, LayoutDashboard, Search } from "lucide-react";

export default function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 glass border-b border-border/40 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto max-w-7xl px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-2 font-bold text-xl text-primary">
          <Briefcase className="w-6 h-6" />
          <span>AI Career Coach</span>
        </Link>
        <div className="flex items-center space-x-6">
          <Link href="/dashboard" className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1 text-sm font-medium">
            <LayoutDashboard className="w-4 h-4" />
            <span>Dashboard</span>
          </Link>
          <Link href="/analyze" className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1 text-sm font-medium">
            <Search className="w-4 h-4" />
            <span>Analyze Resume</span>
          </Link>
          <ThemeToggle />
        </div>
      </div>
    </nav>
  );
}
