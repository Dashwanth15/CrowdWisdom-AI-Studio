import React, { useState, useEffect } from 'react'
import {
  Clapperboard,
  Play,
  RotateCcw,
  Download,
  Film,
  Sparkles,
  Layers,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Monitor,
  Smartphone,
  Square,
  Trash2,
} from 'lucide-react'
import { videosApi, scriptsApi, campaignsApi } from '@/lib/api'
import { VideoJob, Script, Campaign, VideoAspectRatio } from '@/types'
import { wsManager } from '@/lib/websocket'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { getStatusColor, formatRelativeTime, resolveMediaUrl } from '@/lib/utils'
import { CrowdWisdomLogo } from '@/components/branding'
import toast from 'react-hot-toast'

export const VideoProductionPage: React.FC = () => {
  const [videoJobs, setVideoJobs] = useState<VideoJob[]>([])
  const [approvedScripts, setApprovedScripts] = useState<Script[]>([])
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [selectedScriptId, setSelectedScriptId] = useState<string>('')
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>('')
  const [aspectRatio, setAspectRatio] = useState<VideoAspectRatio>('9:16')
  const [duration, setDuration] = useState<number>(45)
  const [quality, setQuality] = useState<string>('high')
  const [isLoading, setIsLoading] = useState(true)
  const [isLaunching, setIsLaunching] = useState(false)

  // Active rendering preview state
  const [activeJob, setActiveJob] = useState<VideoJob | null>(null)

  useEffect(() => {
    loadData()

    // Subscribe to live video rendering progress
    const unsubProgress = wsManager.on('job_progress', (data: any) => {
      if (data.job_type === 'video_production') {
        setVideoJobs((prev) =>
          prev.map((job) =>
            job.id === data.job_id
              ? {
                  ...job,
                  status: data.status,
                  progress_percent: data.progress_percent,
                  current_stage: data.current_stage,
                }
              : job
          )
        )
      }
    })

    return () => {
      unsubProgress()
    }
  }, [])

  const loadData = async () => {
    setIsLoading(true)
    try {
      const [vidsRes, scriptsRes, campsRes] = await Promise.all([
        videosApi.list({ limit: 50 }),
        scriptsApi.list({ status: 'approved' as any }),
        campaignsApi.list(),
      ])
      setVideoJobs(vidsRes.data)
      setApprovedScripts(scriptsRes.data)
      setCampaigns(campsRes.data)

      if (vidsRes.data.length > 0) {
        setActiveJob(vidsRes.data[0])
      }
      if (scriptsRes.data.length > 0) {
        setSelectedScriptId(scriptsRes.data[0].id)
        setSelectedCampaignId(scriptsRes.data[0].campaign_id)
      }
    } catch (err) {
      toast.error('Failed to load video studio')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLaunchVideo = async () => {
    if (!selectedScriptId) {
      toast.error('Please select an approved script first.')
      return
    }

    const currentScript = approvedScripts.find((s) => s.id === selectedScriptId)
    const targetCampaignId = selectedCampaignId || currentScript?.campaign_id
    if (!targetCampaignId) {
      toast.error('Campaign associated with selected script could not be found.')
      return
    }

    const activeRunningJob = videoJobs.find(
      (j) => j.script_id === selectedScriptId && ['queued', 'processing', 'composing', 'rendering'].includes(j.status)
    )
    if (activeRunningJob) {
      toast.error('A rendering job is already actively processing for this script. Please wait for it to complete.')
      return
    }

    setIsLaunching(true)
    try {
      const res = await videosApi.generate({
        campaign_id: targetCampaignId,
        script_id: selectedScriptId,
        aspect_ratio: aspectRatio,
        duration_seconds: duration,
        quality: quality,
      })
      toast.success('Cinematic video production started! Compiling storyboard scenes...')
      const updatedList = await videosApi.list({ limit: 50 })
      setVideoJobs(updatedList.data)
      if (updatedList.data.length > 0) setActiveJob(updatedList.data[0])
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to dispatch video rendering')
    } finally {
      setIsLaunching(false)
    }
  }

  const handleRetryJob = async (jobId: string) => {
    try {
      await videosApi.retry(jobId)
      toast.success('Video rendering job retried!')
      const updatedList = await videosApi.list({ limit: 50 })
      setVideoJobs(updatedList.data)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to retry video job')
    }
  }

  const handleDeleteJob = async (jobId: string) => {
    try {
      await videosApi.delete(jobId)
      toast.success('Video job and associated files deleted.')
      const updatedList = await videosApi.list({ limit: 50 })
      setVideoJobs(updatedList.data)
      if (activeJob?.id === jobId) {
        setActiveJob(updatedList.data.length > 0 ? updatedList.data[0] : null)
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete video job')
    }
  }

  const handleClearFailedJobs = async () => {
    try {
      const res = await videosApi.clearFailed()
      toast.success(res.data.message || 'Cleared failed video jobs.')
      const updatedList = await videosApi.list({ limit: 50 })
      setVideoJobs(updatedList.data)
      if (activeJob && activeJob.status === 'failed') {
        setActiveJob(updatedList.data.length > 0 ? updatedList.data[0] : null)
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to clear failed jobs')
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#292E37]">
        <div className="flex items-center gap-4">
          <CrowdWisdomLogo variant="badge" size="sm" className="hidden sm:inline-flex shadow-sm" />
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-[#C5A46D] px-2 py-0.5 rounded bg-[#C5A46D]/10 border border-[#C5A46D]/20">
                Motion Engine
              </span>
              <span className="text-xs text-[#727B89] font-mono">• OpenMontage & MoviePy Rendering</span>
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
              <Clapperboard className="h-6 w-6 text-[#547DB8]" />
              Cinematic Video Production Studio
            </h1>
            <p className="text-xs text-[#A0A7B2] mt-0.5">
              Turn approved storyboards into professional MP4 video advertisements via OpenMontage & MoviePy.
            </p>
          </div>
        </div>
      </div>

      {/* Production Dispatcher Card */}
      <Card className="border-[#292E37] bg-[#15191F] p-5 space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-[#F2F3F5] flex items-center gap-2">
            <Film className="h-4 w-4 text-[#547DB8]" />
            Render Cinematic Commercial
          </h3>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            Select an approved storyboard. Video Agent will compose scenes, audio, and visual branding.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          {/* Approved Script Select */}
          <div className="space-y-1.5 md:col-span-2">
            <span className="font-semibold text-[#A0A7B2]">Select Approved Storyboard</span>
            {approvedScripts.length === 0 ? (
              <div className="p-2 border border-[#292E37] rounded-md bg-[#101216] text-[#727B89] text-[11px]">
                No approved scripts available. Approve a script in Script Studio first.
              </div>
            ) : (
              <select
                className="w-full bg-[#101216] border border-[#292E37] rounded-md px-3 py-2 text-xs font-medium text-[#F2F3F5] outline-none focus:border-[#547DB8]"
                value={selectedScriptId}
                onChange={(e) => {
                  setSelectedScriptId(e.target.value)
                  const script = approvedScripts.find((s) => s.id === e.target.value)
                  if (script) setSelectedCampaignId(script.campaign_id)
                }}
              >
                {approvedScripts.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.campaign_title || 'Untitled Script'} ({s.approach.replace('_', ' ')})
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Aspect Ratio */}
          <div className="space-y-1.5">
            <span className="font-semibold text-[#A0A7B2]">Aspect Ratio</span>
            <Select value={aspectRatio} onValueChange={(v) => setAspectRatio(v as VideoAspectRatio)}>
              <SelectTrigger className="bg-[#101216] border-[#292E37] text-[#F2F3F5]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#15191F] border-[#292E37] text-[#F2F3F5]">
                <SelectItem value="9:16">9:16 (Vertical Reels / TikTok)</SelectItem>
                <SelectItem value="16:9">16:9 (Landscape YouTube)</SelectItem>
                <SelectItem value="1:1">1:1 (Square Feed)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Render Action */}
          <div className="flex items-end">
            <Button
              variant="brand"
              size="sm"
              className="w-full text-xs h-9 bg-[#547DB8] hover:bg-[#436494] text-white font-medium disabled:opacity-50"
              disabled={!selectedScriptId || approvedScripts.length === 0 || isLaunching}
              onClick={handleLaunchVideo}
            >
              <Play className="h-3.5 w-3.5 mr-1.5" />
              {isLaunching ? 'Dispatching...' : 'Dispatch Video Agent'}
            </Button>
          </div>
        </div>
      </Card>

      {/* Main Studio View: Player & Progress + Video Library Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Video Monitor Player */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="border-[#292E37] overflow-hidden bg-[#15191F]">
            <CardHeader className="pb-3 border-b border-[#292E37] flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold text-[#F2F3F5] flex items-center gap-2">
                  <Monitor className="h-4 w-4 text-[#547DB8]" />
                  Commercial Preview Monitor
                </CardTitle>
                <CardDescription className="text-xs text-[#727B89] font-mono">
                  {activeJob ? `Job ID: ${activeJob.id}` : 'Select a video from the gallery below to preview'}
                </CardDescription>
              </div>

              {activeJob && (
                <div className="flex items-center gap-2">
                  <Badge className={getStatusColor(activeJob.status)}>
                    {activeJob.status}
                  </Badge>
                  <span className="text-xs font-mono text-[#A0A7B2]">
                    {activeJob.aspect_ratio}
                  </span>
                </div>
              )}
            </CardHeader>

            <CardContent className="p-4 bg-[#080A0F] flex items-center justify-center min-h-[400px] relative">
              {activeJob?.video_url ? (
                <div
                  className={`flex items-center justify-center relative rounded-xl overflow-hidden bg-black shadow-2xl border border-border/40 ${
                    activeJob.aspect_ratio === '16:9'
                      ? 'aspect-video w-full max-w-[620px]'
                      : activeJob.aspect_ratio === '1:1'
                      ? 'aspect-square w-full max-w-[420px]'
                      : 'aspect-[9/16] h-[520px] w-auto max-w-full'
                  }`}
                >
                  <video
                    key={activeJob.id}
                    controls
                    playsInline
                    preload="auto"
                    className="h-full w-full object-contain"
                  >
                    <source src={resolveMediaUrl(activeJob.video_url)} type="video/mp4" />
                    Your browser does not support HTML5 MP4 video.
                  </video>
                </div>
              ) : activeJob?.status === 'processing' ||
                activeJob?.status === 'composing' ||
                activeJob?.status === 'rendering' ? (
                <div className="text-center p-8 space-y-3">
                  <Clapperboard className="h-10 w-10 text-[#547DB8] mx-auto animate-pulse" />
                  <p className="text-xs font-mono text-[#F2F3F5] font-semibold">
                    Rendering in Progress: {activeJob.current_stage || 'Composing scenes...'}
                  </p>
                  <div className="w-64 mx-auto">
                    <Progress value={activeJob.progress_percent} />
                    <span className="text-[10px] text-[#A0A7B2] font-mono mt-1 block tabular-nums">
                      {activeJob.progress_percent}% Complete
                    </span>
                  </div>
                </div>
              ) : (
                <div className="text-center p-8 space-y-2 text-[#727B89]">
                  <Clapperboard className="h-10 w-10 mx-auto opacity-30" />
                  <p className="text-xs">No active video selected for preview.</p>
                </div>
              )}
            </CardContent>

            {activeJob && (
              <CardFooter className="p-4 border-t border-[#292E37] flex items-center justify-between bg-[#101216]">
                <div className="text-xs font-mono text-[#A0A7B2] tabular-nums">
                  Duration: {activeJob.duration_actual ? `${Math.round(activeJob.duration_actual)}s` : `${activeJob.duration_seconds}s`} • Size: {activeJob.file_size_mb || '1.2'} MB
                </div>
                <div className="flex items-center gap-2">
                  {activeJob.video_url && (
                    <a href={resolveMediaUrl(activeJob.video_url)} download={`crowdwisdom_${activeJob.id}.mp4`}>
                      <Button variant="outline" size="sm" className="text-xs border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5] hover:bg-[#1B2028]">
                        <Download className="h-3.5 w-3.5 mr-1.5" /> Download MP4 Commercial
                      </Button>
                    </a>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-xs text-[#D66C73] hover:text-[#D66C73] hover:bg-[#D66C73]/10 border-[#D66C73]/30"
                    onClick={() => handleDeleteJob(activeJob.id)}
                  >
                    <Trash2 className="h-3.5 w-3.5 mr-1.5" /> Delete
                  </Button>
                </div>
              </CardFooter>
            )}
          </Card>
        </div>

        {/* Right: Rendered Video Gallery */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-[#727B89] uppercase tracking-wider font-mono">
              Video Production Archive ({videoJobs.length})
            </h3>
            {videoJobs.some((j) => j.status === 'failed') && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-[10px] text-[#D66C73] hover:text-[#D66C73] hover:bg-[#D66C73]/10"
                onClick={handleClearFailedJobs}
              >
                <Trash2 className="h-2.5 w-2.5 mr-1" /> Clear Failed
              </Button>
            )}
          </div>

          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
            {videoJobs.length === 0 ? (
              <Card className="p-6 text-center border-dashed border-[#292E37] bg-[#15191F]">
                <Film className="h-6 w-6 text-[#727B89] mx-auto mb-1 opacity-50" />
                <p className="text-xs text-[#A0A7B2]">No videos produced yet.</p>
              </Card>
            ) : (
              videoJobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => setActiveJob(job)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    activeJob?.id === job.id
                      ? 'bg-[#1B2028] border-[#547DB8] shadow-md'
                      : 'bg-[#15191F] border-[#292E37] hover:bg-[#1B2028]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <Badge className={getStatusColor(job.status)}>{job.status}</Badge>
                    <span className="text-[10px] font-mono text-[#727B89]">
                      {job.aspect_ratio}
                    </span>
                  </div>

                  <p className="text-xs font-semibold text-[#F2F3F5] line-clamp-1">
                    Commercial #{job.id.slice(-6)}
                  </p>

                  <div className="flex items-center justify-between text-[10px] text-[#727B89] mt-2 font-mono">
                    <span>{formatRelativeTime(job.created_at)}</span>
                    <div className="flex items-center gap-1">
                      {job.status === 'failed' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-5 px-1.5 text-[10px] text-[#D9A94F] hover:bg-[#D9A94F]/10"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleRetryJob(job.id)
                          }}
                        >
                          <RotateCcw className="h-2.5 w-2.5 mr-1" /> Retry
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-5 px-1.5 text-[10px] text-[#727B89] hover:text-[#D66C73] hover:bg-[#D66C73]/10"
                        title="Delete video record and files"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteJob(job.id)
                        }}
                      >
                        <Trash2 className="h-2.5 w-2.5" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
