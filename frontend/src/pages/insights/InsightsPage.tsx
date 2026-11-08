import React, { useState, useEffect } from 'react'
import {
  Sparkles,
  AlertTriangle,
  Lightbulb,
  Compass,
  Users,
  Eye,
  CheckCircle2,
  TrendingUp,
  Brain,
} from 'lucide-react'
import { researchApi } from '@/lib/api'
import { MarketingInsight } from '@/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import toast from 'react-hot-toast'

const CATEGORY_MAP: Record<string, { label: string; icon: any; color: string; bg: string; border: string }> = {
  pain_point: { label: 'Customer Pain Points', icon: AlertTriangle, color: 'text-[#D9A94F]', bg: 'bg-[#D9A94F]/10', border: 'border-[#D9A94F]/30' },
  angle: { label: 'Advertising Angles', icon: Compass, color: 'text-[#547DB8]', bg: 'bg-[#547DB8]/10', border: 'border-[#547DB8]/30' },
  hook: { label: 'High-Converting Hooks', icon: Lightbulb, color: 'text-[#C5A46D]', bg: 'bg-[#C5A46D]/10', border: 'border-[#C5A46D]/30' },
  audience: { label: 'Audience Motivations', icon: Users, color: 'text-[#36B58F]', bg: 'bg-[#36B58F]/10', border: 'border-[#36B58F]/30' },
  competitor: { label: 'Competitor Positioning', icon: Eye, color: 'text-[#D66C73]', bg: 'bg-[#D66C73]/10', border: 'border-[#D66C73]/30' },
  pattern: { label: 'Creative Patterns', icon: Sparkles, color: 'text-[#7898C4]', bg: 'bg-[#7898C4]/10', border: 'border-[#7898C4]/30' },
}

export const InsightsPage: React.FC = () => {
  const [insights, setInsights] = useState<MarketingInsight[]>([])
  const [activeCategory, setActiveCategory] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadInsights()
  }, [])

  const loadInsights = async () => {
    setIsLoading(true)
    try {
      const res = await researchApi.listInsights({ limit: 100 })
      setInsights(res.data)
    } catch (err) {
      toast.error('Failed to load marketing intelligence')
    } finally {
      setIsLoading(false)
    }
  }

  const filteredInsights = insights.filter((ins) => {
    if (activeCategory === 'all') return true
    return ins.category === activeCategory
  })

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#292E37]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#C5A46D] px-2 py-0.5 rounded bg-[#C5A46D]/10 border border-[#C5A46D]/20">
              Cognitive Synthesis
            </span>
            <span className="text-xs text-[#727B89] font-mono">• Multi-Angle Competitor Extraction</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
            <Brain className="h-6 w-6 text-[#547DB8]" />
            Marketing Intelligence & Strategy
          </h1>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            AI-extracted customer pain points, competitor positioning, and high-impact advertising angles.
          </p>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 pb-2 overflow-x-auto">
        <Button
          variant={activeCategory === 'all' ? 'secondary' : 'ghost'}
          size="sm"
          className={`h-8 text-xs border ${
            activeCategory === 'all'
              ? 'bg-[#1B2028] text-[#F2F3F5] border-[#547DB8]/50'
              : 'border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#1B2028]'
          }`}
          onClick={() => setActiveCategory('all')}
        >
          All Insights ({insights.length})
        </Button>
        {Object.entries(CATEGORY_MAP).map(([key, info]) => {
          const count = insights.filter((i) => i.category === key).length
          const isActive = activeCategory === key
          return (
            <Button
              key={key}
              variant={isActive ? 'secondary' : 'ghost'}
              size="sm"
              className={`h-8 text-xs border ${
                isActive
                  ? 'bg-[#1B2028] text-[#F2F3F5] border-[#547DB8]/50'
                  : 'border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#1B2028]'
              }`}
              onClick={() => setActiveCategory(key)}
            >
              <info.icon className={`h-3.5 w-3.5 mr-1.5 ${info.color}`} />
              {info.label} ({count})
            </Button>
          )
        })}
      </div>

      {/* Insights Matrix Grid */}
      {filteredInsights.length === 0 ? (
        <Card className="p-12 text-center border-dashed border-[#292E37] bg-[#15191F]">
          <Brain className="h-8 w-8 text-[#727B89] mx-auto mb-2 opacity-50" />
          <p className="text-xs text-[#A0A7B2]">
            No marketing insights discovered yet. Run the Ads Manager Agent on a campaign to extract intelligence.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredInsights.map((ins) => {
            const catInfo = CATEGORY_MAP[ins.category] || {
              label: ins.category,
              icon: Sparkles,
              color: 'text-[#547DB8]',
              bg: 'bg-[#547DB8]/10',
              border: 'border-[#547DB8]/30',
            }
            const Icon = catInfo.icon

            return (
              <Card key={ins.id} className="border-[#292E37] bg-[#15191F] hover:border-[#547DB8]/40 transition-all flex flex-col justify-between">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs font-semibold">
                      <Icon className={`h-4 w-4 ${catInfo.color}`} />
                      <span className="text-[#F2F3F5]">{catInfo.label}</span>
                    </div>
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38] tabular-nums">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" />
                      {Math.round(ins.confidence * 100)}% CONFIDENCE
                    </span>
                  </div>
                  <CardTitle className="text-sm font-semibold mt-2 text-[#F2F3F5]">
                    {ins.title}
                  </CardTitle>
                </CardHeader>

                <CardContent className="pt-0 space-y-3">
                  <p className="text-xs text-[#A0A7B2] leading-relaxed">
                    {ins.description}
                  </p>

                  {/* Supporting Evidence List */}
                  {ins.evidence && ins.evidence.length > 0 && (
                    <div className="p-2.5 rounded-lg bg-[#101216] border border-[#292E37] space-y-1">
                      <span className="text-[10px] uppercase font-mono font-semibold text-[#727B89] block">
                        Supporting Observations:
                      </span>
                      <ul className="space-y-1">
                        {ins.evidence.map((ev, idx) => (
                          <li key={idx} className="text-[11px] text-[#A0A7B2] flex items-start gap-1.5">
                            <span className="text-[#547DB8] mt-0.5">•</span>
                            <span>{ev}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
