import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
  {
    variants: {
      variant: {
        default: "bg-blue-900/40 text-blue-300",
        success: "bg-green-900/40 text-green-300",
        warning: "bg-yellow-900/40 text-yellow-300",
        danger: "bg-red-900/40 text-red-300",
        orange: "bg-orange-900/40 text-orange-300",
        muted: "bg-slate-800 text-slate-400",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export function priorityVariant(nivel: string | null | undefined): BadgeProps["variant"] {
  const n = (nivel ?? "").toLowerCase();
  if (n.includes("crit")) return "danger";
  if (n.includes("alta")) return "orange";
  if (n.includes("media")) return "warning";
  return "default";
}
