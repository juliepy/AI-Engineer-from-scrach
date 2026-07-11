import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Schedulr — Meeting Scheduling for Sales Teams",
  description: "B2B meeting scheduling with CRM integration",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="text-gray-900 bg-gray-50">{children}</body>
    </html>
  );
}
