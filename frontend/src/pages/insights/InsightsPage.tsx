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
  ShieldCheck,
  ShieldAlert,
  Server,
  Activity,
  Globe,
  ArrowRight,
  BookOpen,
} from 'lucide-react'
import { researchApi, marketIntelligenceApi } from '@/lib/api'
import { MarketingInsight } from '@/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import toast from 'react-hot-toast'

const CATEGORY_MAP: Record<string, { label: string; icon: any; color: string; bg: string; border: string }> = {
  competitor_positioning: { label: 'Competitor Positioning', icon: Eye, color: 'text-[#D66C73]', bg: 'bg-[#D66C73]/10', border: 'border-[#D66C73]/30' },
  common_marketing_hooks: { label: 'Common Marketing Hooks', icon: Lightbulb, color: 'text-[#C5A46D]', bg: 'bg-[#C5A46D]/10', border: 'border-[#C5A46D]/30' },
  customer_pain_points: { label: 'Customer Pain Points', icon: AlertTriangle, color: 'text-[#D9A94F]', bg: 'bg-[#D9A94F]/10', border: 'border-[#D9A94F]/30' },
  value_propositions: { label: 'Value Propositions', icon: Compass, color: 'text-[#547DB8]', bg: 'bg-[#547DB8]/10', border: 'border-[#547DB8]/30' },
  audience_objections: { label: 'Audience Objections', icon: Users, color: 'text-[#E07A5F]', bg: 'bg-[#E07A5F]/10', border: 'border-[#E07A5F]/30' },
  content_strategies: { label: 'Content Strategies', icon: Sparkles, color: 'text-[#7898C4]', bg: 'bg-[#7898C4]/10', border: 'border-[#7898C4]/30' },
  market_opportunities: { label: 'Market Opportunities', icon: TrendingUp, color: 'text-[#36B58F]', bg: 'bg-[#36B58F]/10', border: 'border-[#36B58F]/30' },
  gaps_in_messaging: { label: 'Gaps in Competitor Messaging', icon: Brain, color: 'text-[#9B5DE5]', bg: 'bg-[#9B5DE5]/10', border: 'border-[#9B5DE5]/30' },
  // Legacy mappings
  pain_point: { label: 'Customer Pain Points', icon: AlertTriangle, color: 'text-[#D9A94F]', bg: 'bg-[#D9A94F]/10', border: 'border-[#D9A94F]/30' },
  angle: { label: 'Advertising Angles', icon: Compass, color: 'text-[#547DB8]', bg: 'bg-[#547DB8]/10', border: 'border-[#547DB8]/30' },
  hook: { label: 'High-Converting Hooks', icon: Lightbulb, color: 'text-[#C5A46D]', bg: 'bg-[#C5A46D]/10', border: 'border-[#C5A46D]/30' },
  audience: { label: 'Audience Motivations', icon: Users, color: 'text-[#36B58F]', bg: 'bg-[#36B58F]/10', border: 'border-[#36B58F]/30' },
  competitor: { label: 'Competitor Positioning', icon: Eye, color: 'text-[#D66C73]', bg: 'bg-[#D66C73]/10', border: 'border-[#D66C73]/30' },
}

