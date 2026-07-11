"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/api";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

interface AppShellProps {
  title: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

export function AppShell({ title, actions, children }: AppShellProps) {
  const router = useRouter();

  useEffect(() => {
    if (!getToken()) {
      router.push("/");
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="ml-[220px] flex flex-col min-h-screen">
        <Topbar title={title} actions={actions} />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
