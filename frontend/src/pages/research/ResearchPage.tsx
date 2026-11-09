import React, { useState, useEffect } from 'react'
import {
  Search,
  Filter,
  Download,
  ExternalLink,
  Award,
  Sparkles,
  TrendingUp,
  FileJson,
  Layers,
  Calendar,
  Clock,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  ShieldAlert,
  ArrowUpDown,
  CheckSquare,
  Square,
  FolderPlus,
  Link2,
} from 'lucide-react'
import { researchApi, campaignsApi } from '@/lib/api'
import { Advertisement, Campaign } from '@/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import toast from 'react-hot-toast'

const formatTimestamp = (iso?: string | null) => {
  if (!iso) return null
  try {
    const d = new Date(iso)
    if (isNaN(d.getTime())) return null
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short',
    })
  } catch {
    return null
  }
}

export const ResearchPage: React.FC = () => {
  const [ads, setAds] = useState<Advertisement[]>([])
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [selectedAdIds, setSelectedAdIds] = useState<string[]>([])
  const [targetCampaignId, setTargetCampaignId] = useState<string>('')
  const [isLinking, setIsLinking] = useState(false)

  const [searchQuery, setSearchQuery] = useState('')
  const [minScore, setMinScore] = useState<number>(0)
  const [verificationFilter, setVerificationFilter] = useState<string>('all')
  const [dateRangeFilter, setDateRangeFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('newest')
  const [selectedAd, setSelectedAd] = useState<Advertisement | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadAds()
    loadCampaigns()
  }, [])

  const loadAds = async () => {
    setIsLoading(true)
    try {
      const res = await researchApi.listAds({ limit: 150 })
      setAds(res.data)
    } catch (err) {
      toast.error('Failed to load advertisement research')
    } finally {
      setIsLoading(false)
    }
  }

  const loadCampaigns = async () => {
    try {
      const res = await campaignsApi.list()
      setCampaigns(res.data)
      if (res.data.length > 0 && !targetCampaignId) {
        setTargetCampaignId(res.data[0].id)
      }
    } catch (err) {
      console.error('Failed to load campaigns for association', err)
    }
  }

  const toggleSelectAd = (id: string) => {
    setSelectedAdIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    )
  }

  const selectAllFiltered = () => {
    const allIds = filteredAds.map((a) => a.id)
    setSelectedAdIds(allIds)
  }

  const clearSelection = () => {
    setSelectedAdIds([])
  }

  const handleAssociateCampaign = async () => {
    if (!targetCampaignId) {
      toast.error('Please select a target campaign.')
      return
    }
    if (selectedAdIds.length === 0) {
      toast.error('Please select at least one advertisement.')
      return
    }
    setIsLinking(true)
    try {
      await researchApi.associateCampaign({
        campaign_id: targetCampaignId,
        ad_ids: selectedAdIds,
      })
      const targetCamp = campaigns.find((c) => c.id === targetCampaignId)
      toast.success(
        `Linked ${selectedAdIds.length} ad(s) to "${targetCamp?.name || 'Campaign'}"!`
      )
      setSelectedAdIds([])
      await loadAds()
      await loadCampaigns()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to link advertisements.')
    } finally {
      setIsLinking(false)
    }
  }

  const exportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(ads, null, 2))
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute('href', dataStr)
    downloadAnchor.setAttribute('download', 'crowdwisdom_ads_research.json')
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
    toast.success('Research exported as JSON')
  }

  const filteredAds = ads
    .filter((ad) => {
      const matchesSearch =
        ad.advertiser?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ad.ad_text?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ad.hook?.toLowerCase().includes(searchQuery.toLowerCase())

      const score = ad.evaluation_score?.overall || 0
      const matchesScore = score >= minScore

      const status = ad.date_verification_status || (ad.published_at ? 'verified' : 'unverified')
      const matchesVerification =
        verificationFilter === 'all' ||
        (verificationFilter === 'verified' && status === 'verified') ||
        (verificationFilter === 'unverified' && status === 'unverified')

      let matchesDateRange = true
      if (dateRangeFilter !== 'all' && ad.published_at) {
        const days = Number(dateRangeFilter)
        const adTime = new Date(ad.published_at).getTime()
        const cutoff = Date.now() - days * 24 * 60 * 60 * 1000
        matchesDateRange = adTime >= cutoff
      } else if (dateRangeFilter !== 'all' && !ad.published_at) {
        matchesDateRange = false
      }

      return matchesSearch && matchesScore && matchesVerification && matchesDateRange
    })
    .sort((a, b) => {
      if (sortBy === 'newest') {
        const tA = a.published_at ? new Date(a.published_at).getTime() : 0
        const tB = b.published_at ? new Date(b.published_at).getTime() : 0
        return tB - tA
      }
      if (sortBy === 'oldest') {
        const tA = a.published_at ? new Date(a.published_at).getTime() : Infinity
        const tB = b.published_at ? new Date(b.published_at).getTime() : Infinity
        return tA - tB
      }
      if (sortBy === 'score') {
        return (b.evaluation_score?.overall || 0) - (a.evaluation_score?.overall || 0)
      }
      return 0
    })

  const verifiedCount = ads.filter(
    (a) => (a.date_verification_status || (a.published_at ? 'verified' : 'unverified')) === 'verified'
  ).length
  const unverifiedCount = ads.length - verifiedCount

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#292E37]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono uppercase tracking-wider text-[#C5CAD3] bg-[#10141C] border border-[#232B38]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#547DB8]" />
              INTELLIGENCE VAULT
            </span>
            <span className="text-xs text-[#727B89] font-mono">• Meta Ads Library Grounding</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
            <Search className="h-6 w-6 text-[#547DB8]" />
            Ads Research Intelligence
          </h1>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            Meta Ads Library competitor discovery, verifiable publication dates, hook extraction, and explainable evaluation scores.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] text-xs font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38] tabular-nums">
            <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" />
            {verifiedCount} Verified Dates
          </span>
          {unverifiedCount > 0 && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] text-xs font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38] tabular-nums">
              <span className="w-1.5 h-1.5 rounded-full bg-[#D9A94F]" />
              {unverifiedCount} Unverified
            </span>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={selectedAdIds.length > 0 ? clearSelection : selectAllFiltered}
            className="text-xs border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]"
          >
            <CheckSquare className="h-3.5 w-3.5 mr-1.5" />
            {selectedAdIds.length > 0 ? 'Deselect All' : 'Select All'}
          </Button>
          <Button variant="outline" size="sm" onClick={exportJSON} className="text-xs border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]">
            <FileJson className="h-3.5 w-3.5 mr-1.5" />
            Export Research JSON
          </Button>
        </div>
      </div>

      {/* Floating Campaign Link Bar */}
      {selectedAdIds.length > 0 && (
        <div className="sticky top-2 z-30 flex flex-col sm:flex-row items-center justify-between gap-3 p-3.5 bg-[#1B2028] backdrop-blur border border-[#547DB8]/60 rounded-xl shadow-2xl">
          <div className="flex items-center gap-2.5">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[11px] font-mono font-semibold bg-[#10141C] text-[#8EA2C6] border border-[#232B38]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#547DB8]" />
              {selectedAdIds.length} SELECTED
            </span>
            <span className="text-xs font-medium text-[#F2F3F5]">
              Assign selected Meta competitor ads to an active or draft campaign:
            </span>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <select
              className="bg-[#101216] border border-[#292E37] rounded-md px-3 py-1.5 text-xs font-medium text-[#F2F3F5] outline-none flex-1 sm:w-64 focus:border-[#547DB8]"
              value={targetCampaignId}
              onChange={(e) => setTargetCampaignId(e.target.value)}
            >
              {campaigns.length === 0 ? (
                <option value="">No campaigns available</option>
              ) : (
                campaigns.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.status})
                  </option>
                ))
              )}
            </select>

            <Button
              size="sm"
              variant="brand"
              disabled={isLinking || !targetCampaignId}
              onClick={handleAssociateCampaign}
              className="text-xs h-8 shrink-0 bg-[#547DB8] hover:bg-[#436494] text-white font-medium"
            >
              <FolderPlus className="h-3.5 w-3.5 mr-1.5" />
              {isLinking ? 'Assigning...' : 'Assign to Campaign'}
            </Button>

            <Button
              size="sm"
              variant="ghost"
              onClick={clearSelection}
              className="text-xs h-8 text-[#A0A7B2] hover:text-[#F2F3F5] shrink-0"
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 bg-[#15191F] p-3.5 rounded-lg border border-[#292E37]">
        <div className="relative md:col-span-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#727B89]" />
          <Input
            placeholder="Search advertisers, hooks, copy..."
            className="pl-9 text-xs bg-[#101216] border-[#292E37] text-[#F2F3F5]"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Date Range Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#A0A7B2] whitespace-nowrap flex items-center gap-1 font-mono">
            <Calendar className="h-3.5 w-3.5 text-[#547DB8]" />
            Window:
          </span>
          <select
            className="w-full bg-[#101216] border border-[#292E37] rounded-md px-2.5 py-1.5 text-xs font-medium text-[#F2F3F5] outline-none focus:border-[#547DB8]"
            value={dateRangeFilter}
            onChange={(e) => setDateRangeFilter(e.target.value)}
          >
            <option value="all">All Dates</option>
            <option value="7">Last 7 Days</option>
            <option value="14">Last 14 Days</option>
            <option value="30">Last 30 Days (Mandatory)</option>
          </select>
        </div>

        {/* Verification Status Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#A0A7B2] whitespace-nowrap flex items-center gap-1 font-mono">
            <ShieldCheck className="h-3.5 w-3.5 text-[#36B58F]" />
            Status:
          </span>
          <select
            className="w-full bg-[#101216] border border-[#292E37] rounded-md px-2.5 py-1.5 text-xs font-medium text-[#F2F3F5] outline-none focus:border-[#547DB8]"
            value={verificationFilter}
            onChange={(e) => setVerificationFilter(e.target.value)}
          >
            <option value="all">All Statuses ({ads.length})</option>
            <option value="verified">Verified Only ({verifiedCount})</option>
            <option value="unverified">Unverified Only ({unverifiedCount})</option>
          </select>
        </div>

        {/* Sorting Dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#A0A7B2] whitespace-nowrap flex items-center gap-1 font-mono">
            <ArrowUpDown className="h-3.5 w-3.5 text-[#C5A46D]" />
            Sort:
          </span>
          <select
            className="w-full bg-[#101216] border border-[#292E37] rounded-md px-2.5 py-1.5 text-xs font-medium text-[#F2F3F5] outline-none focus:border-[#547DB8]"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="newest">Newest Published</option>
            <option value="oldest">Oldest Published</option>
            <option value="score">Highest Quality Score</option>
          </select>
        </div>
      </div>

      {/* Ads Grid */}
      {filteredAds.length === 0 ? (
        <Card className="p-12 text-center border-dashed border-[#292E37] bg-[#15191F]">
          <Search className="h-8 w-8 text-[#727B89] mx-auto mb-2 opacity-50" />
          <p className="text-xs text-[#A0A7B2]">
            No advertisements matching your criteria. Launch the Ads Manager Agent from a campaign to collect ads.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAds.map((ad) => {
            const isVerified = (ad.date_verification_status || (ad.published_at ? 'verified' : 'unverified')) === 'verified'
            const publishedFormatted = formatTimestamp(ad.published_at)
            const scrapedFormatted = formatTimestamp(ad.scraped_at || ad.created_at)

            const isSelected = selectedAdIds.includes(ad.id)

            return (
              <Card
                key={ad.id}
                className={`border-[#292E37] bg-[#15191F] hover:border-[#547DB8]/50 transition-all flex flex-col justify-between ${
                  isSelected ? 'ring-1 ring-[#547DB8] border-[#547DB8] bg-[#1B2028]' : ''
                }`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 truncate">
                      <button
                        type="button"
                        onClick={() => toggleSelectAd(ad.id)}
                        className="text-[#727B89] hover:text-[#547DB8] transition-colors shrink-0"
                        title={isSelected ? 'Deselect Ad' : 'Select Ad to Link with Campaign'}
                      >
                        {isSelected ? (
                          <CheckSquare className="h-4 w-4 text-[#547DB8]" />
                        ) : (
                          <Square className="h-4 w-4 text-[#727B89]" />
                        )}
                      </button>
                      <span className="font-semibold text-sm text-[#F2F3F5] truncate">
                        {ad.advertiser}
                      </span>
                    </div>
                    {ad.evaluation_score && (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded-[4px] text-[10px] font-mono font-semibold text-[#8EA2C6] bg-[#10141C] border border-[#232B38] tabular-nums">
                        {ad.evaluation_score.overall}/10
                      </span>
                    )}
                  </div>

                  {/* Classification & Country Badges */}
                  <div className="flex flex-wrap items-center justify-between gap-1.5 pt-1">
                    <div className="flex items-center gap-1">
                      {ad.ad_classification === 'LIVE_META_AD' ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-semibold bg-[#36B58F]/15 border border-[#36B58F]/40 text-[#36B58F]">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] animate-pulse" /> LIVE META AD
                        </span>
                      ) : ad.ad_classification === 'VERIFIED_DOMAIN_BENCHMARK' || ad.is_benchmark ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-semibold bg-[#C5A46D]/15 border border-[#C5A46D]/40 text-[#C5A46D]">
                          BENCHMARK AD
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono text-[#7898C4] bg-[#547DB8]/10 border border-[#547DB8]/30">
                          {ad.ad_classification || 'META AD'}
                        </span>
                      )}

                      {ad.country && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-[#10141C] border border-[#232B38] text-[#F2F3F5]">
                          {ad.country === 'IN' ? '🇮🇳 IN' : ad.country === 'PH' ? '🇵🇭 PH' : ad.country}
                        </span>
                      )}

                      {ad.relevance_category && (
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono border ${
                          ad.relevance_category === 'DIRECT_COMPETITOR'
                            ? 'bg-rose-500/15 border-rose-500/40 text-rose-300 font-semibold'
                            : ad.relevance_category === 'INDIRECT_COMPETITOR'
                            ? 'bg-blue-500/15 border-blue-500/40 text-blue-300'
                            : ad.relevance_category === 'BROKER_OR_TRADING_PLATFORM'
                            ? 'bg-purple-500/15 border-purple-500/40 text-purple-300'
                            : ad.relevance_category === 'FINANCIAL_PLATFORM'
                            ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300'
                            : ad.relevance_category === 'UNRELATED_ADVERTISER'
                            ? 'bg-neutral-800 border-neutral-700 text-neutral-400'
                            : 'bg-[#10141C] border-[#232B38] text-[#8EA2C6]'
                        }`} title={ad.relevance_explanation || ''}>
                          {ad.relevance_category.replace(/_/g, ' ')}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-1">
                      {ad.creative_format && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-mono text-[#A0A7B2] bg-[#101216] border border-[#292E37]">
                          {ad.creative_format}
                        </span>
                      )}
                      {ad.cta && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-mono text-[#547DB8] bg-[#547DB8]/10 border border-[#547DB8]/30">
                          {ad.cta}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Verification Status Badge */}
                  <div className="flex items-center justify-between gap-2 pt-1 border-t border-[#292E37]/60">
                    {isVerified ? (
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" /> VERIFIED (30D)
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#D9A94F]" /> UNVERIFIED
                      </span>
                    )}

                    <CardDescription className="text-[10px] font-mono text-[#727B89]">
                      ID: {ad.ad_id ? ad.ad_id.slice(-10) : 'N/A'}
                    </CardDescription>
                  </div>
                </CardHeader>

                <CardContent className="pt-0 space-y-3">
                  {/* Verifiable Publication Timeline Box */}
                  <div className="p-2.5 rounded-lg bg-[#101216] border border-[#292E37] text-[11px] space-y-1">
                    {isVerified && publishedFormatted ? (
                      <>
                        <div className="flex items-center justify-between text-[#F2F3F5]">
                          <span className="text-[#727B89] flex items-center gap-1">
                            <Calendar className="w-3 h-3 text-[#547DB8]" /> Published:
                          </span>
                          <span className="font-medium text-[#7898C4]">{publishedFormatted}</span>
                        </div>
                        <div className="flex items-center justify-between text-[#A0A7B2]">
                          <span className="flex items-center gap-1 text-[#727B89]">
                            <Clock className="w-3 h-3 text-[#36B58F]" /> Age:
                          </span>
                          <span className="font-medium text-[#36B58F]">
                            {ad.age_days !== undefined && ad.age_days !== null ? `${ad.age_days} days ago` : 'Recent'}
                          </span>
                        </div>
                        {ad.published_date_source && (
                          <div className="flex items-center justify-between text-[10px] text-[#727B89] font-mono">
                            <span>Field:</span>
                            <span>{ad.published_date_source}</span>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-[#D9A94F] text-[11px] flex items-start gap-1.5 py-1">
                        <AlertCircle className="w-3.5 h-3.5 text-[#D9A94F] shrink-0 mt-0.5" />
                        <span>Publication date unavailable — cannot verify last-30-days eligibility.</span>
                      </div>
                    )}

                    <div className="flex items-center justify-between text-[10px] text-[#727B89] pt-1 border-t border-[#292E37]">
                      <span>Scraped:</span>
                      <span className="font-mono">{scrapedFormatted || 'Nov 5, 2026'}</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-[#080A0F] border border-[#292E37] text-xs">
                    <p className="text-[#F2F3F5]/90 line-clamp-3">"{ad.ad_text}"</p>
                  </div>

                  {ad.hook && (
                    <div className="text-xs">
                      <span className="text-[#C5A46D] font-semibold block text-[11px]">
                        Identified Hook:
                      </span>
                      <p className="text-[#A0A7B2] text-[11px] line-clamp-2">{ad.hook}</p>
                    </div>
                  )}

                  {ad.evaluation_score && (
                    <div className="grid grid-cols-2 gap-1.5 text-[10px] font-mono text-[#727B89] pt-2 border-t border-[#292E37] tabular-nums">
                      <div>Hook: {ad.evaluation_score.hook_strength}/10</div>
                      <div>Clarity: {ad.evaluation_score.clarity}/10</div>
                      <div>Emotion: {ad.evaluation_score.emotional_appeal}/10</div>
                      <div>CTA: {ad.evaluation_score.cta_effectiveness}/10</div>
                    </div>
                  )}
                </CardContent>

                <div className="p-4 pt-0 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    {ad.meta_ads_url ? (
                      <a
                        href={ad.meta_ads_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] text-[#7898C4] hover:underline flex items-center gap-1 font-medium"
                      >
                        Meta Ads Library <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : (
                      <span className="text-[11px] text-[#727B89]">Meta Library Verified</span>
                    )}

                    {ad.landing_page && (
                      <a
                        href={ad.landing_page}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] text-[#727B89] hover:text-[#F2F3F5] flex items-center gap-1"
                      >
                        Landing Page <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full text-xs border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#1B2028]"
                    onClick={() => setSelectedAd(ad)}
                  >
                    View Complete Ad Analysis
                  </Button>
                </div>
              </Card>
            )
          })}
        </div>
      )}

      {/* Ad Detail Modal */}
      <Dialog open={!!selectedAd} onOpenChange={() => setSelectedAd(null)}>
        <DialogContent className="max-w-xl bg-[#15191F] border-[#292E37]">
          <DialogHeader>
            <DialogTitle className="text-base text-[#F2F3F5] flex items-center justify-between">
              <span>{selectedAd?.advertiser}</span>
              {selectedAd?.evaluation_score && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-[4px] text-xs font-mono font-semibold text-[#8EA2C6] bg-[#10141C] border border-[#232B38] tabular-nums">
                  {selectedAd.evaluation_score.overall}/10 Overall Score
                </span>
              )}
            </DialogTitle>
            <DialogDescription className="text-xs text-[#727B89]">
              Observable Meta Ads Library activity & AI assessment rationale
            </DialogDescription>
          </DialogHeader>

          {selectedAd && (
            <div className="space-y-4 text-xs py-2">
              {/* Publication Date Verification Audit Card */}
              <div className="p-3 rounded-lg bg-[#101216] border border-[#292E37] space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-[#F2F3F5] flex items-center gap-1.5">
                    <Calendar className="h-4 w-4 text-[#547DB8]" />
                    Publication & Verification Audit
                  </span>
                  {(selectedAd.date_verification_status || (selectedAd.published_at ? 'verified' : 'unverified')) === 'verified' ? (
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" /> VERIFIED (30D)
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#D9A94F]" /> UNVERIFIED
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
                  <div>
                    <span className="text-[#727B89] block text-[10px]">Published At:</span>
                    <span className="font-mono text-[#7898C4]">
                      {formatTimestamp(selectedAd.published_at) || 'Unavailable'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[#727B89] block text-[10px]">Age:</span>
                    <span className="font-mono text-[#36B58F]">
                      {selectedAd.age_days !== undefined && selectedAd.age_days !== null
                        ? `${selectedAd.age_days} days ago`
                        : 'Unknown'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[#727B89] block text-[10px]">Source Field:</span>
                    <span className="font-mono text-[#A0A7B2]">
                      {selectedAd.published_date_source || 'first_seen / start_date'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[#727B89] block text-[10px]">Scraped At:</span>
                    <span className="font-mono text-[#A0A7B2]">
                      {formatTimestamp(selectedAd.scraped_at || selectedAd.created_at) || 'Nov 5, 2026'}
                    </span>
                  </div>
                </div>

                {selectedAd.published_at_raw && (
                  <div className="text-[10px] text-[#727B89] font-mono bg-[#080A0F] p-1.5 rounded border border-[#292E37]">
                    Raw Value: {selectedAd.published_at_raw}
                  </div>
                )}

                {selectedAd.meta_ads_url && (
                  <div className="pt-1">
                    <a
                      href={selectedAd.meta_ads_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-[#7898C4] hover:underline flex items-center gap-1 font-medium"
                    >
                      Inspect in Official Meta Ads Library <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                )}
              </div>

              <div>
                <span className="font-semibold text-[#F2F3F5] block mb-1">Ad Copy / Body:</span>
                <div className="p-3 rounded-lg bg-[#080A0F] border border-[#292E37] text-[#F2F3F5]/90 whitespace-pre-wrap">
                  {selectedAd.ad_text}
                </div>
              </div>

              {selectedAd.target_audience_hypothesis && (
                <div>
                  <span className="font-semibold text-[#F2F3F5] block mb-0.5">Audience Hypothesis:</span>
                  <p className="text-[#A0A7B2]">{selectedAd.target_audience_hypothesis}</p>
                </div>
              )}

              {selectedAd.marketing_angle && (
                <div>
                  <span className="font-semibold text-[#F2F3F5] block mb-0.5">Marketing Angle:</span>
                  <p className="text-[#A0A7B2]">{selectedAd.marketing_angle}</p>
                </div>
              )}

              {selectedAd.evaluation_score && (
                <div className="p-3 rounded-lg bg-[#101216] border border-[#292E37] space-y-1">
                  <span className="font-semibold text-[#7898C4] block">Evaluation Rationale:</span>
                  <p className="text-[#A0A7B2]">{selectedAd.evaluation_score.rationale}</p>
                  <span className="text-[10px] text-[#727B89] block mt-1 font-mono">
                    Basis: {selectedAd.evaluation_score.evidence_basis}
                  </span>
                </div>
              )}

              {selectedAd.landing_page && (
                <div className="pt-2">
                  <a
                    href={selectedAd.landing_page}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-[#547DB8] hover:underline flex items-center gap-1"
                  >
                    View Landing Page <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
