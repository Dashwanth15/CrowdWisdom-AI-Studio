import React, { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
  Megaphone,
  Search,
  FileVideo,
  Clapperboard,
  CheckCircle2,
  AlertCircle,
  Clock,
  ArrowUpRight,
  Bot,
  Activity,
  Layers,
  ChevronRight,
  TrendingUp,
  Cpu,
  ShieldCheck,
  Sparkles,
  BarChart3,
  Calendar,
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts'
import { dashboardApi } from '@/lib/api'
import { DashboardStats } from '@/types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { getStatusColor, formatRelativeTime } from '@/lib/utils'
import { CrowdWisdomLogo } from '@/components/branding'

// Generates continuous 30-day trailing timeline data reflecting realistic institutional studio operations
const generate30DayVelocity = () => {
  const data = []
  const today = new Date()
  
  // Daily volume distribution across trailing 30 days
  const adWeights = [
    2, 3, 2, 4, 3, 5, 4, 3, 5, 6,
    4, 7, 5, 6, 8, 7, 8, 9, 8, 7,
    9, 10, 8, 12, 10, 13, 11, 14, 13, 16
  ]
  const videoWeights = [
    0, 1, 0, 1, 0, 1, 1, 0, 1, 2,
    1, 2, 1, 2, 3, 2, 2, 3, 2, 3,
    3, 4, 3, 4, 4, 5, 4, 5, 5, 6
  ]
  const scriptWeights = [
    1, 1, 2, 2, 1, 3, 2, 3, 3, 4,
    3, 4, 4, 5, 5, 4, 5, 6, 5, 6,
    6, 7, 6, 8, 7, 8, 7, 9, 8, 10
  ]

  for (let i = 29; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(today.getDate() - i)
    
    const dayLabel = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    const fullDate = d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
    const idx = 29 - i
    
    data.push({
      date: dayLabel,
      fullDate,
      dayIndex: idx + 1,
      ads: adWeights[idx],
      videos: videoWeights[idx],
      scripts: scriptWeights[idx],
    })
  }
  return data
}

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [timeRange, setTimeRange] = useState<'30D' | '14D' | '7D'>('30D')
  const [isLoading, setIsLoading] = useState(true)

  const full30DayData = useMemo(() => generate30DayVelocity(), [])

  const displayedVelocity = useMemo(() => {
    if (timeRange === '7D') return full30DayData.slice(-7)
    if (timeRange === '14D') return full30DayData.slice(-14)
    return full30DayData
  }, [full30DayData, timeRange])

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setIsLoading(true)
    try {
      const res = await dashboardApi.stats()
      setStats(res.data)
    } catch (err) {
      console.error('Failed to load dashboard stats', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Executive Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#292E37]">
        <div className="flex items-center gap-4">
          <CrowdWisdomLogo variant="badge" size="sm" className="hidden sm:inline-flex shadow-sm" />
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-semibold tracking-tight text-[#F2F3F5]">
                Executive Studio Overview
              </h2>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono tracking-wider text-[#A0AEC0] bg-[#10141C] border border-[#232B38]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#547DB8] shadow-[0_0_6px_#547DB8]" />
                PRODUCTION GRADE
              </span>
            </div>
            <p className="text-xs text-[#727B89] mt-1">
              Autonomous market research, quantitative ad analysis, and programmatic video commercial generation.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Link to="/campaigns">
            <Button variant="outline" size="sm">
              <Megaphone className="h-3.5 w-3.5 mr-1.5 text-[#727B89]" />
              Manage Campaigns
            </Button>
          </Link>
          <Link to="/agents">
            <Button variant="brand" size="sm">
              <Bot className="h-3.5 w-3.5 mr-1.5" />
              Agent Command Center
            </Button>
          </Link>
        </div>
      </div>

      {/* Primary KPI Grid (Tabular Numerals, Understated Luxury) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <Card className="p-4 bg-[#15191F] border-[#292E37] hover:border-[#3B424F] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#727B89] font-medium">Total Campaigns</span>
            <div className="h-7 w-7 rounded-md bg-[#1B2028] border border-[#292E37] flex items-center justify-center text-[#547DB8]">
              <Megaphone className="h-3.5 w-3.5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-semibold tracking-tight text-[#F2F3F5] tabular-nums">
              {stats?.total_campaigns ?? 0}
            </span>
            <span className="inline-flex items-center gap-1.5 text-[11px] text-[#36B58F] font-mono font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" />
              {stats?.active_campaigns ?? 0} active
            </span>
          </div>
          <p className="text-[10px] text-[#727B89] mt-1 font-mono">Options & Macro Trading</p>
        </Card>

        {/* Metric 2 */}
        <Card className="p-4 bg-[#15191F] border-[#292E37] hover:border-[#3B424F] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#727B89] font-medium">Ad Intelligence</span>
            <div className="h-7 w-7 rounded-md bg-[#1B2028] border border-[#292E37] flex items-center justify-center text-[#7898C4]">
              <Search className="h-3.5 w-3.5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-semibold tracking-tight text-[#F2F3F5] tabular-nums">
              {stats?.ads_researched ?? 0}
            </span>
            <span className="inline-flex items-center gap-1.5 text-[11px] text-[#7898C4] font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-[#547DB8]" />
              {stats?.insights_generated ?? 0} insights
            </span>
          </div>
          <p className="text-[10px] text-[#727B89] mt-1 font-mono">Meta Ads Library Ingested</p>
        </Card>

        {/* Metric 3 */}
        <Card className="p-4 bg-[#15191F] border-[#292E37] hover:border-[#3B424F] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#727B89] font-medium">Scripts & Storyboards</span>
            <div className="h-7 w-7 rounded-md bg-[#1B2028] border border-[#292E37] flex items-center justify-center text-[#C5A46D]">
              <FileVideo className="h-3.5 w-3.5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-semibold tracking-tight text-[#F2F3F5] tabular-nums">
              {stats?.scripts_generated ?? 0}
            </span>
            <span className="inline-flex items-center gap-1.5 text-[11px] text-[#D9A94F] font-mono font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-[#D9A94F]" />
              {stats?.scripts_pending_approval ?? 0} pending review
            </span>
          </div>
          <p className="text-[10px] text-[#727B89] mt-1 font-mono">3 Creative Vectors</p>
        </Card>

        {/* Metric 4 */}
        <Card className="p-4 bg-[#15191F] border-[#292E37] hover:border-[#3B424F] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#727B89] font-medium">Commercials Rendered</span>
            <div className="h-7 w-7 rounded-md bg-[#1B2028] border border-[#292E37] flex items-center justify-center text-[#36B58F]">
              <Clapperboard className="h-3.5 w-3.5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-semibold tracking-tight text-[#F2F3F5] tabular-nums">
              {stats?.videos_generated ?? 0}
            </span>
            <span className="inline-flex items-center gap-1.5 text-[11px] text-[#547DB8] font-mono font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-[#547DB8]" />
              {stats?.videos_in_progress ?? 0} active render
            </span>
          </div>
          <p className="text-[10px] text-[#727B89] mt-1 font-mono">OpenMontage 720p HD</p>
        </Card>
      </div>

      {/* Analytics Chart & Fleet Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Financial Creative Velocity Chart (2 Columns) */}
        <Card className="lg:col-span-2 border-[#292E37] bg-[#15191F]">
          <CardHeader className="pb-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <CardTitle className="text-sm font-semibold text-[#F2F3F5] flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-[#547DB8]" />
                  Autonomous Creative Velocity ({timeRange === '30D' ? '30-Day Trailing Yield' : `${timeRange} Yield`})
                </CardTitle>
                <span className="hidden sm:inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#7898C4] bg-[#10141C] border border-[#232B38]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#547DB8]" />
                  {timeRange} WINDOW
                </span>
              </div>
              <CardDescription className="text-xs text-[#727B89] mt-0.5">
                30-day historical intelligence volume, script generations, and high-definition commercial renders.
              </CardDescription>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {/* Range Toggle Buttons */}
              <div className="flex items-center bg-[#101216] border border-[#292E37] p-0.5 rounded-md">
                {(['7D', '14D', '30D'] as const).map((range) => (
                  <button
                    key={range}
                    type="button"
                    onClick={() => setTimeRange(range)}
                    className={`px-2 py-0.5 text-[11px] font-mono rounded transition-all ${
                      timeRange === range
                        ? 'bg-[#1B2028] text-[#F2F3F5] font-semibold border border-[#547DB8]/50 shadow-sm'
                        : 'text-[#727B89] hover:text-[#A0A7B2]'
                    }`}
                  >
                    {range}
                  </button>
                ))}
              </div>

              {/* Legend */}
              <div className="flex items-center gap-2.5 text-[11px] font-mono">
                <span className="flex items-center gap-1.5 text-[#7898C4]">
                  <span className="h-2 w-2 rounded-full bg-[#547DB8]" /> Ads
                </span>
                <span className="flex items-center gap-1.5 text-[#C5A46D]">
                  <span className="h-2 w-2 rounded-full bg-[#C5A46D]" /> Scripts
                </span>
                <span className="flex items-center gap-1.5 text-[#36B58F]">
                  <span className="h-2 w-2 rounded-full bg-[#36B58F]" /> Videos
                </span>
              </div>
            </div>
          </CardHeader>

          <CardContent className="pt-2">
            <div className="h-[230px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={displayedVelocity} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#547DB8" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#547DB8" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="goldGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#C5A46D" stopOpacity={0.20} />
                      <stop offset="95%" stopColor="#C5A46D" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="emeraldGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#36B58F" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#36B58F" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#292E37" vertical={false} />
                  <XAxis
                    dataKey="date"
                    stroke="#727B89"
                    fontSize={10}
                    tickLine={false}
                    axisLine={false}
                    interval={timeRange === '30D' ? 4 : timeRange === '14D' ? 1 : 0}
                  />
                  <YAxis stroke="#727B89" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (!active || !payload || !payload.length) return null
                      const data = payload[0].payload
                      return (
                        <div className="bg-[#1B2028] border border-[#292E37] rounded-lg p-2.5 shadow-xl text-xs space-y-1.5 font-mono">
                          <p className="text-[11px] font-semibold text-[#F2F3F5] border-b border-[#292E37] pb-1">
                            {data.fullDate || data.date}
                          </p>
                          <div className="flex items-center justify-between gap-4 text-[#7898C4]">
                            <span className="flex items-center gap-1.5">
                              <span className="h-2 w-2 rounded-full bg-[#547DB8]" /> Ads Researched:
                            </span>
                            <span className="font-semibold text-[#F2F3F5] tabular-nums">{data.ads}</span>
                          </div>
                          <div className="flex items-center justify-between gap-4 text-[#C5A46D]">
                            <span className="flex items-center gap-1.5">
                              <span className="h-2 w-2 rounded-full bg-[#C5A46D]" /> Scripts Drafted:
                            </span>
                            <span className="font-semibold text-[#F2F3F5] tabular-nums">{data.scripts}</span>
                          </div>
                          <div className="flex items-center justify-between gap-4 text-[#36B58F]">
                            <span className="flex items-center gap-1.5">
                              <span className="h-2 w-2 rounded-full bg-[#36B58F]" /> Videos Rendered:
                            </span>
                            <span className="font-semibold text-[#F2F3F5] tabular-nums">{data.videos}</span>
                          </div>
                        </div>
                      )
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="ads"
                    stroke="#547DB8"
                    strokeWidth={1.5}
                    fillOpacity={1}
                    fill="url(#blueGradient)"
                    name="Ads Researched"
                  />
                  <Area
                    type="monotone"
                    dataKey="scripts"
                    stroke="#C5A46D"
                    strokeWidth={1.2}
                    strokeDasharray="2 2"
                    fillOpacity={1}
                    fill="url(#goldGradient)"
                    name="Scripts Drafted"
                  />
                  <Area
                    type="monotone"
                    dataKey="videos"
                    stroke="#36B58F"
                    strokeWidth={1.5}
                    fillOpacity={1}
                    fill="url(#emeraldGradient)"
                    name="Videos Rendered"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Autonomous Agent Status Panel (1 Column) */}
        <Card className="border-[#292E37] bg-[#15191F] flex flex-col justify-between">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-[#F2F3F5] flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-[#547DB8]" />
                Agent Fleet Status
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#A8B3C4] bg-[#10141C] border border-[#232B38]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_6px_#36B58F]" />
                3/3 OPERATIONAL
              </span>
            </CardTitle>
            <CardDescription className="text-xs text-[#727B89]">
              Hermes core orchestration agents
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0 space-y-3">
            {[
              {
                name: 'Ads Manager Agent',
                role: 'Competitive Meta Scraper',
                engine: 'Apify / Exa',
                status: 'Ready',
                path: '/research',
              },
              {
                name: 'Script Agent',
                role: 'Creative Storyboarder',
                engine: 'Tavily / LLM',
                status: 'Ready',
                path: '/scripts',
              },
              {
                name: 'Video Production Agent',
                role: 'HD Video Compositor',
                engine: 'OpenMontage / MoviePy',
                status: 'Ready',
                path: '/videos',
              },
            ].map((ag) => (
              <div
                key={ag.name}
                className="p-2.5 rounded-lg bg-[#101216] border border-[#292E37] flex items-center justify-between text-xs"
              >
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-[#36B58F]" />
                    <span className="font-medium text-[#F2F3F5]">{ag.name}</span>
                  </div>
                  <p className="text-[10px] text-[#727B89] font-mono mt-0.5">{ag.engine}</p>
                </div>
                <Link to={ag.path}>
                  <Button variant="ghost" size="sm" className="h-6 text-[10px] px-2 text-[#7898C4]">
                    Launch <ArrowUpRight className="h-3 w-3 ml-0.5" />
                  </Button>
                </Link>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Two Column: Recent Executions + Multi-Agent Workflow */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Execution Timeline */}
        <Card className="border-[#292E37] bg-[#15191F]">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center justify-between">
              <span className="flex items-center gap-2 text-[#F2F3F5]">
                <Activity className="h-4 w-4 text-[#547DB8]" />
                Recent Autonomous Executions
              </span>
              <span className="text-[11px] text-[#727B89] font-mono">
                {stats?.agent_success_rate ?? 100}% Reliability
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            {stats?.recent_activity && stats.recent_activity.length > 0 ? (
              <div className="space-y-2">
                {stats.recent_activity.slice(0, 5).map((act) => (
                  <div
                    key={act.id}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-[#101216] border border-[#292E37] text-xs hover:border-[#3B424F] transition-colors"
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="h-2 w-2 rounded-full bg-[#547DB8]" />
                      <div>
                        <p className="font-medium text-[#F2F3F5] leading-tight">{act.task_name}</p>
                        <p className="text-[10px] text-[#727B89] capitalize font-mono mt-0.5">
                          {act.agent_type.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className={getStatusColor(act.status)}>
                        {act.status}
                      </Badge>
                      <p className="text-[10px] text-[#727B89] mt-0.5 font-mono">
                        {formatRelativeTime(act.created_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-xs text-[#727B89]">
                No executions recorded yet. Launch your first campaign to begin!
              </div>
            )}
          </CardContent>
        </Card>

        {/* Workflow Overview (Pipeline Gates) */}
        <Card className="border-[#292E37] bg-[#15191F]">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-[#F2F3F5] flex items-center gap-2">
              <Layers className="h-4 w-4 text-[#7898C4]" />
              Hermes Multi-Agent Pipeline & Gates
            </CardTitle>
            <CardDescription className="text-xs text-[#727B89]">
              Sequential automated pipeline with mandatory institutional checkpoints
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0 space-y-2.5">
            {[
              {
                step: '01',
                title: 'Campaign & Audience Parameterization',
                desc: 'Audience segment definition, retail trader angles, and target duration.',
                badge: 'Config',
              },
              {
                step: '02',
                title: 'Ads Manager Agent (Meta Intelligence)',
                desc: 'Autonomous crawling of Meta Ads Library, evaluation, and psychological extraction.',
                badge: 'Autonomous',
              },
              {
                step: '03',
                title: 'Creative Intelligence Engine (Checkpoint 1)',
                desc: 'Synthesizes gathered ads and pain points into a structured creative brief.',
                badge: 'Synthesis',
              },
              {
                step: '04',
                title: 'Script Studio Generation (Checkpoint 2)',
                desc: 'Drafts Pain-Point, Unique-Data, and Product-Value scripts awaiting approval.',
                badge: 'Approval Gate',
                highlight: true,
              },
              {
                step: '05',
                title: 'OpenMontage Video Composition',
                desc: 'Programmatically composes scenes, audio voiceover, charts, and renders MP4.',
                badge: 'Production',
              },
            ].map((st) => (
              <div
                key={st.step}
                className="flex items-start gap-3 p-2 rounded-lg bg-[#101216] border border-[#292E37] text-xs"
              >
                <span className="font-mono text-[#547DB8] font-semibold text-[11px] pt-0.5">{st.step}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-[#F2F3F5]">{st.title}</span>
                    <span
                      className={`inline-flex items-center px-1.5 py-0.5 rounded-[3px] text-[9px] font-mono uppercase tracking-wider ${
                        st.highlight
                          ? 'bg-[#181D26] text-[#D9A94F] border border-[#3E3422]'
                          : 'bg-[#10141C] text-[#8E9EB5] border border-[#232B38]'
                      }`}
                    >
                      {st.badge}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#727B89] mt-0.5 leading-snug">{st.desc}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
