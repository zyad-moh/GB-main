"use client";

import { usePathname } from "next/navigation";
import Sidebar from "./Sidebar";

const FULL_WIDTH_ROUTES = ["/"];
const AUTH_ROUTES = ["/login", "/signup"];

export default function LayoutShell({ children }) {
  const pathname = usePathname();
  const isFullWidth = FULL_WIDTH_ROUTES.includes(pathname);
  const isAuthPage = AUTH_ROUTES.includes(pathname);

  // Home / Landing page — full viewport, no sidebar
  if (isFullWidth) {
    return (
      <div className="flex-1 w-full min-h-screen overflow-y-auto">
        {children}
      </div>
    );
  }

  // Auth pages (login/signup) — no sidebar, centered content
  if (isAuthPage) {
    return (
      <main className="flex-1 overflow-y-auto w-full">
        <div className="container mx-auto p-4 md:p-8">
          {children}
        </div>
      </main>
    );
  }

  // Dashboard / App pages — sidebar layout
  return (
    <>
      <Sidebar className="hidden md:flex w-64 flex-col bg-card" />
      <main className="flex-1 overflow-y-auto w-full md:pl-64 pb-20 md:pb-0">
        <div className="container mx-auto p-4 md:p-8">
          {children}
        </div>
      </main>
    </>
  );
}
