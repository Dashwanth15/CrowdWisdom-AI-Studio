import * as React from "react"
import { cn } from "@/lib/utils"

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> { }

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          "flex min-h-[75px] w-full rounded-lg border border-[#292E37] bg-[#101216] px-3 py-2 text-xs text-[#F2F3F5] shadow-inner transition-colors placeholder:text-[#727B89] focus-visible:outline-none focus-visible:border-[#547DB8] focus-visible:ring-1 focus-visible:ring-[#547DB8] disabled:cursor-not-allowed disabled:opacity-40",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = "Textarea"

export { Textarea }
