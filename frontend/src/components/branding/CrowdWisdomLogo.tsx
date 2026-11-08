import React from 'react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'

export type LogoVariant = 'sidebar' | 'header' | 'auth' | 'symbol' | 'badge' | 'full'
export type BadgeTheme = 'white' | 'dark' | 'auto'

export interface CrowdWisdomLogoProps {
  variant?: LogoVariant
  badgeTheme?: BadgeTheme
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  showBadge?: boolean
  showSubtitle?: boolean
  className?: string
  imageClassName?: string
  asLink?: boolean
  href?: string
}

export const CrowdWisdomLogo: React.FC<CrowdWisdomLogoProps> = ({
  variant = 'sidebar',
  badgeTheme = 'white',
  size = 'md',
  showBadge = true,
  showSubtitle = true,
  className,
  imageClassName,
  asLink = false,
  href = '/',
}) => {
  // Asset paths from public directory
  const badgeSrc = badgeTheme === 'dark' ? '/crowdwisdom_logo_dark.png' : '/crowdwisdom_logo_badge.png'
  const symbolSrc = '/crowdwisdom_logo_symbol.png'
  const fullSrc = '/crowdwisdom_logo_full.png'

  // Size mapping for symbol-only and badge-only variants
  const symbolSizeClasses = {
    xs: 'h-5 w-auto',
    sm: 'h-7 w-auto',
    md: 'h-9 w-auto',
    lg: 'h-12 w-auto',
    xl: 'h-16 w-auto',
  }

  // -------------------------------------------------------------
  // Variant: Symbol Only (Bears & Bulls Tug-of-War Artwork)
  // -------------------------------------------------------------
  if (variant === 'symbol') {
    const content = (
      <img
        src={symbolSrc}
        alt="CrowdWisdom Official Brand Symbol"
        className={cn(
          'object-contain select-none transition-transform duration-200 hover:scale-105',
          symbolSizeClasses[size],
          imageClassName
        )}
        loading="eager"
      />
    )
    return asLink ? <Link to={href} className={cn('inline-flex items-center', className)}>{content}</Link> : <div className={cn('inline-flex items-center', className)}>{content}</div>
  }

  // -------------------------------------------------------------
  // Variant: Badge Only (White or Dark Rounded Card)
  // -------------------------------------------------------------
  if (variant === 'badge') {
    const badgeHeights = {
      xs: 'h-6',
      sm: 'h-8',
      md: 'h-10',
      lg: 'h-14',
      xl: 'h-20',
    }
    const content = (
      <img
        src={badgeSrc}
        alt="CrowdWisdom Official Brand Badge"
        className={cn(
          'object-contain select-none drop-shadow-md rounded-lg',
          badgeHeights[size],
          imageClassName
        )}
        loading="eager"
      />
    )
    return asLink ? <Link to={href} className={cn('inline-flex items-center', className)}>{content}</Link> : <div className={cn('inline-flex items-center', className)}>{content}</div>
  }

  // -------------------------------------------------------------
  // Variant: Full Artwork (Bears & Bulls with Wordmark)
  // -------------------------------------------------------------
  if (variant === 'full') {
    const content = (
      <img
        src={fullSrc}
        alt="CrowdWisdom Official Brand Identity"
        className={cn('h-auto max-w-full object-contain select-none', imageClassName)}
        loading="eager"
      />
    )
    return asLink ? <Link to={href} className={cn('inline-flex items-center', className)}>{content}</Link> : <div className={cn('inline-flex items-center', className)}>{content}</div>
  }

  // -------------------------------------------------------------
  // Variant: Header (Compact for Top Navbar / Breadcrumbs)
  // -------------------------------------------------------------
  if (variant === 'header') {
    const content = (
      <div className={cn('inline-flex items-center gap-2', className)}>
        <div className="h-6 w-11 rounded-[5px] overflow-hidden bg-white/95 border border-[#38BDF8]/40 shadow-sm flex items-center justify-center p-0.5 flex-shrink-0">
          <img
            src={symbolSrc}
            alt="CrowdWisdom"
            className="h-full w-full object-contain"
            loading="eager"
          />
        </div>
        <span className="text-xs font-semibold tracking-tight text-[#F2F3F5] uppercase">
          CrowdWisdom
        </span>
        {showBadge && (
          <span className="text-[8px] font-mono font-semibold px-1 py-0.2 rounded bg-[#141820] border border-[#232B38] text-[#8E9EB5]">
            PRO
          </span>
        )}
      </div>
    )
    return asLink ? <Link to={href} className="inline-flex items-center">{content}</Link> : content
  }

  // -------------------------------------------------------------
  // Variant: Auth Screen (Prominent Brand Header on Login / Register)
  // -------------------------------------------------------------
  if (variant === 'auth') {
    return (
      <div className={cn('text-center space-y-3', className)}>
        <div className="inline-block relative group">
          {/* Subtle ambient cyan/blue backlight glow */}
          <div className="absolute -inset-1 bg-gradient-to-r from-[#547DB8]/30 via-[#38BDF8]/40 to-[#36B58F]/30 rounded-2xl blur-lg opacity-75 group-hover:opacity-100 transition duration-500" />
          
          {/* Institutional Badge Container */}
          <div className="relative rounded-xl bg-white p-2.5 px-4 border border-[#38BDF8]/50 shadow-2xl flex items-center justify-center">
            <img
              src={badgeSrc}
              alt="CrowdWisdom Official Bears & Bulls Logo"
              className="h-14 sm:h-16 w-auto object-contain select-none"
              loading="eager"
            />
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center justify-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-[#F2F3F5]">
              CrowdWisdom
            </h1>
            {showBadge && (
              <span className="text-[10px] font-mono uppercase tracking-widest px-1.5 py-0.5 rounded bg-[#C5A46D]/15 text-[#C5A46D] border border-[#C5A46D]/30 font-semibold">
                PRO STUDIO
              </span>
            )}
          </div>
          {showSubtitle && (
            <p className="text-xs text-[#A0A7B2] font-mono max-w-sm mx-auto">
              Autonomous AI Marketing & Cinematic Video Advertising Platform
            </p>
          )}
        </div>
      </div>
    )
  }

  // -------------------------------------------------------------
  // Variant: Sidebar (Primary Application Brand Presentation)
  // -------------------------------------------------------------
  const sidebarContent = (
    <div className={cn('flex items-center gap-3 select-none group', className)}>
      {/* Official Bears & Bulls Logo Badge */}
      <div className="relative flex-shrink-0">
        <div className="h-9 w-16 sm:h-10 sm:w-18 rounded-lg bg-white p-1 border border-[#38BDF8]/40 shadow-[0_2px_8px_rgba(0,0,0,0.35)] flex items-center justify-center overflow-hidden transition-all duration-200 group-hover:border-[#38BDF8] group-hover:shadow-[0_0_12px_rgba(56,189,248,0.3)]">
          <img
            src={symbolSrc}
            alt="CrowdWisdom Official Bears & Bulls Logo"
            className="h-full w-full object-contain"
            loading="eager"
          />
        </div>
      </div>

      {/* Brand Typography & Status Descriptor */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5">
          <h1 className="font-semibold text-xs tracking-tight text-[#F2F3F5] uppercase truncate">
            CrowdWisdom
          </h1>
          {showBadge && (
            <span className="text-[9px] font-mono font-semibold px-1.5 py-0.2 rounded-[3px] bg-[#141820] border border-[#232B38] text-[#8E9EB5] group-hover:text-[#547DB8] group-hover:border-[#547DB8]/40 transition-colors">
              PRO
            </span>
          )}
        </div>
        {showSubtitle && (
          <p className="text-[10px] text-[#727B89] font-mono tracking-wider truncate">
            AI MARKETING STUDIO
          </p>
        )}
      </div>
    </div>
  )

  return asLink ? (
    <Link to={href} className="block hover:opacity-95 transition-opacity">
      {sidebarContent}
    </Link>
  ) : (
    sidebarContent
  )
}

