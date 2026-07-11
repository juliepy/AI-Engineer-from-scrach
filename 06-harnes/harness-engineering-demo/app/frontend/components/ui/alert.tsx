import * as React from "react";
import { cn } from "@/lib/utils";

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "error" | "success" | "warning" | "info";
}

function Alert({ className, variant = "error", ...props }: AlertProps) {
  const variantClass = {
    error: "bg-red-50 border-red-200 text-red-700",
    success: "bg-green-50 border-green-200 text-green-700",
    warning: "bg-amber-50 border-amber-200 text-amber-700",
    info: "bg-blue-50 border-blue-200 text-blue-700",
  }[variant];

  return (
    <div
      className={cn("rounded-lg border px-4 py-3 text-sm", variantClass, className)}
      {...props}
    />
  );
}

export { Alert };
