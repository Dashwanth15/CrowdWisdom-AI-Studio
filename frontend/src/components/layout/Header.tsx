import React, { useState, useEffect } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { CheckCircle2, ChevronRight, ExternalLink, Activity, Radio } from 'lucide-react'
import { wsManager } from '@/lib/websocket'
import { WSEvent } from '@/types'
import { CrowdWisdomLogo } from '@/components/branding'

const ROUTE_LABELS: Record<string, string> = {
  '': 'Executive Dashboard',
  'campaigns': 'Campaign Management',
  'agents': 'Agent Command Center',
  'research': 'Ads Intelligence',
  'insights': 'Marketing Intelligence',
  'scripts': 'Script Studio',
  'videos': 'Video Production',
  'workflow': 'Workflow & Pipeline',
  'assets': 'Creative Assets',
  'settings': 'Integrations & API',
  'logs': 'Execution Logs',
}

export const Header: React.FC = () => {
  const location = useLocation()
  const [isConnected, setIsConnected] = useState(false)
  const [lastNotification, setLastNotification] = useState<string | null>(null)

  useEffect(() => {
    setIsConnected(wsManager.isConnected)

    const unsubConnected = wsManager.on('connected', () => {
      setIsConnected(true)
    })

    const unsubNotification = wsManager.on('notification', (event: WSEvent) => {
      if ('message' in event) {
        setLastNotification(event.message as string)
        setTimeout(() => setLastNotification(null), 6000)
      }
    })

    return () => {
      unsubConnected()
      unsubNotification()
    }
  }, [])

  // Parse path segments for clean breadcrumb
  const segments = location.pathname.split('/').filter(Boolean)
  const primarySegment = segments[0] || ''
  const currentTitle = ROUTE_LABELS[primarySegment] || 'Command Center'

  return (
    <header className="h-13 border-b border-[#292E37] bg-[#0C0F14]/90 backdrop-blur-md px-6 flex items-center justify-between flex-shrink-0 z-20">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2.5 text-xs">
        <CrowdWisdomLogo variant="header" showBadge={false} asLink href="/" />
        <ChevronRight className="h-3 w-3 text-[#727B89]" />
        <span className="text-[#F2F3F5] font-medium tracking-tight">
          {currentTitle}
        </span>
        {segments.length > 1 && (
          <>
            <ChevronRight className="h-3 w-3 text-[#727B89]" />
            <span className="text-[#A0A7B2] font-mono text-[11px] bg-[#15191F] px-2 py-0.5 rounded border border-[#292E37]">
              {segments[1].slice(0, 8)}...
            </span>
          </>
        )}

        {/* Live Event Notification Banner */}
        {lastNotification && (
          <div className="ml-4 flex items-center gap-2 bg-[#1B2028] text-[#547DB8] border border-[#292E37] px-2.5 py-0.5 rounded-full text-[11px] animate-in fade-in">
            <CheckCircle2 className="h-3 w-3 text-[#36B58F]" />
            <span className="truncate max-w-sm text-[#A0A7B2]">{lastNotification}</span>
          </div>
        )}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Real-time Telemetry Bar */}
        <div className="flex items-center gap-2.5">
          {/* WebSocket Status */}
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-[4px] bg-[#10141C] border border-[#232936] text-[10px] font-mono">
            <span className="relative flex h-1.5 w-1.5">
              {isConnected ? (
                <>
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#36B58F] opacity-75" />
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[#36B58F] shadow-[0_0_6px_#36B58F]" />
                </>
              ) : (
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[#D9A94F]" />
              )}
            </span>
            <span className="text-[#C5CAD3] tracking-wide">
              {isConnected ? 'LIVE FEED' : 'CONNECTING'}
            </span>
          </div>

          {/* Market Intel Feed Ticker (Institutional Bloomberg Style) */}
          <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-[4px] bg-[#10141C] border border-[#232936] text-[10px] font-mono">
            <span className="text-[#727B89] uppercase tracking-wider">SENTIMENT</span>
            <span className="h-2.5 w-px bg-[#262D38]" />
            <span className="text-[#36B58F] font-semibold flex items-center gap-1">
              <span className="text-[9px]">▲</span> BULLISH
            </span>
          </div>
        </div>

        <div className="h-4 w-[1px] bg-[#292E37]" />

        {/* External Platform Link */}
        <a
          href="https://crowdwisdomtrading.com"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-[11px] text-[#727B89] hover:text-[#F2F3F5] transition-colors font-mono"
        >
          <span>CrowdWisdomTrading.com</span>
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>
    </header>
  )
}
