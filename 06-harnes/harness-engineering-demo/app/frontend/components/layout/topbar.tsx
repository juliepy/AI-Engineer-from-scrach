"use client";

import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { getMe, type UserOut } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface TopbarProps {
  title: string;
  actions?: React.ReactNode;
}

export function Topbar({ title, actions }: TopbarProps) {
  const [user, setUser] = useState<UserOut | null>(null);

  useEffect(() => {
    getMe().then(setUser).catch(() => null);
  }, []);

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6">
      <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
      <div className="flex items-center gap-3">
        {actions}
        <Button variant="ghost" size="icon">
          <Bell className="h-4 w-4" />
        </Button>
        {user && (
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand text-white text-xs font-semibold">
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <span className="text-sm text-gray-700 hidden md:block">{user.full_name}</span>
          </div>
        )}
      </div>
    </header>
  );
}
