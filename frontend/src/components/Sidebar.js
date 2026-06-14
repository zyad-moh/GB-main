"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { ThemeToggle } from "./ThemeToggle";
import { 
  LayoutDashboard, 
  FileSearch, 
  Briefcase, 
  Target, 
  Zap, 
  BookOpen,
  Cpu
} from "lucide-react";
import { cn } from "@/lib/utils";

const routes = [
  { name: "Dashboard", path: "dashboard", icon: LayoutDashboard },
  { name: "CV Analyzer", path: "/cv-analyzer", icon: FileSearch },
  { name: "Job Matching", path: "/job-matching", icon: Briefcase },
  { name: "Skill Gap Detector", path: "/skill-gap", icon: Target },
  { name: "Resume Optimizer", path: "/resume-optimizer", icon: Zap },
  { name: "Learning & Projects", path: "/learning", icon: BookOpen },
  { name: "AI Interview", path: "/agent_board", icon: Cpu },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="w-64 hidden md:flex flex-col h-screen fixed top-0 left-0 glass-panel border-r border-[var(--border)] z-50">
        
        {/* Logo Area */}
        <div className="h-20 flex items-center px-6 border-b border-[var(--border)]">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center group-hover:bg-primary/20 transition-all shadow-[0_0_15px_rgba(0,240,255,0.3)]">
              <Cpu className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-foreground to-primary">
                CAREER<span className="text-primary font-normal">AI</span>
              </h1>
              <p className="text-[10px] text-primary uppercase tracking-widest leading-none mt-1 opacity-80">v.0.9 Engine</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-8 px-4 space-y-2">
          {routes.map((route) => {
            const isActive = pathname === route.path || pathname.startsWith(`${route.path}/`);
            
            return (
              <Link 
                key={route.path} 
                href={route.path}
                className={cn(
                  "relative flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-300 group",
                  isActive 
                    ? "bg-primary/10 text-primary border border-primary/30 shadow-[inset_0_0_20px_rgba(0,240,255,0.1)]" 
                    : "text-muted-foreground hover:bg-foreground/5 hover:text-foreground"
                )}
              >
                {isActive && (
                  <motion.div 
                    layoutId="active-nav-indicator"
                    className="absolute left-0 w-1 h-8 bg-primary rounded-r-full shadow-[0_0_10px_rgba(0,240,255,0.8)]"
                    initial={false}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                
                <route.icon className={cn(
                  "w-5 h-5 transition-colors", 
                  isActive ? "text-primary" : "group-hover:text-primary"
                )} />
                
                <span className="font-medium tracking-wide text-sm">{route.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Profile / System Toggle Footer */}
        <div className="p-4 border-t border-[var(--border)] flex justify-between items-center">
          <div className="flex flex-col">
            <span className="text-xs text-foreground font-semibold uppercase tracking-wider">Appearance</span>
            <span className="text-[10px] text-muted-foreground">Select system theme</span>
          </div>
          <ThemeToggle />
        </div>
      </aside>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full h-16 glass border-t border-[var(--border)] z-50 flex items-center justify-around px-2">
        {routes.map((route) => {
          const isActive = pathname === route.path || pathname.startsWith(`${route.path}/`);
          return (
            <Link 
              key={route.path} 
              href={route.path}
              className={cn(
                "flex flex-col items-center justify-center w-full h-full space-y-1 transition-colors",
                isActive ? "text-primary" : "text-muted-foreground hover:text-foreground"
              )}
            >
              <route.icon className="w-5 h-5" />
              <span className="text-[10px] font-medium hidden sm:block">{route.name}</span>
            </Link>
          );
        })}
        {/* Add ThemeToggle specifically for mobile at the end */}
        <div className="flex items-center justify-center p-2">
           <ThemeToggle />
        </div>
      </nav>
    </>
  );
}
