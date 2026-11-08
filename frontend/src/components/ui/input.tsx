import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-8.5 w-full rounded-lg border border-[#292E37] bg-[#101216] px-3 py-1.5 text-xs text-[#F2F3F5] shadow-inner transition-colors file:border-0 file:bg-transparent file:text-xs file:font-medium placeholder:text-[#727B89] focus-visible:outline-none focus-visible:border-[#547DB8] focus-visible:ring-1 focus-visible:ring-[#547DB8] disabled:cursor-not-allowed disabled:opacity-40",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
