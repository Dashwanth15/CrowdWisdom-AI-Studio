import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Plus,
  Megaphone,
  Copy,
  Trash2,
  ExternalLink,
  ArrowRight,
  Search,
  LayoutList,
  LayoutGrid,
  TrendingUp,
  Clock,
  Sparkles,
  Layers,
  Film,
  FileText,
} from 'lucide-react'
import { campaignsApi } from '@/lib/api'
import { Campaign, CampaignStatus, VideoAspectRatio } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { getStatusColor, formatRelativeTime } from '@/lib/utils'
import toast from 'react-hot-toast'

export const CampaignsPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table')
  const [isLoading, setIsLoading] = useState(true)

  // Create Campaign Modal State
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [name, setName] = useState('')
  const [targetCountry, setTargetCountry] = useState<'IN' | 'PH' | 'BOTH'>('IN')
  const [description, setDescription] = useState('')
  const [objective, setObjective] = useState('brand_awareness')
  const [duration, setDuration] = useState(45)
  const [aspectRatio, setAspectRatio] = useState<VideoAspectRatio>('9:16')
  const [creativeDirection, setCreativeDirection] = useState('Cinematic financial thriller with visual sentiment clarity')
  const [instructions, setInstructions] = useState('')

  // Delete Dialog State
  const [deleteId, setDeleteId] = useState<string | null>(null)

  useEffect(() => {
    loadCampaigns()
  }, [])

  const loadCampaigns = async () => {
    setIsLoading(true)
    try {
      const res = await campaignsApi.list()
      setCampaigns(res.data)
    } catch (err) {
      toast.error('Failed to load campaigns')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const defaultSegments =
        targetCountry === 'PH'
          ? ['pse_equities_trader', 'ofw_investor', 'young_pro_wealth']
          : ['retail_traders', 'options_traders', 'swing_traders']
      const defaultInterests =
        targetCountry === 'PH'
          ? ['PSE', 'PSEi', 'dividends', 'financial freedom', 'crypto crossover']
          : ['trading', 'investing', 'market sentiment', 'Nifty 50', 'options']

      const payload = {
        name,
        description,
        objective,
        target_country: targetCountry,
        video_duration_seconds: Number(duration),
        video_aspect_ratio: aspectRatio,
        creative_direction: creativeDirection,
        additional_instructions: instructions,
        audience: {
          target_country: targetCountry,
          segments: defaultSegments,
          interests: defaultInterests,
        },
        research_approaches: ['pain_point', 'unique_data', 'product_value'],
      }
      await campaignsApi.create(payload)
      toast.success(
        targetCountry === 'BOTH'
          ? 'Dual-market campaigns (India 🇮🇳 & Philippines 🇵🇭) generated successfully!'
          : 'Campaign created successfully!'
      )
      setIsCreateOpen(false)
      setName('')
      setDescription('')
      loadCampaigns()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to create campaign')
    }
  }

  const handleDuplicate = async (id: string) => {
    try {
      await campaignsApi.duplicate(id)
      toast.success('Campaign duplicated!')
      loadCampaigns()
    } catch (err) {
      toast.error('Failed to duplicate campaign')
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await campaignsApi.delete(deleteId)
      toast.success('Campaign deleted')
      setDeleteId(null)
      loadCampaigns()
    } catch (err) {
      toast.error('Failed to delete campaign')
    }
  }

  const filteredCampaigns = campaigns.filter((c) => {
    const matchesStatus = filterStatus === 'all' || c.status === filterStatus
    const matchesSearch =
      searchQuery === '' ||
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase()))
    return matchesStatus && matchesSearch
  })

  const renderCountryBadge = (country?: string) => {
    if (country === 'PH') {
      return (
        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-cyan-950/60 text-cyan-300 border border-cyan-700/50">
          <span>🇵🇭</span> PH
        </span>
      )
    }
    if (country === 'BOTH') {
      return (
        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-purple-950/60 text-purple-300 border border-purple-700/50">
          <span>🌐</span> IN+PH
        </span>
      )
    }
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-amber-950/60 text-amber-300 border border-amber-700/50">
        <span>🇮🇳</span> IN
      </span>
    )
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#292E37]">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-semibold tracking-tight text-[#F2F3F5]">
              Campaign Management
            </h2>
            <span className="text-xs font-mono text-[#727B89]">
              ({campaigns.length} campaigns)
            </span>
          </div>
          <p className="text-xs text-[#727B89] mt-1">
            Institutional portfolio of autonomous multi-agent advertising campaigns for CrowdWisdomTrading.
          </p>
        </div>

        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button variant="brand" size="sm" className="font-medium bg-[#547DB8] hover:bg-[#436494] text-white shadow-sm">
              <Plus className="h-4 w-4 mr-1.5" />
              New Campaign
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg bg-[#15191F] border-[#292E37]">
            <form onSubmit={handleCreateCampaign}>
              <DialogHeader>
                <DialogTitle>Configure Marketing Campaign</DialogTitle>
                <DialogDescription className="text-xs text-[#727B89]">
                  Define target market audience, video format specifications, and creative direction.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-4 text-xs">
                <div className="space-y-1.5">
                  <Label htmlFor="camp-name">Campaign Title</Label>
                  <Input
                    id="camp-name"
                    placeholder="e.g. Options Volatility Master — Q4 Push"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="camp-desc">Executive Objective & Goal</Label>
                  <Textarea
                    id="camp-desc"
                    placeholder="Demonstrate CrowdWisdom options consensus clarity to retail traders experiencing market noise."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={2}
                  />
                </div>

                {/* Country-Specific Market Intelligence Target */}
                <div className="space-y-1.5">
                  <Label className="flex items-center justify-between">
                    <span>Target Financial Market</span>
                    <span className="text-[10px] text-[#8C9BB3] font-mono">SEBI & SEC Compliant</span>
                  </Label>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setTargetCountry('IN')}
                      className={`flex flex-col items-center justify-center p-2.5 rounded-lg border text-xs transition-all ${
                        targetCountry === 'IN'
                          ? 'border-[#3B82F6] bg-[#1E293B] text-white shadow-sm ring-1 ring-[#3B82F6]'
                          : 'border-[#222E42] bg-[#101622] text-[#94A3B8] hover:border-[#334155]'
                      }`}
                    >
                      <span className="text-base mb-0.5">🇮🇳</span>
                      <span className="font-semibold text-[11px]">India</span>
                      <span className="text-[9px] text-[#64748B] font-mono">NSE / Nifty 50</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setTargetCountry('PH')}
                      className={`flex flex-col items-center justify-center p-2.5 rounded-lg border text-xs transition-all ${
                        targetCountry === 'PH'
                          ? 'border-[#06B6D4] bg-[#0E2A38] text-white shadow-sm ring-1 ring-[#06B6D4]'
                          : 'border-[#222E42] bg-[#101622] text-[#94A3B8] hover:border-[#334155]'
                      }`}
                    >
                      <span className="text-base mb-0.5">🇵🇭</span>
                      <span className="font-semibold text-[11px]">Philippines</span>
                      <span className="text-[9px] text-[#64748B] font-mono">PSE / PSEi</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setTargetCountry('BOTH')}
                      className={`flex flex-col items-center justify-center p-2.5 rounded-lg border text-xs transition-all ${
                        targetCountry === 'BOTH'
                          ? 'border-[#A855F7] bg-[#2E1A47] text-white shadow-sm ring-1 ring-[#A855F7]'
                          : 'border-[#222E42] bg-[#101622] text-[#94A3B8] hover:border-[#334155]'
                      }`}
                    >
                      <span className="text-base mb-0.5">🌐</span>
                      <span className="font-semibold text-[11px]">Both Markets</span>
                      <span className="text-[9px] text-[#64748B] font-mono">Dual Variants</span>
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <Label>Marketing Objective</Label>
                    <Select value={objective} onValueChange={setObjective}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="brand_awareness">Brand Awareness</SelectItem>
                        <SelectItem value="product_education">Sentiment Education</SelectItem>
                        <SelectItem value="customer_acquisition">Direct Acquisition</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-1.5">
                    <Label>Video Aspect Ratio</Label>
                    <Select
                      value={aspectRatio}
                      onValueChange={(v) => setAspectRatio(v as VideoAspectRatio)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="9:16">9:16 (Vertical Mobile / TikTok / Reels)</SelectItem>
                        <SelectItem value="16:9">16:9 (Landscape YouTube)</SelectItem>
                        <SelectItem value="1:1">1:1 (Square Feed)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <div className="flex justify-between items-center">
                    <Label>Target Duration</Label>
                    <span className="text-[11px] font-mono text-[#547DB8] font-semibold">{duration} seconds</span>
                  </div>
                  <input
                    type="range"
                    min="30"
                    max="60"
                    step="5"
                    className="w-full accent-[#547DB8]"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                  />
                  <div className="flex justify-between text-[10px] text-[#727B89] font-mono">
                    <span>30s (Hook)</span>
                    <span>45s (Standard Commercial)</span>
                    <span>60s (Cinematic In-Depth)</span>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <Label>Cinematic Direction</Label>
                  <Input
                    value={creativeDirection}
                    onChange={(e) => setCreativeDirection(e.target.value)}
                    placeholder="Cinematic financial thriller, moody lighting, crisp audio voiceover"
                  />
                </div>
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsCreateOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="brand">
                  Initialize Campaign
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Control Bar: Search, Filters & View Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-xl bg-[#0D111A] border border-[#1E2638] shadow-md">
        <div className="flex items-center gap-2 flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-[#64748B]" />
            <Input
              placeholder="Search campaigns by name, thesis, or audience..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 bg-[#131A26] border-[#222E42] text-xs h-9 text-[#F1F5F9] placeholder:text-[#64748B] focus:border-[#3B82F6] rounded-lg"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Status Filter Pills */}
          <div className="flex items-center gap-1 bg-[#131A26] border border-[#222E42] p-1 rounded-lg">
            {['all', 'active', 'draft', 'completed', 'paused'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-3 py-1 text-[11px] font-mono uppercase tracking-wider rounded-[5px] transition-all ${
                  filterStatus === status
                    ? 'bg-[#1E293B] text-[#FFFFFF] border border-[#3B82F6] shadow-sm font-semibold'
                    : 'text-[#8E9BB3] hover:text-[#F1F5F9] hover:bg-[#1A2332]'
                }`}
              >
                {status}
              </button>
            ))}
          </div>

          <div className="h-4 w-[1px] bg-[#222E42] mx-1" />

          {/* View Mode Toggle */}
          <div className="flex items-center bg-[#131A26] border border-[#222E42] p-1 rounded-lg">
            <button
              onClick={() => setViewMode('table')}
              title="Enterprise Table View"
              className={`p-1.5 rounded-[5px] transition-colors ${
                viewMode === 'table' ? 'bg-[#1E293B] text-[#60A5FA]' : 'text-[#8E9BB3] hover:text-[#F1F5F9]'
              }`}
            >
              <LayoutList className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              title="Card Grid View"
              className={`p-1.5 rounded-[5px] transition-colors ${
                viewMode === 'grid' ? 'bg-[#1E293B] text-[#60A5FA]' : 'text-[#8E9BB3] hover:text-[#F1F5F9]'
              }`}
            >
              <LayoutGrid className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Campaign Portfolio Content */}
      {filteredCampaigns.length === 0 ? (
        <Card className="p-12 text-center border-dashed border-[#292E37] bg-[#15191F]/50">
          <Megaphone className="h-8 w-8 text-[#727B89] mx-auto mb-3 opacity-60" />
          <h3 className="text-sm font-semibold text-[#F2F3F5]">No matching campaigns found</h3>
          <p className="text-xs text-[#727B89] mt-1 max-w-sm mx-auto">
            {searchQuery ? 'Try adjusting your search query or filter settings.' : 'Initialize a new campaign to begin autonomous marketing execution.'}
          </p>
          <Button
            variant="brand"
            size="sm"
            className="mt-4 text-xs font-medium bg-[#547DB8] hover:bg-[#436494] text-white"
            onClick={() => setIsCreateOpen(true)}
          >
            <Plus className="h-3.5 w-3.5 mr-1.5" />
            Create Campaign
          </Button>
        </Card>
      ) : viewMode === 'table' ? (
        /* --- Enterprise Table View (Institutional Standard) --- */
        <Card className="border-[#1E2638] bg-[#0D111A] rounded-xl shadow-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#131A26] border-b border-[#1E2638] text-[11px] font-mono text-[#8C9BB3] uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4 font-semibold">Campaign Name & Objective</th>
                  <th className="py-3.5 px-3 font-semibold">Status</th>
                  <th className="py-3.5 px-3 font-semibold">Specs</th>
                  <th className="py-3.5 px-3 font-semibold">Target Audience</th>
                  <th className="py-3.5 px-3 text-center font-semibold">Research</th>
                  <th className="py-3.5 px-3 text-center font-semibold">Scripts</th>
                  <th className="py-3.5 px-3 text-center font-semibold">Commercials</th>
                  <th className="py-3.5 px-3 font-semibold">Created</th>
                  <th className="py-3.5 px-4 text-right font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#171E2B]">
                {filteredCampaigns.map((camp) => (
                  <tr
                    key={camp.id}
                    className="hover:bg-[#151D2A] transition-all duration-150 group"
                  >
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        {renderCountryBadge(camp.target_country || camp.audience?.target_country)}
                        <Link
                          to={`/campaigns/${camp.id}`}
                          className="font-semibold text-[13px] text-[#FFFFFF] group-hover:text-[#60A5FA] transition-colors flex items-center gap-1.5"
                        >
                          <span className="line-clamp-1">{camp.name}</span>
                          <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity text-[#60A5FA]" />
                        </Link>
                      </div>
                      <p className="text-[11px] text-[#94A3B8] line-clamp-1 mt-0.5 capitalize">
                        {camp.objective.replace('_', ' ')} • {camp.description || 'Autonomous marketing campaign'}
                      </p>
                    </td>

                    <td className="py-3.5 px-3">
                      <Badge className={getStatusColor(camp.status)}>
                        {camp.status}
                      </Badge>
                    </td>

                    <td className="py-3.5 px-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-[4px] bg-[#141A26] border border-[#222E42] font-mono text-[11px] text-[#CBD5E1] whitespace-nowrap">
                        {camp.video_aspect_ratio} • {camp.video_duration_seconds}s
                      </span>
                    </td>

                    <td className="py-3.5 px-3">
                      <div className="flex flex-col gap-1 items-start">
                        {camp.audience?.segments && camp.audience.segments.length > 0 ? (
                          camp.audience.segments.slice(0, 2).map((seg) => (
                            <span
                              key={seg}
                              className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[11px] font-mono font-medium bg-[#141F32] text-[#93C5FD] border border-[#243754] shadow-xs whitespace-nowrap"
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8]" />
                              {seg.replace('_', ' ')}
                            </span>
                          ))
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[11px] font-mono font-medium bg-[#141F32] text-[#93C5FD] border border-[#243754] whitespace-nowrap">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8]" />
                            Options Traders
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="py-3.5 px-3 text-center font-mono text-xs font-semibold text-[#F8FAFC] tabular-nums">
                      {camp.ads_researched}
                    </td>

                    <td className="py-3.5 px-3 text-center font-mono text-xs font-semibold text-[#93C5FD] tabular-nums">
                      {camp.scripts_generated}
                    </td>

                    <td className="py-3.5 px-3 text-center font-mono text-xs font-bold text-[#34D399] tabular-nums">
                      {camp.videos_generated}
                    </td>

                    <td className="py-3.5 px-3 font-mono text-[11px] text-[#94A3B8] whitespace-nowrap">
                      {formatRelativeTime(camp.created_at)}
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link to={`/campaigns/${camp.id}`} className="shrink-0">
                          <Button
                            size="sm"
                            className="h-8 px-3.5 text-xs font-semibold bg-[#2563EB] hover:bg-[#1D4ED8] text-white shadow-md shadow-blue-600/30 border border-blue-400/30 flex items-center gap-1.5 rounded-[6px] transition-all hover:scale-[1.02] active:scale-[0.98]"
                          >
                            <span>Open Hub</span>
                            <ArrowRight className="h-3.5 w-3.5 text-blue-100" />
                          </Button>
                        </Link>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-[#94A3B8] hover:text-[#FFFFFF] hover:bg-[#1A2332] rounded-[6px] transition-colors"
                          onClick={() => handleDuplicate(camp.id)}
                          title="Duplicate Campaign"
                        >
                          <Copy className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-[#94A3B8] hover:text-[#F87171] hover:bg-[#2A1517] rounded-[6px] transition-colors"
                          onClick={() => setDeleteId(camp.id)}
                          title="Delete Campaign"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        /* --- Card Grid View --- */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCampaigns.map((camp) => (
            <Card
              key={camp.id}
              className="border-[#1E2638] bg-[#0D111A] hover:border-[#3B82F6]/50 shadow-xl transition-all flex flex-col justify-between"
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    <Badge className={getStatusColor(camp.status)}>
                      {camp.status}
                    </Badge>
                    {renderCountryBadge(camp.target_country || camp.audience?.target_country)}
                  </div>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-[4px] bg-[#141A26] border border-[#222E42] font-mono text-[11px] text-[#CBD5E1]">
                    {camp.video_aspect_ratio} • {camp.video_duration_seconds}s
                  </span>
                </div>
                <CardTitle className="text-sm font-semibold mt-2 line-clamp-1 text-[#FFFFFF]">
                  {camp.name}
                </CardTitle>
                <CardDescription className="text-xs line-clamp-2 text-[#94A3B8]">
                  {camp.description || 'Autonomous marketing campaign for CrowdWisdomTrading.'}
                </CardDescription>

                {/* Target Audience Tags */}
                <div className="flex flex-wrap gap-1 mt-2">
                  {camp.audience?.segments && camp.audience.segments.length > 0 ? (
                    camp.audience.segments.map((seg) => (
                      <span
                        key={seg}
                        className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono font-medium bg-[#141F32] text-[#93C5FD] border border-[#243754]"
                      >
                        <span className="w-1 h-1 rounded-full bg-[#38BDF8]" />
                        {seg.replace('_', ' ')}
                      </span>
                    ))
                  ) : (
                    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono font-medium bg-[#141F32] text-[#93C5FD] border border-[#243754]">
                      <span className="w-1 h-1 rounded-full bg-[#38BDF8]" />
                      Options Traders
                    </span>
                  )}
                </div>
              </CardHeader>

              <CardContent className="pt-0">
                <div className="grid grid-cols-3 gap-2 p-2.5 rounded-lg bg-[#131A26] border border-[#20293A] text-center text-[11px] mb-3">
                  <div>
                    <span className="text-[#8E9BB3] block text-[10px] font-mono">Ads Scraped</span>
                    <span className="font-semibold text-[#F8FAFC] tabular-nums text-xs">{camp.ads_researched}</span>
                  </div>
                  <div>
                    <span className="text-[#8E9BB3] block text-[10px] font-mono">Scripts</span>
                    <span className="font-semibold text-[#93C5FD] tabular-nums text-xs">{camp.scripts_generated}</span>
                  </div>
                  <div>
                    <span className="text-[#8E9BB3] block text-[10px] font-mono">Videos</span>
                    <span className="font-bold text-[#34D399] tabular-nums text-xs">{camp.videos_generated}</span>
                  </div>
                </div>

                <div className="text-[11px] text-[#94A3B8] font-mono flex items-center justify-between">
                  <span>{formatRelativeTime(camp.created_at)}</span>
                  <span className="capitalize">{camp.objective.replace('_', ' ')}</span>
                </div>
              </CardContent>

              <CardFooter className="pt-0 border-t border-[#1E2638] flex items-center justify-between py-2.5">
                <Link to={`/campaigns/${camp.id}`} className="flex-1 mr-2">
                  <Button
                    size="sm"
                    className="w-full h-8 text-xs font-semibold bg-[#2563EB] hover:bg-[#1D4ED8] text-white shadow-md shadow-blue-600/30 border border-blue-400/30 flex items-center justify-center gap-1.5 rounded-[6px]"
                  >
                    <span>Open Hub</span>
                    <ArrowRight className="h-3.5 w-3.5 text-blue-100" />
                  </Button>
                </Link>

                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-[#94A3B8] hover:text-[#FFFFFF] hover:bg-[#1A2332] rounded-[6px]"
                    onClick={() => handleDuplicate(camp.id)}
                    title="Duplicate Campaign"
                  >
                    <Copy className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-[#94A3B8] hover:text-[#F87171] hover:bg-[#2A1517] rounded-[6px]"
                    onClick={() => setDeleteId(camp.id)}
                    title="Delete Campaign"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Alert */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Campaign Confirmation</AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              This action will permanently delete this campaign and all associated research,
              storyboards, and video records from MongoDB. This cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete}>
              Confirm Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
