import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Search,
  FileVideo,
  Clapperboard,
  CheckCircle2,
  AlertTriangle,
  Play,
  Download,
  Share2,
  Sparkles,
  Bot,
  Layers,
  ShieldCheck,
  Check,
  X,
  ExternalLink,
  RefreshCw,
  FolderOpen,
  Film,
  FileText,
  Lightbulb,
  Clock,
  Eye,
  Trash2,
  FolderPlus,
  Calendar,
} from 'lucide-react'
import {
  campaignsApi,
  agentsApi,
  scriptsApi,
  videosApi,
  researchApi,
  creativeBriefsApi,
  assetsApi,
} from '@/lib/api'
import {
  Campaign,
  Script,
  VideoJob,
  Advertisement,
  MarketingInsight,
  CreativeBrief,
  MediaAsset,
} from '@/types'
import { wsManager } from '@/lib/websocket'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { getStatusColor, formatRelativeTime, formatFileSize, resolveMediaUrl } from '@/lib/utils'
import { CrowdWisdomLogo } from '@/components/branding'
import toast from 'react-hot-toast'

export const CampaignDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [scripts, setScripts] = useState<Script[]>([])
  const [videos, setVideos] = useState<VideoJob[]>([])
  const [ads, setAds] = useState<Advertisement[]>([])
  const [insights, setInsights] = useState<MarketingInsight[]>([])
  const [brief, setBrief] = useState<CreativeBrief | null>(null)
  const [assets, setAssets] = useState<MediaAsset[]>([])

  const [isLoading, setIsLoading] = useState(true)
  const [campaignError, setCampaignError] = useState<string | null>(null)
  const [isApprovingScriptId, setIsApprovingScriptId] = useState<string | null>(null)
  const [isApprovingBrief, setIsApprovingBrief] = useState(false)
  const [isDispatchingVideoId, setIsDispatchingVideoId] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<string>('scripts')

  // Deduplicate scripts by approach: show only the single active/approved script per approach
  // Prioritizes approved scripts first, then latest generated scripts to prevent duplicate pending approvals
  const displayScripts = React.useMemo(() => {
    const approachGroups: Record<string, Script[]> = {}
    for (const s of scripts) {
      const app = s.approach || 'pain_point'
      if (!approachGroups[app]) approachGroups[app] = []
      approachGroups[app].push(s)
    }

    const activeList: Script[] = []
    for (const app of Object.keys(approachGroups)) {
      const group = approachGroups[app]
      const approved = group.find((s) => s.status === 'approved')
      if (approved) {
        activeList.push(approved)
      } else {
        const sorted = [...group].sort(
          (a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
        )
        if (sorted[0]) activeList.push(sorted[0])
      }
    }
    return activeList
  }, [scripts])

  useEffect(() => {
    if (id) {
      loadCampaignDetails()
    }
  }, [id])

  useEffect(() => {
    // Subscribe to WebSocket updates for real-time progress & completed tasks
    const unsubProgress = wsManager.on('job_progress', (data: any) => {
      if (data.campaign_id === id) {
        // Update in-memory state smoothly without hammering the server with 7 API calls per frame
        if (data.progress_percent !== undefined) {
          setVideos((prev) => {
            const hasMatch = prev.some(
              (v) => v.id === data.job_id || v.id === data.video_job_id || (data.script_id && v.script_id === data.script_id)
            )
            if (hasMatch) {
              return prev.map((v) =>
                v.id === data.job_id || v.id === data.video_job_id || (data.script_id && v.script_id === data.script_id)
                  ? {
                    ...v,
                    progress_percent: data.progress_percent,
                    current_stage: data.current_stage || v.current_stage,
                    status: (data.status === 'completed' ? 'completed' : data.status === 'failed' ? 'failed' : v.status) as any,
                  }
                  : v
              )
            }
            return prev
          })
        }
        // Only perform full sub-resource reload when task finishes or fails
        if (data.status === 'completed' || data.status === 'failed') {
          loadCampaignDetails(false)
          if (data.status === 'completed') {
            toast.success('🎬 Cinematic video rendered successfully! Opening Rendered Videos tab.', {
              duration: 5000,
            })
            setActiveTab('videos')
          }
        }
      }
    })

    const unsubNotification = wsManager.on('notification', (notif: any) => {
      loadCampaignDetails(false)
      if (notif?.title?.toLowerCase().includes('video') && notif?.title?.toLowerCase().includes('finished')) {
        setActiveTab('videos')
      }
    })

    const unsubStatus = wsManager.on('agent_status', (data: any) => {
      if (data?.status === 'completed' || data?.status === 'failed') {
        loadCampaignDetails(false)
        if (data?.agent_type === 'video_production' && data?.status === 'completed') {
          setActiveTab('videos')
        }
      }
    })

    return () => {
      unsubProgress()
      unsubNotification()
      unsubStatus()
    }
  }, [id])

  // Active polling fallback whenever any script or video is actively generating/rendering
  useEffect(() => {
    const hasActiveTask =
      scripts.some((s) => s.status === 'generating' || s.status === 'in_production') ||
      videos.some((v) => ['queued', 'processing', 'rendering', 'composing'].includes(v.status))

    if (!hasActiveTask || !id) return

    const timer = setInterval(() => {
      loadCampaignDetails(false)
    }, 4000)

    return () => clearInterval(timer)
  }, [scripts, videos, id])

  const loadCampaignDetails = async (showLoading = true) => {
    if (!id) return
    if (showLoading) setIsLoading(true)

    // 1. Mandatory Campaign Fetch
    try {
      const campRes = await campaignsApi.get(id)
      setCampaign(campRes.data)
      setCampaignError(null)
    } catch (err: any) {
      // Only show full-screen error on initial load when no campaign is present
      if (showLoading) {
        const msg = err.response?.data?.detail || 'Campaign not found or failed to load.'
        setCampaignError(msg)
        setIsLoading(false)
      }
      return
    }

    // 2. Resilient Sub-resource Fetching (Promise.allSettled)
    // Sub-resource absence is an empty state, not a fatal campaign failure!
    try {
      const [scriptsRes, vidsRes, adsRes, insightsRes, briefRes, assetsRes] =
        await Promise.allSettled([
          scriptsApi.list({ campaign_id: id }),
          videosApi.list({ campaign_id: id }),
          researchApi.listAds({ campaign_id: id }),
          researchApi.listInsights({ campaign_id: id }),
          creativeBriefsApi.getByCampaign(id),
          assetsApi.list({ campaign_id: id }),
        ])

      if (scriptsRes.status === 'fulfilled') setScripts(scriptsRes.value.data || [])
      if (vidsRes.status === 'fulfilled') setVideos(vidsRes.value.data || [])
      if (adsRes.status === 'fulfilled') setAds(adsRes.value.data || [])
      if (insightsRes.status === 'fulfilled') setInsights(insightsRes.value.data || [])
      if (briefRes.status === 'fulfilled') setBrief(briefRes.value.data || null)
      if (assetsRes.status === 'fulfilled') setAssets(assetsRes.value.data || [])
    } catch (e) {
      console.warn('Sub-resource fetch error:', e)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLaunchResearch = async () => {
    if (!id) return
    try {
      await agentsApi.launchResearch({
        campaign_id: id,
        keywords: ['trading market sentiment', 'options trading tools', 'retail investor signals'],
        date_range_days: 30,
      })
      toast.success('Ads Manager Agent launched! Crawling Meta Ads Library...')
      loadCampaignDetails(false)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to start research')
    }
  }

  const handleGenerateScript = async (approach: string) => {
    if (!id) return
    try {
      await agentsApi.generateScript({
        campaign_id: id,
        approach,
      })
      toast.success(`Script Agent dispatched for ${approach.replace('_', ' ')} approach!`)
      loadCampaignDetails(false)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to generate script')
    }
  }

  const handleApproveScript = async (script: Script) => {
    // 1. Strict Frontend Validation Gate
    if (script.status === 'generating') {
      toast.error('Cannot approve: Script is still actively generating. Please wait.')
      return
    }
    if (!script.scenes || script.scenes.length === 0) {
      toast.error('Validation Error: Storyboard contains zero scenes. Incomplete scripts cannot be approved.')
      return
    }
    if (!script.core_message || !script.core_message.trim()) {
      toast.error('Validation Error: Script is missing its Core Message. Incomplete scripts cannot be approved.')
      return
    }

    setIsApprovingScriptId(script.id)
    try {
      await scriptsApi.approve(script.id)
      toast.success('Script approved! Human checkpoint passed. Ready for Video Agent.')
      await loadCampaignDetails(false)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Validation Error: Approval rejected by server.')
    } finally {
      setIsApprovingScriptId(null)
    }
  }

  const handleApproveBrief = async () => {
    if (!brief) return
    setIsApprovingBrief(true)
    try {
      await creativeBriefsApi.approve(brief.id)
      toast.success('Creative Brief approved! Checkpoint 1 Sign-off passed.')
      await loadCampaignDetails(false)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to approve creative brief.')
    } finally {
      setIsApprovingBrief(false)
    }
  }

  const handleSynthesizeBrief = async () => {
    if (!id) return
    try {
      await creativeBriefsApi.generate(id)
      toast.success('Creative Intelligence Engine dispatched to synthesize brief!')
      await loadCampaignDetails(false)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to synthesize brief.')
    }
  }

  const handleRenderVideo = async (scriptId: string) => {
    if (!id || isDispatchingVideoId) return
    setIsDispatchingVideoId(scriptId)
    try {
      const res = await videosApi.generate({
        campaign_id: id,
        script_id: scriptId,
        aspect_ratio: campaign?.video_aspect_ratio || '9:16',
        duration_seconds: campaign?.video_duration_seconds || 45,
        quality: 'high',
      })
      toast.success('Video Production Agent initiated rendering!')
      if (res.data?.video_job_id) {
        setVideos((prev) => [
          {
            id: res.data.video_job_id,
            campaign_id: id,
            script_id: scriptId,
            status: 'processing' as any,
            aspect_ratio: campaign?.video_aspect_ratio || '9:16',
            duration_seconds: campaign?.video_duration_seconds || 45,
            quality: 'high',
            progress_percent: 5,
            current_stage: 'initializing_engine',
            created_at: new Date().toISOString(),
          },
          ...prev.filter((v) => v.id !== res.data.video_job_id),
        ])
      }
      await loadCampaignDetails(false)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to start video rendering')
    } finally {
      setIsDispatchingVideoId(null)
    }
  }

  const handleDeleteVideo = async (videoId: string) => {
    try {
      await videosApi.delete(videoId)
      toast.success('Video and associated media files deleted.')
      await loadCampaignDetails(false)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete video.')
    }
  }

  const handleDeleteScript = async (scriptId: string) => {
    try {
      await scriptsApi.delete(scriptId)
      toast.success('Script storyboard deleted.')
      await loadCampaignDetails(false)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete script.')
    }
  }

  // --- Render Loading Skeleton ---
  if (isLoading && !campaign) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto p-4 animate-pulse">
        <div className="h-4 w-40 bg-muted/40 rounded"></div>
        <div className="h-32 bg-card/60 rounded-xl border border-border/40 p-6 flex flex-col justify-between">
          <div className="h-6 w-72 bg-muted/50 rounded"></div>
          <div className="h-4 w-full max-w-xl bg-muted/30 rounded mt-2"></div>
        </div>
        <div className="h-10 w-96 bg-card/60 rounded border border-border/40"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="h-64 bg-card/40 rounded-xl border border-border/30"></div>
          <div className="h-64 bg-card/40 rounded-xl border border-border/30"></div>
        </div>
      </div>
    )
  }

  // --- Render Error State ---
  if (campaignError || !campaign) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-8 border border-destructive/40 bg-destructive/10 rounded-xl text-center space-y-4">
        <AlertTriangle className="h-10 w-10 text-destructive mx-auto" />
        <h2 className="text-lg font-semibold text-foreground">Campaign Hub Error</h2>
        <p className="text-xs text-muted-foreground">{campaignError || 'Failed to locate the requested campaign.'}</p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <Link to="/campaigns">
            <Button variant="outline" size="sm" className="text-xs">
              <ArrowLeft className="h-3.5 w-3.5 mr-1.5" /> Back to Campaigns
            </Button>
          </Link>
          <Button size="sm" onClick={() => loadCampaignDetails(true)} className="text-xs">
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" /> Retry Loading
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Breadcrumb & Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Link to="/campaigns" className="hover:text-foreground flex items-center gap-1">
            <ArrowLeft className="h-3.5 w-3.5" /> Back to Campaigns
          </Link>
          <span>/</span>
          <span className="text-foreground font-medium">{campaign.name}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => loadCampaignDetails(false)}
          className="text-xs h-8 text-muted-foreground hover:text-foreground"
        >
          <RefreshCw className="h-3 w-3 mr-1.5" /> Refresh
        </Button>
      </div>

      {/* Campaign Header Banner */}
      <div className="p-6 rounded-xl border border-border/70 bg-card/60 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <CrowdWisdomLogo variant="badge" size="sm" className="hidden sm:inline-flex mt-1 flex-shrink-0 shadow-sm" />
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge className={getStatusColor(campaign.status)}>{campaign.status}</Badge>
              <span className="text-xs font-mono text-muted-foreground">
                {campaign.video_aspect_ratio} • {campaign.video_duration_seconds}s target
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">{campaign.name}</h1>
            <p className="text-xs text-muted-foreground mt-1 max-w-2xl leading-relaxed">
              {campaign.description || 'Autonomous multi-agent marketing campaign for CrowdWisdomTrading.'}
            </p>
          </div>
        </div>

        {/* Quick Launch Actions */}
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleLaunchResearch} className="text-xs">
            <Search className="h-3.5 w-3.5 mr-1.5" />
            Launch Ads Research
          </Button>

          <Button
            variant="brand"
            size="sm"
            onClick={() => handleGenerateScript('pain_point')}
            className="text-xs"
          >
            <FileVideo className="h-3.5 w-3.5 mr-1.5" />
            Generate Script
          </Button>
        </div>
      </div>

      {/* Main Campaign Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="bg-card/70 border border-border/60">
          <TabsTrigger value="scripts" className="text-xs">
            Scripts & Storyboards ({displayScripts.length})
          </TabsTrigger>
          <TabsTrigger value="brief" className="text-xs">
            Creative Brief {brief ? '(1)' : '(0)'}
          </TabsTrigger>
          <TabsTrigger value="videos" className="text-xs">
            Rendered Videos ({videos.length})
          </TabsTrigger>
          <TabsTrigger value="research" className="text-xs">
            Ad Intelligence ({ads.length})
          </TabsTrigger>
          <TabsTrigger value="insights" className="text-xs">
            Marketing Insights ({insights.length})
          </TabsTrigger>
          <TabsTrigger value="assets" className="text-xs">
            Media Assets ({assets.length})
          </TabsTrigger>
          <TabsTrigger value="config" className="text-xs">
            Audience & Parameters
          </TabsTrigger>
        </TabsList>

        {/* --- 1. Scripts & Storyboards Tab (Checkpoint 2) --- */}
        <TabsContent value="scripts" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-xs text-muted-foreground">
              <span className="font-semibold text-foreground">Checkpoint 2:</span> Human approval is required on scripts before dispatching to the Video Production Agent.
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                className="text-xs h-8"
                onClick={() => handleGenerateScript('unique_data')}
              >
                + Unique-Data Script
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="text-xs h-8"
                onClick={() => handleGenerateScript('product_value')}
              >
                + Product-Value Script
              </Button>
            </div>
          </div>

          {displayScripts.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <FileVideo className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-50" />
              <p className="text-xs text-muted-foreground">
                No scripts generated yet. Click "Generate Script" above to initiate the Script Agent.
              </p>
            </Card>
          ) : (
            displayScripts.map((script) => {
              const isGenerating = script.status === 'generating'
              const isApproved = script.status === 'approved'
              const isFailed = script.status === 'failed'
              const sceneCount = script.scenes ? script.scenes.length : 0
              const hasMinScenes = sceneCount >= 3
              const hasCoreMessage = !!script.core_message && script.core_message.trim().length > 0 && !script.core_message.startsWith('AI Script Agent is actively')
              const scriptTitle = script.campaign_title || script.title || `${script.approach.replace('_', ' ').toUpperCase()} Concept`
              const canApprove = !isGenerating && !isApproved && !isFailed && hasMinScenes && hasCoreMessage

              return (
                <Card key={script.id} className="border-border/60">
                  <CardHeader className="pb-3 border-b border-border/40">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge className={getStatusColor(script.status)}>
                            {script.status.replace('_', ' ')}
                          </Badge>
                          <span className="px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono capitalize bg-[#10141C] text-[#8E9EB5] border border-[#232B38]">
                            {script.approach.replace('_', ' ')}
                          </span>
                          {!hasMinScenes && !isGenerating && !isApproved && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono text-[#D66C73] bg-[#10141C] border border-[#232B38]">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#D66C73]" />
                              Incomplete ({sceneCount}/3 min scenes)
                            </span>
                          )}
                        </div>
                        <CardTitle className="text-base mt-2">
                          {isGenerating ? 'Generating Script Concept...' : scriptTitle}
                        </CardTitle>
                        <CardDescription className="text-xs mt-1">
                          <span className="text-foreground font-medium">Core Message: </span>
                          {script.core_message || (isGenerating ? 'AI Script Agent is synthesizing research and narrative arc...' : 'No message set')}
                        </CardDescription>
                      </div>

                      {/* Human Approval Checkpoint Actions */}
                      <div className="flex items-center gap-2">
                        {isApproved ? (
                          <div className="flex items-center gap-2">
                            <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-[4px] text-xs font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" /> APPROVED
                            </span>
                            {(() => {
                              const relatedVideos = videos
                                .filter((v) => (v.script_id ? v.script_id === script.id : v.campaign_id === campaign?.id))
                                .sort((a, b) => new Date(b.created_at || b.completed_at || 0).getTime() - new Date(a.created_at || a.completed_at || 0).getTime())

                              const activeJob = relatedVideos.find((v) =>
                                ['queued', 'processing', 'composing', 'rendering'].includes(v.status)
                              )
                              const completedJobs = relatedVideos.filter((v) => v.status === 'completed')
                              const failedJob = relatedVideos.find((v) => v.status === 'failed')
                              const isDispatching = isDispatchingVideoId === script.id
                              if (activeJob) {
                                const isJobStalled = activeJob.created_at && (Date.now() - new Date(activeJob.created_at).getTime() > 4 * 60 * 1000)
                                if (isJobStalled) {
                                  return (
                                    <div className="flex items-center gap-1.5">
                                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] text-xs font-mono text-[#E5A84B] bg-[#10141C] border border-[#5A451C]">
                                        <AlertTriangle className="h-3 w-3 mr-1 text-[#E5A84B]" /> Rendering Stalled ({activeJob.progress_percent || 0}%)
                                      </span>
                                      <Button
                                        variant="brand"
                                        size="sm"
                                        disabled={isDispatching}
                                        className="h-8 text-xs bg-[#547DB8] hover:bg-[#436494] text-white disabled:opacity-50"
                                        onClick={() => handleRenderVideo(script.id)}
                                      >
                                        <RefreshCw className="h-3.5 w-3.5 mr-1" />
                                        {isDispatching ? 'Dispatching...' : 'Restart Render'}
                                      </Button>
                                    </div>
                                  )
                                }
                                return (
                                  <div className="flex items-center gap-1.5">
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] text-xs font-mono text-[#7898C4] bg-[#10141C] border border-[#232B38] animate-pulse">
                                      <Clapperboard className="h-3 w-3 mr-1 animate-spin" /> Rendering Video ({activeJob.progress_percent || 0}%)
                                    </span>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      disabled={isDispatching}
                                      className="h-7 text-[11px] px-2 text-muted-foreground hover:text-foreground border-[#232B38]"
                                      title="Restart rendering"
                                      onClick={() => handleRenderVideo(script.id)}
                                    >
                                      <RefreshCw className="h-3 w-3 mr-1" /> Restart
                                    </Button>
                                  </div>
                                )
                              }
                              if (completedJobs.length > 0) {
                                return (
                                  <div className="flex items-center gap-1.5">
                                    <Button
                                      variant="brand"
                                      size="sm"
                                      className="h-8 text-xs bg-[#36B58F] hover:bg-[#2d9676] text-[#080A0F] font-semibold shadow-sm"
                                      onClick={() => setActiveTab('videos')}
                                    >
                                      <Play className="h-3.5 w-3.5 mr-1 fill-[#080A0F]" /> Watch Output Video ({completedJobs.length})
                                    </Button>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      disabled={isDispatching}
                                      className="h-8 text-xs text-muted-foreground hover:text-foreground"
                                      title="Render another video variation"
                                      onClick={() => handleRenderVideo(script.id)}
                                    >
                                      <RefreshCw className="h-3 w-3 mr-1" /> Re-render
                                    </Button>
                                  </div>
                                )
                              }
                              if (failedJob) {
                                return (
                                  <div className="flex items-center gap-1.5">
                                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-[4px] text-[11px] font-mono text-[#D66C73] bg-[#10141C] border border-[#5A1C24]" title={failedJob.error_message || 'Rendering was interrupted'}>
                                      <AlertTriangle className="h-3 w-3 mr-1 text-[#D66C73]" /> Interrupted
                                    </span>
                                    <Button
                                      variant="brand"
                                      size="sm"
                                      disabled={isDispatching}
                                      className="h-8 text-xs bg-[#547DB8] hover:bg-[#436494] text-white disabled:opacity-50"
                                      onClick={() => handleRenderVideo(script.id)}
                                    >
                                      <RefreshCw className="h-3.5 w-3.5 mr-1" />
                                      {isDispatching ? 'Dispatching...' : 'Retry Video Agent'}
                                    </Button>
                                  </div>
                                )
                              }
                              return (
                                <Button
                                  variant="brand"
                                  size="sm"
                                  disabled={isDispatching}
                                  className="h-8 text-xs bg-[#547DB8] hover:bg-[#436494] text-white disabled:opacity-50"
                                  onClick={() => handleRenderVideo(script.id)}
                                >
                                  <Clapperboard className="h-3.5 w-3.5 mr-1" />
                                  {isDispatching ? 'Dispatching...' : 'Dispatch to Video Agent'}
                                </Button>
                              )
                            })()}
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10"
                              title="Delete script"
                              onClick={() => handleDeleteScript(script.id)}
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        ) : isGenerating ? (
                          <div className="flex items-center gap-2">
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] text-xs font-mono text-[#D9A94F] bg-[#10141C] border border-[#232B38] animate-pulse">
                              <Clock className="h-3 w-3 mr-1" /> Generating Storyboard...
                            </span>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10"
                              title="Delete stuck script"
                              onClick={() => handleDeleteScript(script.id)}
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        ) : isFailed ? (
                          <div className="flex items-center gap-2">
                            <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-[4px] text-xs font-mono text-[#D66C73] bg-[#10141C] border border-[#232B38]">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#D66C73]" /> FAILED
                            </span>
                            <Button
                              variant="outline"
                              size="sm"
                              className="h-8 text-xs"
                              onClick={() => handleGenerateScript(script.approach)}
                            >
                              Regenerate
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10"
                              title="Delete script"
                              onClick={() => handleDeleteScript(script.id)}
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2">
                            <div className="flex flex-col items-end gap-1">
                              <Button
                                variant="brand"
                                size="sm"
                                disabled={!canApprove || isApprovingScriptId === script.id}
                                className={`h-8 text-xs ${canApprove ? 'bg-[#36B58F] hover:bg-[#2d9676] text-[#080A0F] font-semibold' : 'opacity-40 cursor-not-allowed'
                                  }`}
                                onClick={() => handleApproveScript(script)}
                              >
                                <Check className="h-3.5 w-3.5 mr-1" />
                                {isApprovingScriptId === script.id ? 'Approving...' : 'Approve Storyboard'}
                              </Button>
                              {!canApprove && (
                                <span className="text-[10px] text-muted-foreground">
                                  {!hasMinScenes ? 'Requires ≥ 3 scenes' : 'Missing core message'}
                                </span>
                              )}
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10"
                              title="Delete script"
                              onClick={() => handleDeleteScript(script.id)}
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="pt-4 space-y-4">
                    {/* Visual Hook Callout */}
                    {script.visual_hook && (
                      <div className="p-3 rounded-lg bg-[#101216] border border-[#292E37] text-xs">
                        <span className="font-semibold text-[#7898C4] block mb-0.5">
                          Opening 3-5 Second Cinematic Hook:
                        </span>
                        <p className="text-[#A0A7B2]">{script.visual_hook}</p>
                      </div>
                    )}

                    {/* Scene-by-Scene Storyboard Grid */}
                    <div>
                      <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider mb-2">
                        Scene-by-Scene Production Storyboard ({script.scenes?.length || 0} Scenes)
                      </h4>

                      {!sceneCount ? (
                        <div className="p-6 text-center border border-dashed rounded-lg bg-[#101216]/50 text-xs text-muted-foreground">
                          {isGenerating ? (
                            <div className="space-y-2">
                              <Clapperboard className="h-6 w-6 text-[#D9A94F] mx-auto animate-pulse" />
                              <p>Generating scenes and visual cues...</p>
                            </div>
                          ) : (
                            <p>No scenes found. Script is incomplete or requires regeneration.</p>
                          )}
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                          {script.scenes.map((scene, idx) => (
                            <div
                              key={idx}
                              className="p-3 rounded-lg bg-[#101216] border border-[#292E37] text-xs flex flex-col justify-between space-y-2 hover:border-[#547DB8]/40 transition-all"
                            >
                              <div className="space-y-2">
                                <div className="flex items-center justify-between text-[10px] font-mono text-muted-foreground pb-1 border-b border-[#292E37]">
                                  <span className="font-bold text-[#7898C4]">SCENE {scene.scene_number.toString().padStart(2, '0')}</span>
                                  <span>{scene.duration_seconds}s</span>
                                </div>

                                {scene.visual_asset_url && (
                                  <div className="relative w-full h-28 rounded-md overflow-hidden bg-[#080A0F] border border-[#292E37] group">
                                    <img
                                      src={resolveMediaUrl(scene.visual_asset_url)}
                                      alt={`Scene ${scene.scene_number}`}
                                      className="w-full h-full object-cover transition-transform group-hover:scale-105 duration-300"
                                    />
                                    <div className="absolute top-1.5 left-1.5">
                                      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-[3px] text-[9px] font-mono font-medium bg-[#10141C]/90 backdrop-blur text-[#D8DCE4] border border-[#232B38] shadow">
                                        <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" /> READY
                                      </span>
                                    </div>
                                    {scene.camera_motion && (
                                      <div className="absolute bottom-1 right-1">
                                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[8px] font-mono bg-[#080A0F]/85 text-[#A0A7B2] border border-[#292E37]">
                                          {scene.camera_motion.replace('_', ' ')}
                                        </span>
                                      </div>
                                    )}
                                  </div>
                                )}

                                <p className="text-foreground font-medium text-[11px] line-clamp-2">
                                  {scene.visual_description}
                                </p>
                              </div>

                              <div className="pt-2 border-t border-[#292E37] space-y-1 text-[11px]">
                                {scene.voiceover && (
                                  <div className="text-muted-foreground">
                                    <span className="text-[#C5A46D] font-semibold">VO: </span>
                                    "{scene.voiceover}"
                                  </div>
                                )}
                                {scene.on_screen_text && (
                                  <div className="text-[#7898C4] font-mono text-[10px]">
                                    TEXT: {scene.on_screen_text}
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      {/* Research References & Evidence Footprint */}
                      {script.research_references && script.research_references.length > 0 && (
                        <div className="mt-3 p-3 rounded-lg bg-[#101216] border border-[#292E37] text-xs">
                          <span className="text-[11px] font-semibold text-[#547DB8] block mb-1 flex items-center gap-1.5">
                            <Search className="h-3 w-3" /> Research Intelligence Grounding ({script.research_references.length} Meta Ad / Data References):
                          </span>
                          <ul className="list-disc list-inside space-y-0.5 text-[10px] text-muted-foreground font-mono">
                            {script.research_references.map((ref, idx) => (
                              <li key={idx} className="truncate">{ref}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Completed Video Callout Banner */}
                      {(() => {
                        const scriptVideos = videos.filter((v) => v.script_id === script.id && v.status === 'completed')
                        if (scriptVideos.length === 0) return null
                        const latest = scriptVideos[0]
                        return (
                          <div className="mt-4 p-4 rounded-xl bg-[#15191F] border border-[#36B58F]/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div className="flex items-center gap-3">
                              <div className="h-10 w-10 rounded-lg bg-[#36B58F]/15 border border-[#36B58F]/30 flex items-center justify-center shrink-0">
                                <Play className="h-5 w-5 text-[#36B58F] fill-[#36B58F]" />
                              </div>
                              <div>
                                <div className="text-xs font-semibold text-[#36B58F] flex items-center gap-1.5">
                                  <span>Cinematic Commercial MP4 Rendered & Ready!</span>
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#7898C4] bg-[#10141C] border border-[#232B38]">
                                    {latest.duration_actual ? `${Math.round(latest.duration_actual)}s` : `${latest.duration_seconds}s`} • {latest.aspect_ratio}
                                  </span>
                                </div>
                                <p className="text-[11px] text-muted-foreground mt-0.5">
                                  Complete with spoken voiceover narration, audio soundscape, motion visuals, and typography.
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2 shrink-0">
                              <Button
                                variant="brand"
                                size="sm"
                                className="h-8 text-xs bg-[#36B58F] hover:bg-[#2d9676] text-[#080A0F] font-semibold"
                                onClick={() => setActiveTab('videos')}
                              >
                                <Play className="h-3.5 w-3.5 mr-1 fill-[#080A0F]" /> Open in Video Player
                              </Button>
                              {latest.video_url && (
                                <a
                                  href={resolveMediaUrl(latest.video_url)}
                                  download={`crowdwisdom_${latest.id}.mp4`}
                                >
                                  <Button variant="outline" size="sm" className="h-8 text-xs">
                                    <Download className="h-3.5 w-3.5 mr-1" /> Download MP4
                                  </Button>
                                </a>
                              )}
                            </div>
                          </div>
                        )
                      })()}
                    </div>
                  </CardContent>
                </Card>
              )
            })
          )}
        </TabsContent>

        {/* --- 2. Creative Brief Tab (Checkpoint 1) --- */}
        <TabsContent value="brief" className="space-y-4">
          {!brief ? (
            <Card className="p-8 text-center border-dashed">
              <Sparkles className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-50" />
              <p className="text-xs text-muted-foreground mb-4">
                Creative Strategic Brief has not been synthesized yet. Launch research or synthesize directly from campaign parameters.
              </p>
              <Button size="sm" onClick={handleSynthesizeBrief} className="text-xs">
                <Sparkles className="h-3.5 w-3.5 mr-1.5" /> Synthesize Creative Brief
              </Button>
            </Card>
          ) : (
            <Card className="border-border/60">
              <CardHeader className="pb-3 border-b border-border/40 flex flex-row items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor(brief.status)}>{brief.status}</Badge>
                    <span className="text-[10px] font-mono text-muted-foreground">
                      Version {brief.version}
                    </span>
                  </div>
                  <CardTitle className="text-base mt-2">
                    {brief.content?.title || 'Creative Strategic Blueprint'}
                  </CardTitle>
                  <CardDescription className="text-xs mt-1">
                    Checkpoint 1: Human review and strategic sign-off prior to script generation.
                  </CardDescription>
                </div>

                {brief.status === 'pending_approval' ? (
                  <Button
                    size="sm"
                    disabled={isApprovingBrief}
                    onClick={handleApproveBrief}
                    className="text-xs bg-[#36B58F] hover:bg-[#2d9676] text-[#080A0F] font-semibold"
                  >
                    <Check className="h-3.5 w-3.5 mr-1.5" />
                    {isApprovingBrief ? 'Approving...' : 'Approve Brief (Checkpoint 1)'}
                  </Button>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] text-xs font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" /> APPROVED BY {brief.approved_by || 'STRATEGIST'}
                  </span>
                )}
              </CardHeader>

              <CardContent className="pt-4 space-y-4 text-xs">
                <div>
                  <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] mb-1">
                    Executive Strategic Summary
                  </h4>
                  <p className="text-muted-foreground leading-relaxed">
                    {brief.content?.executive_summary || 'Antidote to noisy retail trading sentiment.'}
                  </p>
                </div>

                {brief.content?.target_audience_deep_dive && (
                  <div className="p-3 rounded-lg bg-card/60 border border-border/40 space-y-2">
                    <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px]">
                      Audience Psychology Deep Dive
                    </h4>
                    <p className="text-muted-foreground">
                      <span className="text-foreground font-medium">Persona: </span>
                      {brief.content.target_audience_deep_dive.primary_persona}
                    </p>
                    <p className="text-muted-foreground">
                      <span className="text-foreground font-medium">Psychological State: </span>
                      {brief.content.target_audience_deep_dive.psychological_state}
                    </p>
                    <p className="text-muted-foreground">
                      <span className="text-foreground font-medium">Core Desire: </span>
                      {brief.content.target_audience_deep_dive.core_desire}
                    </p>
                  </div>
                )}

                {brief.content?.compliance_guardrails && (
                  <div>
                    <h4 className="font-semibold text-foreground uppercase tracking-wider text-[11px] mb-1 flex items-center gap-1.5">
                      <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" /> Compliance Guardrails
                    </h4>
                    <ul className="list-disc list-inside text-muted-foreground space-y-0.5">
                      {brief.content.compliance_guardrails.map((g: string, i: number) => (
                        <li key={i}>{g}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* --- 3. Rendered Videos Tab (Checkpoint 3) --- */}
        <TabsContent value="videos" className="space-y-4">
          {videos.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <Clapperboard className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-50" />
              <p className="text-xs text-muted-foreground">
                No videos rendered yet. Approve a storyboard script to initiate cinematic video rendering.
              </p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...videos]
                .sort((a, b) => {
                  if (a.status === 'completed' && b.status !== 'completed') return -1
                  if (a.status !== 'completed' && b.status === 'completed') return 1
                  return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
                })
                .map((vid) => (
                  <Card key={vid.id} className="border-border/60 overflow-hidden flex flex-col justify-between">
                    <div className="bg-[#060911] w-full flex items-center justify-center p-3 relative">
                      <div className="aspect-[9/16] w-full max-w-[280px] sm:max-w-[320px] max-h-[560px] flex items-center justify-center relative rounded-xl overflow-hidden bg-black shadow-2xl border border-border/40">
                        {vid.video_url ? (
                          <video
                            key={vid.id}
                            controls
                            playsInline
                            preload="metadata"
                            className="h-full w-full object-contain"
                          >
                            <source src={resolveMediaUrl(vid.video_url)} type="video/mp4" />
                            Your browser does not support HTML5 MP4 video.
                          </video>
                        ) : vid.status === 'failed' ? (
                          <div className="text-center p-6 space-y-2">
                            <AlertTriangle className="h-8 w-8 text-rose-400 mx-auto opacity-70" />
                            <p className="text-xs text-rose-300 font-medium">
                              Render Interrupted ({vid.progress_percent}%)
                            </p>
                            <p className="text-[10px] text-muted-foreground px-4">
                              {vid.error_message || 'Video rendering job stopped.'}
                            </p>
                            {vid.script_id && (
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-xs h-7 mt-2 border-rose-500/30 hover:bg-rose-500/10 text-rose-200"
                                onClick={() => handleRenderVideo(vid.script_id!)}
                              >
                                <RefreshCw className="h-3 w-3 mr-1" /> Retry Render
                              </Button>
                            )}
                          </div>
                        ) : (
                          <div className="text-center p-6 space-y-2">
                            <Clapperboard className="h-8 w-8 text-muted-foreground mx-auto animate-pulse" />
                            <p className="text-xs text-muted-foreground capitalize">
                              Status: {vid.status} ({vid.progress_percent}%)
                            </p>
                            {vid.script_id && vid.created_at && (Date.now() - new Date(vid.created_at).getTime() > 4 * 60 * 1000) && (
                              <div className="pt-2">
                                <p className="text-[10px] text-[#E5A84B] mb-1.5">Render may have stalled</p>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="text-xs h-7 border-[#E5A84B]/40 hover:bg-[#E5A84B]/10 text-[#E5A84B]"
                                  onClick={() => handleRenderVideo(vid.script_id!)}
                                >
                                  <RefreshCw className="h-3 w-3 mr-1" /> Restart Render
                                </Button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                    <CardContent className="p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <Badge className={getStatusColor(vid.status)}>
                          {vid.status === 'completed' ? 'Completed Commercial' : vid.status}
                        </Badge>
                        <span className="text-xs font-mono text-muted-foreground">
                          {vid.duration_actual ? `${Math.round(vid.duration_actual)}s` : `${vid.duration_seconds}s`} • {vid.aspect_ratio}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 mt-2">
                        {vid.video_url && (
                          <a href={resolveMediaUrl(vid.video_url)} download={`crowdwisdom_${vid.id}.mp4`} className="flex-1">
                            <Button variant="brand" size="sm" className="w-full text-xs bg-[#36B58F] hover:bg-[#2d9676] text-[#080A0F] font-semibold">
                              <Download className="h-3.5 w-3.5 mr-1.5" /> Download MP4 Commercial
                            </Button>
                          </a>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-xs text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 h-8 px-2"
                          title="Delete video record and file"
                          onClick={() => handleDeleteVideo(vid.id)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
            </div>
          )}
        </TabsContent>

        {/* --- 4. Ad Intelligence Tab --- */}
        <TabsContent value="research" className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-1 border-b border-border/40">
            <div>
              <h4 className="text-sm font-semibold text-foreground">Competitor Ad Intelligence</h4>
              <p className="text-[11px] text-muted-foreground">
                Verified Meta Ads Library advertisements linked to this campaign.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Link to="/research">
                <Button variant="outline" size="sm" className="text-xs h-7">
                  <FolderPlus className="h-3.5 w-3.5 mr-1" />
                  Select & Link Ads ({ads.length} Linked)
                </Button>
              </Link>
              <Button size="sm" variant="brand" onClick={handleLaunchResearch} className="text-xs h-7">
                <Search className="h-3.5 w-3.5 mr-1" />
                Run Meta Ads Scraper
              </Button>
            </div>
          </div>

          {ads.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <Search className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-50" />
              <p className="text-xs text-muted-foreground mb-4">
                No competitor ads linked yet. You can link existing verified ads from the Research Intelligence Library or run the Meta Ads scraper.
              </p>
              <div className="flex items-center justify-center gap-2">
                <Link to="/research">
                  <Button variant="brand" size="sm" className="text-xs">
                    <FolderPlus className="h-3.5 w-3.5 mr-1.5" /> Link from Research Library
                  </Button>
                </Link>
                <Button variant="outline" size="sm" onClick={handleLaunchResearch} className="text-xs">
                  <Search className="h-3.5 w-3.5 mr-1.5" /> Launch Meta Ads Scraper
                </Button>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {ads.map((ad) => (
                <Card key={ad.id} className="p-4 border-border/50 text-xs space-y-2 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-foreground truncate">{ad.advertiser}</span>
                      {ad.evaluation_score && (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded-[4px] text-[10px] font-mono font-semibold text-[#8EA2C6] bg-[#10141C] border border-[#232B38]">
                          {ad.evaluation_score.overall}/10 SCORE
                        </span>
                      )}
                    </div>
                    <p className="text-muted-foreground line-clamp-3">"{ad.ad_text}"</p>
                    {ad.hook && (
                      <div className="text-[11px] text-[#C5A46D]">
                        <span className="font-semibold">Hook: </span>
                        {ad.hook}
                      </div>
                    )}
                  </div>
                  {ad.meta_ads_url && (
                    <div className="pt-2 border-t border-[#292E37]">
                      <a
                        href={ad.meta_ads_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[10px] text-[#7898C4] hover:underline flex items-center gap-1 font-mono"
                      >
                        <ExternalLink className="h-3 w-3" /> Meta Library Reference
                      </a>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* --- 5. Marketing Insights Tab --- */}
        <TabsContent value="insights" className="space-y-4">
          {insights.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <Lightbulb className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-50" />
              <p className="text-xs text-muted-foreground">
                No marketing insights extracted yet. Launch research to populate insights.
              </p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {insights.map((ins) => (
                <Card key={ins.id} className="p-4 border-border/50 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono capitalize bg-[#10141C] text-[#8E9EB5] border border-[#232B38]">
                      {ins.category.replace('_', ' ')}
                    </span>
                    <span className="text-[11px] font-mono text-emerald-400">
                      {Math.round(ins.confidence * 100)}% Confidence
                    </span>
                  </div>
                  <h4 className="font-semibold text-foreground text-sm">{ins.title}</h4>
                  <p className="text-muted-foreground leading-relaxed">{ins.description}</p>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* --- 6. Media Assets Tab --- */}
        <TabsContent value="assets" className="space-y-4">
          {assets.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <FolderOpen className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-50" />
              <p className="text-xs text-muted-foreground">
                No media files recorded for this campaign yet.
              </p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {assets.map((asset) => (
                <Card key={asset.id} className="p-4 border-border/50 text-xs space-y-2 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono capitalize bg-[#10141C] text-[#8E9EB5] border border-[#232B38]">{asset.asset_type}</span>
                      <span className="text-[10px] font-mono text-muted-foreground">
                        {asset.file_size_bytes ? formatFileSize(asset.file_size_bytes) : ''}
                      </span>
                    </div>
                    <p className="font-semibold text-foreground line-clamp-1">{asset.filename}</p>
                    <span className="text-[10px] text-muted-foreground font-mono">
                      {formatRelativeTime(asset.created_at)}
                    </span>
                  </div>

                  {asset.url && (
                    <a href={resolveMediaUrl(asset.url)} download={asset.filename}>
                      <Button variant="outline" size="sm" className="w-full text-xs">
                        <Download className="h-3 w-3 mr-1" /> Download Asset
                      </Button>
                    </a>
                  )}
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* --- 7. Audience & Parameters Tab --- */}
        <TabsContent value="config">
          <Card className="p-6 border-border/60 text-xs space-y-4">
            <div>
              <h4 className="font-semibold text-foreground">Target Audience Segments</h4>
              <p className="text-muted-foreground mt-0.5">
                {campaign.audience?.segments?.join(', ') || 'Retail traders, options traders'}
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-foreground">Creative Direction</h4>
              <p className="text-muted-foreground mt-0.5">{campaign.creative_direction}</p>
            </div>
            {campaign.compliance_rules && campaign.compliance_rules.length > 0 && (
              <div>
                <h4 className="font-semibold text-foreground flex items-center gap-1.5">
                  <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" /> Compliance Rules Enforced
                </h4>
                <ul className="list-disc list-inside text-muted-foreground space-y-0.5 mt-1">
                  {campaign.compliance_rules.map((rule, idx) => (
                    <li key={idx}>{rule}</li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
