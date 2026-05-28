import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '../../lib/utils'

const buttonVariants = cva(
  'inline-flex h-10 items-center justify-center gap-2 rounded-[8px] border text-sm font-medium outline-none transition duration-300 focus-visible:ring-2 focus-visible:ring-emerald-400/70 disabled:pointer-events-none disabled:opacity-45',
  {
    variants: {
      variant: {
        primary:
          'border-emerald-300/30 bg-emerald-400 text-[#04120a] shadow-[0_0_32px_rgba(34,197,94,0.24)] hover:bg-emerald-300',
        glass:
          'border-white/10 bg-white/[0.06] text-zinc-100 shadow-[0_18px_60px_rgba(0,0,0,0.28)] hover:border-emerald-300/30 hover:bg-white/[0.1]',
        ghost:
          'border-transparent bg-transparent text-zinc-300 hover:bg-white/[0.08] hover:text-white',
      },
      size: {
        sm: 'h-9 px-3',
        md: 'h-10 px-4',
        lg: 'h-12 px-5 text-base',
        icon: 'h-10 w-10 p-0',
      },
    },
    defaultVariants: {
      variant: 'glass',
      size: 'md',
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
  },
)

Button.displayName = 'Button'

export { Button }