export const InsightsPage: React.FC = () => {
  const [insights, setInsights] = useState<MarketingInsight[]>([])
  const [activeCategory, setActiveCategory] = useState<string>('all')
  const [activeTab, setActiveTab] = useState<'insights' | 'comparison' | 'diagnostics'>('insights')
  const [providerHealth, setProviderHealth] = useState<any>(null)
  const [comparisonData, setComparisonData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadInsights()
    loadProviderHealth()
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

  const loadProviderHealth = async () => {
    try {
      const res = await marketIntelligenceApi.getProviderHealth()
      setProviderHealth(res.data)
    } catch (err) {
      console.warn('Provider diagnostics notice:', err)
    }
  }

  const loadComparison = async () => {
    if (comparisonData) return
    try {
      const res = await marketIntelligenceApi.getComparison()
      setComparisonData(res.data)
    } catch (err) {
      toast.error('Failed to load market comparison data')
    }
  }

  const handleTabChange = (tab: 'insights' | 'comparison' | 'diagnostics') => {
    setActiveTab(tab)
    if (tab === 'comparison') loadComparison()
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
              Evidence-Grounded Intelligence
            </span>
            <span className="text-xs text-[#727B89] font-mono">• Research Intelligence 2.0</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
            <Brain className="h-6 w-6 text-[#547DB8]" />
            Marketing Intelligence & Evidence Strategy
          </h1>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            Empirical customer pain points, competitor positioning, and verified marketing opportunities for India 🇮🇳 and the Philippines 🇵🇭.
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-[#15191F] border border-[#292E37] rounded-lg">
          <Button
            size="sm"
            variant={activeTab === 'insights' ? 'secondary' : 'ghost'}
            className="text-xs h-7 px-3"
            onClick={() => handleTabChange('insights')}
          >
            Insights Matrix
          </Button>
          <Button
            size="sm"
            variant={activeTab === 'comparison' ? 'secondary' : 'ghost'}
            className="text-xs h-7 px-3"
            onClick={() => handleTabChange('comparison')}
          >
            <Globe className="h-3 w-3 mr-1 text-[#547DB8]" />
            Dual-Market Comparison
          </Button>
          <Button
            size="sm"
            variant={activeTab === 'diagnostics' ? 'secondary' : 'ghost'}
            className="text-xs h-7 px-3"
            onClick={() => handleTabChange('diagnostics')}
          >
            <Server className="h-3 w-3 mr-1 text-[#36B58F]" />
            Provider Diagnostics
          </Button>
        </div>
      </div>

      {/* Provider Health Mini-Status Bar */}
      {providerHealth && (
        <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-lg bg-[#10141C] border border-[#232B38] text-xs">
          <div className="flex items-center gap-2 font-mono text-[11px] text-[#A0A7B2]">
            <span className="font-semibold text-[#F2F3F5]">INTEGRATION HEALTH:</span>
            <span>Research: <span className="text-[#36B58F] font-semibold">{providerHealth.active_research_pipeline}</span></span>
            <span>•</span>
            <span>Ads: <span className="text-[#547DB8] font-semibold">{providerHealth.active_ads_pipeline}</span></span>
            <span>•</span>
            <span>LLM: <span className="text-[#C5A46D] font-semibold">{providerHealth.active_llm_pipeline}</span></span>
          </div>

          <div className="flex items-center gap-2">
            {Object.entries(providerHealth.providers || {}).map(([key, prov]: [string, any]) => {
              const isLive = prov.status === 'LIVE_AND_VERIFIED'
              const isQuota = prov.status === 'QUOTA_EXCEEDED'
              const isAuthFail = prov.status === 'AUTHENTICATION_FAILED'
              return (
                <span
                  key={key}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                    isLive
                      ? 'bg-[#36B58F]/10 border-[#36B58F]/30 text-[#36B58F]'
                      : isQuota
                      ? 'bg-[#D9A94F]/10 border-[#D9A94F]/30 text-[#D9A94F]'
                      : isAuthFail
                      ? 'bg-[#D66C73]/10 border-[#D66C73]/30 text-[#D66C73]'
                      : 'bg-[#15191F] border-[#292E37] text-[#727B89]'
                  }`}
                  title={prov.error || prov.status}
                >
                  {prov.provider}: {isLive ? `${prov.latency_ms}ms` : prov.status.replace(/_/g, ' ')}
                </span>
              )
            })}
          </div>
        </div>
      )}

      {/* TAB 1: INSIGHTS MATRIX */}
      {activeTab === 'insights' && (
        <div className="space-y-4">
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
              if (count === 0 && !['competitor_positioning', 'customer_pain_points', 'market_opportunities'].includes(key)) return null
              const isActive = activeCategory === key
              return (
                <Button
                  key={key}
                  variant={isActive ? 'secondary' : 'ghost'}
                  size="sm"
                  className={`h-8 text-xs border whitespace-nowrap ${
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
                  label: ins.category.replace(/_/g, ' '),
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
                      <CardTitle className="text-sm font-semibold mt-2 text-[#F2F3F5] leading-snug">
                        {ins.title}
                      </CardTitle>
                    </CardHeader>

                    <CardContent className="pt-0 space-y-3">
                      {/* AI Strategic Interpretation */}
                      <div>
                        <span className="text-[10px] uppercase font-mono font-semibold text-[#547DB8] block mb-0.5">
                          AI Strategic Interpretation:
                        </span>
                        <p className="text-xs text-[#A0A7B2] leading-relaxed">
                          {ins.ai_interpretation || ins.description}
                        </p>
                      </div>

                      {/* Supporting Observed Evidence */}
                      {((ins.observed_evidence && ins.observed_evidence.length > 0) || (ins.evidence && ins.evidence.length > 0)) && (
                        <div className="p-2.5 rounded-lg bg-[#101216] border border-[#292E37] space-y-1">
                          <span className="text-[10px] uppercase font-mono font-semibold text-[#36B58F] block">
                            Observed Evidence & Citations:
                          </span>
                          <ul className="space-y-1">
                            {(ins.observed_evidence || ins.evidence || []).map((ev, idx) => (
                              <li key={idx} className="text-[11px] text-[#A0A7B2] flex items-start gap-1.5">
                                <span className="text-[#36B58F] mt-0.5">•</span>
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
      )}

      {/* TAB 2: DUAL-MARKET COMPARISON */}
      {activeTab === 'comparison' && (
        <div className="space-y-6">
          <div className="p-4 rounded-lg bg-[#15191F] border border-[#292E37]">
            <h2 className="text-sm font-semibold text-[#F2F3F5] mb-1 flex items-center gap-2">
              <Globe className="h-4 w-4 text-[#547DB8]" />
              Comparative Market Framework: India 🇮🇳 vs Philippines 🇵🇭
            </h2>
            <p className="text-xs text-[#A0A7B2]">
              Side-by-side empirical research findings across the 8 strategic marketing intelligence categories.
            </p>
          </div>

          {comparisonData ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* India Column */}
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-[#D9A94F]/10 border border-[#D9A94F]/30 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">🇮🇳</span>
                    <span className="text-sm font-semibold text-[#F2F3F5]">India Financial Market</span>
                  </div>
                  <Badge variant="outline" className="border-[#D9A94F]/40 text-[#D9A94F] text-[10px]">
                    Derivatives & Equity (NSE/BSE)
                  </Badge>
                </div>

                {(comparisonData.IN?.analysis?.insights || []).map((item: any, idx: number) => (
                  <Card key={idx} className="border-[#292E37] bg-[#15191F]">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="text-[10px] border-[#547DB8]/30 text-[#547DB8]">
                          {item.category.replace(/_/g, ' ').toUpperCase()}
                        </Badge>
                        <span className="text-[10px] font-mono text-[#36B58F]">
                          {Math.round((item.confidence || 0.9) * 100)}% CONFIDENCE
                        </span>
                      </div>
                      <CardTitle className="text-xs font-semibold text-[#F2F3F5] mt-1">
                        {item.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0 space-y-2 text-xs">
                      <div className="p-2 rounded bg-[#101216] border border-[#292E37]">
                        <span className="text-[10px] font-mono font-semibold text-[#36B58F] block mb-0.5">Observed Evidence:</span>
                        <ul className="space-y-0.5 text-[11px] text-[#A0A7B2]">
                          {(item.observed_evidence || []).map((ev: string, i: number) => (
                            <li key={i}>• {ev}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <span className="text-[10px] font-mono font-semibold text-[#547DB8] block mb-0.5">Strategic Implication:</span>
                        <p className="text-[11px] text-[#A0A7B2]">{item.ai_interpretation}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Philippines Column */}
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-[#547DB8]/10 border border-[#547DB8]/30 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">🇵🇭</span>
                    <span className="text-sm font-semibold text-[#F2F3F5]">Philippines Financial Market</span>
                  </div>
                  <Badge variant="outline" className="border-[#547DB8]/40 text-[#547DB8] text-[10px]">
                    Equities & REITs (PSE/BSP)
                  </Badge>
                </div>

                {(comparisonData.PH?.analysis?.insights || []).map((item: any, idx: number) => (
                  <Card key={idx} className="border-[#292E37] bg-[#15191F]">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="text-[10px] border-[#547DB8]/30 text-[#547DB8]">
                          {item.category.replace(/_/g, ' ').toUpperCase()}
                        </Badge>
                        <span className="text-[10px] font-mono text-[#36B58F]">
                          {Math.round((item.confidence || 0.9) * 100)}% CONFIDENCE
                        </span>
                      </div>
                      <CardTitle className="text-xs font-semibold text-[#F2F3F5] mt-1">
                        {item.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0 space-y-2 text-xs">
                      <div className="p-2 rounded bg-[#101216] border border-[#292E37]">
                        <span className="text-[10px] font-mono font-semibold text-[#36B58F] block mb-0.5">Observed Evidence:</span>
                        <ul className="space-y-0.5 text-[11px] text-[#A0A7B2]">
                          {(item.observed_evidence || []).map((ev: string, i: number) => (
                            <li key={i}>• {ev}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <span className="text-[10px] font-mono font-semibold text-[#547DB8] block mb-0.5">Strategic Implication:</span>
                        <p className="text-[11px] text-[#A0A7B2]">{item.ai_interpretation}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ) : (
            <Card className="p-12 text-center border-[#292E37] bg-[#15191F]">
              <Globe className="h-8 w-8 text-[#547DB8] mx-auto mb-2 opacity-50 animate-pulse" />
              <p className="text-xs text-[#A0A7B2]">Loading live dual-market comparison data...</p>
            </Card>
          )}
        </div>
      )}

      {/* TAB 3: PROVIDER DIAGNOSTICS */}
      {activeTab === 'diagnostics' && providerHealth && (
        <div className="space-y-4">
          <Card className="border-[#292E37] bg-[#15191F]">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-[#F2F3F5] flex items-center gap-2">
                <Server className="h-4 w-4 text-[#36B58F]" />
                Research Engine Integration Health & Latency Telemetry
              </CardTitle>
              <CardDescription className="text-xs text-[#A0A7B2]">
                Real-time operational status across external search, scraping, and LLM synthesis providers.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(providerHealth.providers || {}).map(([key, prov]: [string, any]) => {
                  const isLive = prov.status === 'LIVE_AND_VERIFIED'
                  const isQuota = prov.status === 'QUOTA_EXCEEDED'
                  const isAuthFail = prov.status === 'AUTHENTICATION_FAILED'
                  return (
                    <div
                      key={key}
                      className="p-3.5 rounded-lg bg-[#10141C] border border-[#232B38] space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold text-[#F2F3F5]">{prov.provider}</span>
                        <Badge
                          variant="outline"
                          className={`text-[10px] font-mono ${
                            isLive
                              ? 'border-[#36B58F]/40 text-[#36B58F] bg-[#36B58F]/10'
                              : isQuota
                              ? 'border-[#D9A94F]/40 text-[#D9A94F] bg-[#D9A94F]/10'
                              : 'border-[#D66C73]/40 text-[#D66C73] bg-[#D66C73]/10'
                          }`}
                        >
                          {prov.status.replace(/_/g, ' ')}
                        </Badge>
                      </div>

                      <div className="space-y-1 text-[11px] font-mono text-[#A0A7B2]">
                        <div className="flex justify-between">
                          <span>Role:</span>
                          <span className="text-[#F2F3F5]">{prov.category}</span>
                        </div>
                        {prov.latency_ms && (
                          <div className="flex justify-between">
                            <span>Latency:</span>
                            <span className="text-[#36B58F]">{prov.latency_ms} ms</span>
                          </div>
                        )}
                        {prov.model && (
                          <div className="flex justify-between">
                            <span>Model:</span>
                            <span className="text-[#C5A46D]">{prov.model}</span>
                          </div>
                        )}
                        {prov.account_username && (
                          <div className="flex justify-between">
                            <span>Account:</span>
                            <span className="text-[#547DB8]">{prov.account_username}</span>
                          </div>
                        )}
                        {prov.monthly_credits_usd && (
                          <div className="flex justify-between">
                            <span>Monthly Credits:</span>
                            <span className="text-[#36B58F]">${prov.monthly_credits_usd}.00</span>
                          </div>
                        )}
                      </div>

                      {prov.error && (
                        <div className="p-2 rounded bg-[#D66C73]/10 border border-[#D66C73]/20 text-[10px] text-[#D66C73]">
                          {prov.error}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
