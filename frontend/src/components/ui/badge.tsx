import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold uppercase tracking-wider transition-colors focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border border-transparent bg-brand text-white",
        secondary:
          "border border-border bg-canvas text-slateSecondary",
        outline: "border border-border text-ink bg-surface",
        success:
          "border border-green-200 bg-emerald-50 text-emerald-700",
        warning:
          "border border-amber-200 bg-amber-50 text-amber-800",
        destructive:
          "border border-red-200 bg-red-50 text-red-700 font-bold",
        info:
          "border border-blue-200 bg-blue-50 text-blue-700",
        priceGuard:
          "border border-red-300 bg-red-100 text-red-900 font-bold tracking-normal",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
