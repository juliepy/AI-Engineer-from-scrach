"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  CalendarDays,
  Clock,
  Users2,
  Users,
  Settings,
  LogOut,
  CalendarPlus,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { clearToken } from "@/lib/api";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/meetings", label: "Meetings", icon: CalendarDays },
  { href: "/schedule", label: "Schedule", icon: CalendarPlus },
  { href: "/availability", label: "Availability", icon: Clock },
  { href: "/contacts", label: "Contacts", icon: Users2 },
  { href: "/team", label: "Team", icon: Users },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    clearToken();
    if (typeof window !== "undefined") {
      window.localStorage.removeItem("schedulr_session_token");
    }
    router.push("/");
  }

  return (
    <aside className="fixed left-0 top-0 z-30 flex h-full w-[220px] flex-col border-r border-gray-200 bg-white">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2.5 px-5 border-b border-gray-100">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand">
          <Zap className="h-4 w-4 text-white" />
        </div>
        <span className="text-base font-semibold text-gray-900">Schedulr</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active =
            href === "/meetings"
              ? pathname.startsWith("/meetings")
              : href === "/contacts"
              ? pathname.startsWith("/contacts")
              : pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-brand-50 text-brand"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="border-t border-gray-100 px-3 py-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
