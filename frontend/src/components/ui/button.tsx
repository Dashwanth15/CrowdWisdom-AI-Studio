import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-xs font-medium transition-all duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#547DB8] disabled:pointer-events-none disabled:opacity-40 select-none cursor-pointer",
  {
    variants: {
      variant: {
        default:
          "bg-[#547DB8] text-white hover:bg-[#45699c] active:bg-[#395682] shadow-sm",
        brand:
          "bg-[#547DB8] text-white hover:bg-[#45699c] active:bg-[#395682] shadow-sm",
        destructive:
          "bg-[#D66C73]/15 text-[#D66C73] border border-[#D66C73]/30 hover:bg-[#D66C73]/25 active:bg-[#D66C73]/35",
        outline:
          "border border-[#292E37] bg-[#15191F] text-[#F2F3F5] hover:bg-[#232A34] hover:border-[#3B424F] active:bg-[#1B2028]",
        secondary:
          "bg-[#1B2028] text-[#F2F3F5] border border-[#292E37] hover:bg-[#232A34] hover:border-[#3B424F]",
        ghost:
          "text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#232A34]",
        link:
          "text-[#547DB8] underline-offset-4 hover:underline hover:text-[#7898C4]",
        champagne:
          "bg-[#C5A46D] text-[#080A0F] font-semibold hover:bg-[#D7BD8F] active:bg-[#B3935C] shadow-sm",
        emerald:
          "bg-[#36B58F] text-white font-medium hover:bg-[#2ea27f] shadow-sm",
      },
      size: {
        default: "h-8.5 px-3.5 py-1.5",
        sm: "h-7.5 rounded-md px-2.5 text-[11px]",
        lg: "h-10 rounded-lg px-6 text-sm",
        icon: "h-8 w-8 rounded-md",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
