import * as React from 'react'

import { cn } from '../../lib/utils'

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'rounded-[8px] border border-white/10 bg-white/[0.055] shadow-[0_24px_80px_rgba(0,0,0,0.32)] backdrop-blur-2xl',
        className,
      )}
      {...props}
    />
  ),
)

Card.displayName = 'Card'

export { Card }

