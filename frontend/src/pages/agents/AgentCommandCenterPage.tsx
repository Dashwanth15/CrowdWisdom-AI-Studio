import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Bot,
  Play,
  RotateCcw,
  XCircle,
  Terminal,
  Activity,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  Search,
  FileVideo,
  Clapperboard,
  Download,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  Check,
} from 'lucide-react'
import { agentsApi, campaignsApi, scriptsApi, videosApi, researchApi } from '@/lib/api'
import { AgentExecution, Campaign, AgentType, Script, VideoJob } from '@/types'
import { wsManager } from '@/lib/websocket'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { getStatusColor, formatRelativeTime, formatDuration, resolveMediaUrl } from '@/lib/utils'
import toast from 'react-hot-toast'

export const AgentCommandCenterPage: React.FC = () => {
  const [executions, setExecutions] = useState<AgentExecution[]>([])
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [selectedCampaign, setSelectedCampaign] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)

  // Real-time progress trackers per agent
  const [agentProgress, setAgentProgress] = useState<Record<string, { pct: number; stage: string }>>({
    ads_manager: { pct: 0, stage: 'Idle' },
    script: { pct: 0, stage: 'Idle' },
    video_production: { pct: 0, stage: 'Idle' },
  })

  // Selected Campaign Artifacts
  const [campaignScripts, setCampaignScripts] = useState<Script[]>([])
  const [campaignVideos, setCampaignVideos] = useState<VideoJob[]>([])
  const [campaignAdsCount, setCampaignAdsCount] = useState<number>(0)
  const [isDispatchingVideo, setIsDispatchingVideo] = useState(false)
  const [previewVideoUrl, setPreviewVideoUrl] = useState<string | null>(null)

  // Logs Viewer Modal
  const [logsExecutionId, setLogsExecutionId] = useState<string | null>(null)
  const [activeLogs, setActiveLogs] = useState<any[]>([])

  useEffect(() => {
    loadData()

    // Subscribe to WebSocket live updates
    const unsubProgress = wsManager.on('job_progress', (data: any) => {
      if (data.job_type && data.progress_percent !== undefined) {
        setAgentProgress((prev) => ({
          ...prev,
          [data.job_type]: {
            pct: data.progress_percent,
            stage: data.current_stage || 'Processing...',
          },
        }))
      }
      if (data.status === 'completed') {
        if (selectedCampaign) loadCampaignArtifacts(selectedCampaign)
        if (data.job_type === 'video_production') {
          toast.success('🎬 Video production complete! Click "Watch Output Video" to play.', { duration: 6000 })
        }
      }
      loadExecutions()
    })

    const unsubStatus = wsManager.on('agent_status', () => {
      loadExecutions()
      if (selectedCampaign) loadCampaignArtifacts(selectedCampaign)
    })

    return () => {
      unsubProgress()
      unsubStatus()
    }
  }, [selectedCampaign])

  useEffect(() => {
    if (selectedCampaign) {
      loadCampaignArtifacts(selectedCampaign)
    }
  }, [selectedCampaign])

  const loadCampaignArtifacts = async (campaignId: string) => {
    if (!campaignId) return
    try {
      const [scriptsRes, vidsRes, adsRes] = await Promise.all([
        scriptsApi.list({ campaign_id: campaignId }),
        videosApi.list({ campaign_id: campaignId }),
        researchApi.listAds({ campaign_id: campaignId }),
      ])
      const sList = scriptsRes.data || []
      const vList = vidsRes.data || []
      const aList = adsRes.data || []

      setCampaignScripts(sList)
      setCampaignVideos(vList)
      setCampaignAdsCount(aList.length)

      // Synchronize agent cards to ground-truth results of the selected campaign
      if (aList.length > 0) {
        setAgentProgress((prev) => ({
          ...prev,
          ads_manager: prev.ads_manager.pct === 0 || prev.ads_manager.stage === 'Idle'
            ? { pct: 100, stage: `Completed (${aList.length} ads)` }
            : prev.ads_manager,
        }))
      }

      const approvedScript = sList.find((s: Script) => s.status === 'approved')
      if (sList.length > 0) {
        setAgentProgress((prev) => ({
          ...prev,
          script: prev.script.pct === 0 || prev.script.stage === 'Idle'
            ? { pct: 100, stage: approvedScript ? 'Completed (Storyboard Approved)' : `Completed (${sList.length} scripts)` }
            : prev.script,
        }))
      }

      const completedVid = vList.find((v: VideoJob) => v.status === 'completed')
      const activeVid = vList.find((v: VideoJob) => ['queued', 'processing', 'composing', 'rendering'].includes(v.status))
      if (activeVid) {
        setAgentProgress((prev) => ({
          ...prev,
          video_production: { pct: activeVid.progress_percent || 50, stage: activeVid.current_stage || 'Rendering video...' },
        }))
      } else if (completedVid) {
        setAgentProgress((prev) => ({
          ...prev,
          video_production: prev.video_production.pct === 0 || prev.video_production.stage === 'Idle'
            ? { pct: 100, stage: 'Completed (MP4 Video Ready)' }
            : prev.video_production,
        }))
      }
    } catch (err) {
      console.warn('Failed to load campaign artifacts', err)
    }
  }

  const loadData = async () => {
    setIsLoading(true)
    try {
      const [campsRes, execsRes] = await Promise.all([
        campaignsApi.list(),
        agentsApi.listExecutions({ limit: 50 }),
      ])
      setCampaigns(campsRes.data)
      setExecutions(execsRes.data)
      if (campsRes.data.length > 0) {
        const initialCid = campsRes.data[0].id
        setSelectedCampaign(initialCid)
        loadCampaignArtifacts(initialCid)
      }
    } catch (err) {
      toast.error('Failed to load agent command center')
    } finally {
      setIsLoading(false)
    }
  }

  const loadExecutions = async () => {
    try {
      const res = await agentsApi.listExecutions({ limit: 50 })
      setExecutions(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleLaunchAgent = async (agentType: AgentType) => {
    if (!selectedCampaign) {
      toast.error('Please select an active campaign first.')
      return
    }

    try {
      if (agentType === 'ads_manager') {
        await agentsApi.launchResearch({
          campaign_id: selectedCampaign,
          keywords: ['market sentiment trading', 'retail investor intelligence', 'options flow'],
          date_range_days: 30,
        })
        toast.success('Ads Manager Agent dispatched!')
      } else if (agentType === 'script') {
        await agentsApi.generateScript({
          campaign_id: selectedCampaign,
          approach: 'pain_point',
        })
        toast.success('Script Agent dispatched!')
      }
      loadExecutions()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to dispatch agent')
    }
  }

  const handleLaunchVideoProduction = async () => {
    if (!selectedCampaign) {
      toast.error('Please select an active campaign first.')
      return
    }
    const approvedScript = campaignScripts.find((s) => s.status === 'approved') || campaignScripts[0]
    if (!approvedScript) {
      toast.error('No script found for this campaign. Please dispatch the Script Agent first.')
      return
    }

    setIsDispatchingVideo(true)
    try {
      const camp = campaigns.find((c) => c.id === selectedCampaign)
      await videosApi.generate({
        campaign_id: selectedCampaign,
        script_id: approvedScript.id,
        aspect_ratio: camp?.video_aspect_ratio || '9:16',
        duration_seconds: camp?.video_duration_seconds || 45,
        quality: 'high',
      })
      toast.success('Video Production Agent dispatched!')
      setAgentProgress((prev) => ({
        ...prev,
        video_production: { pct: 15, stage: 'Setting up scene timeline...' },
      }))
      loadCampaignArtifacts(selectedCampaign)
      loadExecutions()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to dispatch video production')
    } finally {
      setIsDispatchingVideo(false)
    }
  }

  const handleCancel = async (executionId: string) => {
    try {
      await agentsApi.cancelExecution(executionId)
      toast.success('Agent execution cancelled.')
      loadExecutions()
    } catch (err: any) {
      toast.error('Failed to cancel execution')
    }
  }

  const handleRetry = async (executionId: string) => {
    try {
      await agentsApi.retryExecution(executionId)
      toast.success('Agent task retried!')
      loadExecutions()
    } catch (err: any) {
      toast.error('Failed to retry execution')
    }
  }

  const openLogs = async (executionId: string) => {
    setLogsExecutionId(executionId)
    try {
      const res = await agentsApi.getExecutionLogs(executionId)
      setActiveLogs(res.data)
    } catch (err) {
      toast.error('Failed to fetch execution logs')
    }
  }

  const renderExecutionModeBadge = (mode?: string, status?: string) => {
    if (status === 'failed' || mode === 'failed') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#D66C73]" />
          FAILED
        </span>
      )
    }
    if (mode === 'native_hermes') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" />
          HERMES NATIVE
        </span>
      )
    }
    if (mode === 'llm_fallback') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#D9A94F]" />
          LLM FALLBACK
        </span>
      )
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#727B89] bg-[#10141C] border border-[#232B38]">
        <span className="w-1.5 h-1.5 rounded-full bg-[#727B89]" />
        UNCONFIGURED
      </span>
    )
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#292E37]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono uppercase tracking-wider text-[#C5CAD3] bg-[#10141C] border border-[#232B38]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#547DB8]" />
              AUTONOMOUS FLEET
            </span>
            <span className="text-xs text-[#727B89] font-mono">• 3 Specialized Agents Active</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
            <Bot className="h-6 w-6 text-[#547DB8]" />
            AI Agent Command Center
          </h1>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            Orchestrate, monitor, and inspect autonomous Hermes agent executions in real-time.
          </p>
        </div>

        {/* Campaign Selector */}
        {campaigns.length > 0 && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-[#A0A7B2]">Target Campaign:</span>
            <select
              className="bg-[#101216] border border-[#292E37] rounded-md px-3 py-1.5 text-xs font-medium text-[#F2F3F5] outline-none focus:border-[#547DB8] transition-colors"
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
            >
              {campaigns.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Runtime Architecture Transparency Strip */}
      <div className="bg-[#101216] border border-[#292E37] rounded-lg p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <span className="font-mono text-[#727B89]">Framework:</span>
          <span className="font-mono text-[11px] text-[#8E9EB5] bg-[#141820] border border-[#232B38] px-2 py-0.5 rounded-[4px]">
            NousResearch/hermes-agent@c55af2c9
          </span>
          <span className="text-[#292E37] hidden sm:inline">|</span>
          <span className="font-mono text-[#727B89] hidden sm:inline">Tool Registry:</span>
          <span className="font-mono text-[#F2F3F5] font-semibold hidden sm:inline">tools.registry.registry</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-[#A0A7B2]">Telemetry Mode:</span>
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#141820] border border-[#232B38]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" />
            NATIVE HERMES ACTIVE
          </span>
        </div>
      </div>

      {/* 3 Active Agent Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Agent 1: Ads Manager */}
        <Card className="border-[#292E37] bg-[#15191F] flex flex-col justify-between">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-[#7898C4] uppercase tracking-wider font-semibold">HERMES / RESEARCH</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-[3px] bg-[#10141C] border border-[#232B38] text-[#8E9EB5]">Apify Meta Scraper</span>
            </div>
            <CardTitle className="text-base mt-2 flex items-center gap-2 text-[#F2F3F5]">
              <Search className="h-4 w-4 text-[#547DB8]" />
              Ads Manager Agent
            </CardTitle>
            <CardDescription className="text-xs text-[#A0A7B2]">
              Crawls Meta Ads Library, performs ad evaluation, and extracts psychological triggers.
            </CardDescription>
          </CardHeader>

          <CardContent className="pt-0 space-y-3">
            <div>
              <div className="flex justify-between text-[11px] mb-1 font-mono text-[#A0A7B2]">
                <span className="truncate pr-2">Stage: {agentProgress.ads_manager.stage}</span>
                <span className="tabular-nums font-semibold">{agentProgress.ads_manager.pct}%</span>
              </div>
              <Progress value={agentProgress.ads_manager.pct} />
            </div>

            {campaignAdsCount > 0 || agentProgress.ads_manager.pct === 100 ? (
              <div className="flex items-center gap-2">
                <Link to="/research" className="flex-1">
                  <Button variant="brand" size="sm" className="w-full text-xs bg-[#547DB8] hover:bg-[#436494] text-white font-medium">
                    <Search className="h-3.5 w-3.5 mr-1" />
                    View Researched Ads {campaignAdsCount > 0 ? `(${campaignAdsCount})` : ''}
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs px-2.5 h-8 text-[#A0A7B2] hover:text-[#F2F3F5] border-[#292E37]"
                  title="Re-run Ads Manager Scraper"
                  onClick={() => handleLaunchAgent('ads_manager')}
                >
                  <RotateCcw className="h-3 w-3" />
                </Button>
              </div>
            ) : (
              <Button
                variant="brand"
                size="sm"
                className="w-full text-xs bg-[#547DB8] hover:bg-[#436494] text-white font-medium"
                onClick={() => handleLaunchAgent('ads_manager')}
              >
                <Play className="h-3 w-3 mr-1.5" />
                Dispatch Ads Manager
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Agent 2: Script Agent */}
        <Card className="border-[#292E37] bg-[#15191F] flex flex-col justify-between">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-[#C5A46D] uppercase tracking-wider font-semibold">HERMES / CREATIVE</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-[3px] bg-[#10141C] border border-[#232B38] text-[#8E9EB5]">Tavily / LLM</span>
            </div>
            <CardTitle className="text-base mt-2 flex items-center gap-2 text-[#F2F3F5]">
              <FileVideo className="h-4 w-4 text-[#C5A46D]" />
              Script Agent
            </CardTitle>
            <CardDescription className="text-xs text-[#A0A7B2]">
              Drafts 30-60s cinematic storyboards with camera directions, voiceovers, and visual hooks.
            </CardDescription>
          </CardHeader>

          <CardContent className="pt-0 space-y-3">
            <div>
              <div className="flex justify-between text-[11px] mb-1 font-mono text-[#A0A7B2]">
                <span className="truncate pr-2">Stage: {agentProgress.script.stage}</span>
                <span className="tabular-nums font-semibold">{agentProgress.script.pct}%</span>
              </div>
              <Progress value={agentProgress.script.pct} />
            </div>

            {campaignScripts.length > 0 || agentProgress.script.pct === 100 ? (
              <div className="flex items-center gap-2">
                <Link to={selectedCampaign ? `/campaigns/${selectedCampaign}` : '/scripts'} className="flex-1">
                  <Button variant="brand" size="sm" className="w-full text-xs bg-[#547DB8] hover:bg-[#436494] text-white font-medium">
                    <FileVideo className="h-3.5 w-3.5 mr-1" />
                    Review Storyboards ({campaignScripts.length})
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs px-2.5 h-8 text-[#A0A7B2] hover:text-[#F2F3F5] border-[#292E37]"
                  title="Re-run Script Agent"
                  onClick={() => handleLaunchAgent('script')}
                >
                  <RotateCcw className="h-3 w-3" />
                </Button>
              </div>
            ) : (
              <Button
                variant="brand"
                size="sm"
                className="w-full text-xs bg-[#547DB8] hover:bg-[#436494] text-white font-medium"
                onClick={() => handleLaunchAgent('script')}
              >
                <Play className="h-3 w-3 mr-1.5" />
                Dispatch Script Agent
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Agent 3: Video Production Agent */}
        <Card className="border-[#292E37] bg-[#15191F] flex flex-col justify-between">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-[#7898C4] uppercase tracking-wider font-semibold">OPENMONTAGE / VIDEO</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-[3px] bg-[#10141C] border border-[#232B38] text-[#8E9EB5]">MoviePy / Composite</span>
            </div>
            <CardTitle className="text-base mt-2 flex items-center gap-2 text-[#F2F3F5]">
              <Clapperboard className="h-4 w-4 text-[#547DB8]" />
              Video Production Agent
            </CardTitle>
            <CardDescription className="text-xs text-[#A0A7B2]">
              Composes scenes from approved storyboards into final high-definition MP4 advertisements.
            </CardDescription>
          </CardHeader>

          <CardContent className="pt-0 space-y-3">
            <div>
              <div className="flex justify-between text-[11px] mb-1 font-mono text-[#A0A7B2]">
                <span className="truncate pr-2">Stage: {agentProgress.video_production.stage}</span>
                <span className="tabular-nums font-semibold">{agentProgress.video_production.pct}%</span>
              </div>
              <Progress value={agentProgress.video_production.pct} />
            </div>

            {(() => {
              const isRendering = ['queued', 'processing', 'composing', 'rendering'].includes(
                agentProgress.video_production.stage.toLowerCase()
              ) || (agentProgress.video_production.pct > 0 && agentProgress.video_production.pct < 100)
              
              const completedVideo = campaignVideos.find((v) => v.status === 'completed') || 
                (agentProgress.video_production.pct === 100 && campaignVideos.length > 0 ? campaignVideos[0] : null)
              
              const approvedScript = campaignScripts.find((s) => s.status === 'approved')
              const hasAnyScript = campaignScripts.length > 0

              if (isRendering) {
                return (
                  <Button variant="brand" size="sm" disabled className="w-full text-xs bg-[#547DB8]/80 animate-pulse text-white font-medium">
                    <Clapperboard className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                    Rendering Video ({agentProgress.video_production.pct}%)
                  </Button>
                )
              }

              if (completedVideo && completedVideo.video_url) {
                return (
                  <div className="space-y-2">
                    <Button
                      variant="brand"
                      size="sm"
                      className="w-full text-xs bg-[#36B58F] hover:bg-[#2d9676] text-[#080A0F] font-semibold py-2 shadow-sm flex items-center justify-center gap-1.5"
                      onClick={() => setPreviewVideoUrl(resolveMediaUrl(completedVideo.video_url))}
                    >
                      <Play className="h-3.5 w-3.5 fill-[#080A0F]" />
                      Watch Output Video (MP4)
                    </Button>
                    <div className="flex items-center gap-2">
                      <a
                        href={resolveMediaUrl(completedVideo.video_url)}
                        download={`crowdwisdom_${completedVideo.id}.mp4`}
                        className="flex-1"
                      >
                        <Button variant="outline" size="sm" className="w-full text-[11px] h-7 border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]">
                          <Download className="h-3 w-3 mr-1" /> Download MP4
                        </Button>
                      </a>
                      {selectedCampaign && (
                        <Link to={`/campaigns/${selectedCampaign}`}>
                          <Button variant="outline" size="sm" className="text-[11px] h-7 px-2 border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]" title="Open in Campaign Hub">
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                        </Link>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-[11px] h-7 px-2 border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]"
                        title="Re-render another cut"
                        disabled={isDispatchingVideo || !approvedScript}
                        onClick={handleLaunchVideoProduction}
                      >
                        <RotateCcw className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                )
              }

              // If script is generated but not approved, provide quick action to approve in campaign hub
              if (hasAnyScript && !approvedScript) {
                return (
                  <div className="space-y-2">
                    <Link to={selectedCampaign ? `/campaigns/${selectedCampaign}` : '/campaigns'} className="block">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full text-xs border-[#D9A94F]/40 bg-[#D9A94F]/10 text-[#D9A94F] hover:bg-[#D9A94F]/20 font-medium flex items-center justify-center gap-1.5"
                      >
                        <ShieldCheck className="h-3.5 w-3.5" />
                        Approve Storyboard in Campaign Hub →
                      </Button>
                    </Link>
                    <span className="block text-center text-[10px] text-[#727B89]">
                      Human approval required before dispatching video render
                    </span>
                  </div>
                )
              }

              return (
                <div className="space-y-2">
                  <Button
                    variant="brand"
                    size="sm"
                    className="w-full text-xs bg-[#547DB8] hover:bg-[#436494] text-white font-medium"
                    disabled={isDispatchingVideo || !approvedScript}
                    onClick={handleLaunchVideoProduction}
                  >
                    <Clapperboard className="h-3.5 w-3.5 mr-1.5" />
                    {isDispatchingVideo
                      ? 'Dispatching...'
                      : approvedScript
                      ? 'Dispatch Video Production'
                      : 'Dispatch Script Agent First'}
                  </Button>
                  <Link to="/videos" className="block text-center text-[11px] text-[#727B89] hover:text-[#F2F3F5] transition-colors">
                    Open Video Studio →
                  </Link>
                </div>
              )
            })()}
          </CardContent>
        </Card>
      </div>

      {/* Execution History Table */}
      <Card className="border-[#292E37] bg-[#15191F]">
        <CardHeader className="pb-3 border-b border-[#292E37]/60">
          <CardTitle className="text-sm font-semibold flex items-center justify-between text-[#F2F3F5]">
            <span className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-[#547DB8]" />
              Persistent Execution History & Task Queue
            </span>
            <Button variant="ghost" size="sm" onClick={loadExecutions} className="h-7 text-xs text-[#A0A7B2] hover:text-[#F2F3F5]">
              <RotateCcw className="h-3 w-3 mr-1" /> Refresh
            </Button>
          </CardTitle>
        </CardHeader>

        <CardContent className="pt-0 p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#101216] border-b border-[#292E37] text-[#727B89] font-mono text-[11px]">
                <tr>
                  <th className="py-2.5 px-4">Agent</th>
                  <th className="py-2.5 px-4">Task Name</th>
                  <th className="py-2.5 px-4">Runtime Mode</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4">Duration</th>
                  <th className="py-2.5 px-4">Started</th>
                  <th className="py-2.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#292E37]/50">
                {executions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-xs text-[#727B89]">
                      No agent executions recorded yet. Dispatch an agent above to begin.
                    </td>
                  </tr>
                ) : (
                  executions.map((exec) => (
                    <tr key={exec.id} className="hover:bg-[#1B2028] transition-colors">
                      <td className="py-3 px-4 font-medium capitalize flex items-center gap-2 text-[#F2F3F5]">
                        <span className="h-2 w-2 rounded-full bg-[#547DB8]" />
                        {exec.agent_type.replace('_', ' ')}
                      </td>
                      <td className="py-3 px-4 text-[#F2F3F5] font-medium">{exec.task_name}</td>
                      <td className="py-3 px-4">
                        {renderExecutionModeBadge(exec.execution_mode, exec.status)}
                      </td>
                      <td className="py-3 px-4">
                        <Badge className={getStatusColor(exec.status)}>
                          {exec.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 font-mono text-[#A0A7B2] tabular-nums">
                        {exec.duration_seconds ? formatDuration(exec.duration_seconds) : '-'}
                      </td>
                      <td className="py-3 px-4 text-[#727B89]">
                        {formatRelativeTime(exec.created_at)}
                      </td>
                      <td className="py-3 px-4 text-right space-x-1.5">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 px-2 text-[11px] text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#232A34]"
                          onClick={() => openLogs(exec.id)}
                        >
                          <Terminal className="h-3 w-3 mr-1" />
                          Logs
                        </Button>

                        {exec.status === 'running' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 px-2 text-[11px] text-[#D66C73] hover:bg-[#D66C73]/10"
                            onClick={() => handleCancel(exec.id)}
                          >
                            <XCircle className="h-3 w-3 mr-1" />
                            Cancel
                          </Button>
                        )}

                        {exec.status === 'failed' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 px-2 text-[11px] text-[#D9A94F] hover:bg-[#D9A94F]/10"
                            onClick={() => handleRetry(exec.id)}
                          >
                            <RotateCcw className="h-3 w-3 mr-1" />
                            Retry
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Execution Logs Modal */}
      <Dialog open={!!logsExecutionId} onOpenChange={() => setLogsExecutionId(null)}>
        <DialogContent className="max-w-2xl bg-[#15191F] border-[#292E37]">
          <DialogHeader>
            <DialogTitle className="text-sm font-mono flex items-center gap-2 text-[#F2F3F5]">
              <Terminal className="h-4 w-4 text-[#547DB8]" />
              Detailed Execution Log Stream
            </DialogTitle>
            <DialogDescription className="text-xs font-mono text-[#727B89]">
              Execution ID: {logsExecutionId}
            </DialogDescription>
          </DialogHeader>

          <div className="h-80 overflow-y-auto bg-[#080A0F] rounded-lg p-3 font-mono text-[11px] space-y-1.5 border border-[#292E37]">
            {activeLogs.length === 0 ? (
              <span className="text-[#727B89]">No log entries found.</span>
            ) : (
              activeLogs.map((lg) => (
                <div key={lg.id} className="flex items-start gap-2 text-[#F2F3F5]/90">
                  <span className="text-[#727B89]">[{lg.created_at.slice(11, 19)}]</span>
                  <span className="text-[#7898C4] font-semibold uppercase">{lg.stage}:</span>
                  <span className="text-[#A0A7B2]">{lg.message}</span>
                </div>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Video Preview Modal */}
      <Dialog open={!!previewVideoUrl} onOpenChange={() => setPreviewVideoUrl(null)}>
        <DialogContent className="max-w-2xl bg-[#15191F] border-[#292E37] p-4">
          <DialogHeader className="pb-2 border-b border-[#292E37]">
            <DialogTitle className="text-sm font-semibold flex items-center justify-between text-[#F2F3F5]">
              <span className="flex items-center gap-2">
                <Clapperboard className="h-4 w-4 text-[#36B58F]" />
                Rendered Commercial Video Output
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-[10px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" />
                COMPLETED MP4
              </span>
            </DialogTitle>
          </DialogHeader>

          {previewVideoUrl && (
            <div className="aspect-[9/16] max-h-[65vh] mx-auto bg-[#080A0F] rounded-lg overflow-hidden flex items-center justify-center my-2 border border-[#292E37]">
              <video
                controls
                autoPlay
                playsInline
                className="h-full w-full object-contain"
                src={previewVideoUrl}
              >
                Your browser does not support HTML5 video.
              </video>
            </div>
          )}

          <div className="flex items-center justify-between pt-2 border-t border-[#292E37]">
            {selectedCampaign && (
              <Link to={`/campaigns/${selectedCampaign}`}>
                <Button variant="outline" size="sm" className="text-xs border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]">
                  <ExternalLink className="h-3.5 w-3.5 mr-1" /> Open in Campaign Hub
                </Button>
              </Link>
            )}
            {previewVideoUrl && (
              <a href={previewVideoUrl} download="crowdwisdom_commercial.mp4">
                <Button variant="brand" size="sm" className="text-xs bg-[#36B58F] hover:bg-[#2d9676] text-[#080A0F] font-semibold">
                  <Download className="h-3.5 w-3.5 mr-1" /> Download MP4 Commercial
                </Button>
              </a>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
