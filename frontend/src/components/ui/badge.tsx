import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-[4px] border px-2 py-0.5 text-[10px] font-mono tracking-wider uppercase font-medium transition-colors focus:outline-none select-none",
  {
    variants: {
      variant: {
        default:
          "border-[#2B3952] bg-[#161D2B] text-[#CBD5E1]",
        secondary:
          "border-[#26334A] bg-[#141A26] text-[#94A3B8]",
        destructive:
          "border-[#5A1C24] bg-[#260E12] text-[#F87171] before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:bg-[#EF4444] before:shadow-[0_0_6px_#EF4444]",
        outline:
          "border-[#26334A] bg-transparent text-[#94A3B8]",
        success:
          "border-[#14533D] bg-[#092319] text-[#34D399] before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:bg-[#10B981] before:shadow-[0_0_6px_#10B981]",
        warning:
          "border-[#533B18] bg-[#251B0B] text-[#FBBF24] before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:bg-[#F59E0B] before:shadow-[0_0_6px_#F59E0B]",
        info:
          "border-[#144872] bg-[#0A2238] text-[#38BDF8] before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:bg-[#0EA5E9] before:shadow-[0_0_6px_#0EA5E9]",
        champagne:
          "border-[#3D3524] bg-[#1C170E] text-[#FCD34D] before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:bg-[#FBBF24]",
        purple:
          "border-[#144872] bg-[#0A2238] text-[#38BDF8] before:content-[''] before:inline-block before:w-1.5 before:h-1.5 before:rounded-full before:bg-[#0EA5E9]",
        brand:
          "border-[#2563EB]/40 bg-[#14233D] text-[#93C5FD]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
