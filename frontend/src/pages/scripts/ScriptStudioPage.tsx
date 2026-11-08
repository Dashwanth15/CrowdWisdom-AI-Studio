import React, { useState, useEffect } from 'react'
import {
  FileVideo,
  Play,
  Check,
  X,
  Edit3,
  Download,
  Sparkles,
  Clapperboard,
  Layers,
  Clock,
  Volume2,
  Tv,
  Camera,
  Save,
  Trash2,
  Film,
  CheckCircle2,
} from 'lucide-react'
import { scriptsApi, campaignsApi, agentsApi, videosApi } from '@/lib/api'
import { Script, Campaign, ScriptApproach, SceneSpec } from '@/types'
import { wsManager } from '@/lib/websocket'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { getStatusColor, formatRelativeTime, resolveMediaUrl } from '@/lib/utils'
import toast from 'react-hot-toast'

export const ScriptStudioPage: React.FC = () => {
  const [scripts, setScripts] = useState<Script[]>([])
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>('')
  const [selectedScript, setSelectedScript] = useState<Script | null>(null)
  const [activeApproach, setActiveApproach] = useState<ScriptApproach>('pain_point')
  const [customPrompt, setCustomPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isDispatchingVideo, setIsDispatchingVideo] = useState(false)

  // Scene edit state
  const [editingSceneIdx, setEditingSceneIdx] = useState<number | null>(null)
  const [editVisual, setEditVisual] = useState('')
  const [editVO, setEditVO] = useState('')
  const [editOnScreen, setEditOnScreen] = useState('')
  const [editDuration, setEditDuration] = useState(5)

  useEffect(() => {
    loadInitialData()
  }, [])

  // Auto-polling fallback whenever any script is generating or in production
  useEffect(() => {
    const hasActive = scripts.some(
      (s) => s.status === 'generating' || s.status === 'in_production'
    )
    if (!hasActive) return

    const timer = setInterval(async () => {
      try {
        const res = await scriptsApi.list({ limit: 50 })
        setScripts(res.data)
        if (selectedScript) {
          const matched = res.data.find((s: Script) => s.id === selectedScript.id)
          if (matched) setSelectedScript(matched)
        }
      } catch (e) {
        // Silent poll
      }
    }, 2500)

    return () => clearInterval(timer)
  }, [scripts, selectedScript])

  // WebSocket real-time subscription for immediate updates
  useEffect(() => {
    const refresh = async () => {
      try {
        const res = await scriptsApi.list({ limit: 50 })
        setScripts(res.data)
        if (selectedScript) {
          const matched = res.data.find((s: Script) => s.id === selectedScript.id)
          if (matched) setSelectedScript(matched)
        }
      } catch (e) {
        // Silent
      }
    }

    const unsubProgress = wsManager.on('job_progress', refresh)
    const unsubNotification = wsManager.on('notification', refresh)
    const unsubStatus = wsManager.on('agent_status', refresh)

    return () => {
      unsubProgress()
      unsubNotification()
      unsubStatus()
    }
  }, [selectedScript])

  const loadInitialData = async () => {
    setIsLoading(true)
    try {
      const [campsRes, scriptsRes] = await Promise.all([
        campaignsApi.list(),
        scriptsApi.list({ limit: 50 }),
      ])
      setCampaigns(campsRes.data)
      setScripts(scriptsRes.data)
      if (scriptsRes.data.length > 0) {
        setSelectedScript(scriptsRes.data[0])
      }
      if (campsRes.data.length > 0) {
        setSelectedCampaignId(campsRes.data[0].id)
      }
    } catch (err) {
      toast.error('Failed to load scripts')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDispatchToVideo = async (scriptId: string) => {
    if (!selectedScript || isDispatchingVideo) return
    setIsDispatchingVideo(true)
    try {
      await videosApi.generate({
        campaign_id: selectedScript.campaign_id,
        script_id: scriptId,
        aspect_ratio: '9:16',
        duration_seconds: selectedScript.estimated_duration_seconds || 45,
        quality: 'high',
      })
      toast.success('Video Production Agent dispatched! Rendering cinematic commercial...')
      const res = await scriptsApi.list({ limit: 50 })
      setScripts(res.data)
      const matched = res.data.find((s: Script) => s.id === scriptId)
      if (matched) setSelectedScript(matched)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to dispatch video agent')
    } finally {
      setIsDispatchingVideo(false)
    }
  }

  const handleGenerateScript = async () => {
    if (!selectedCampaignId) {
      toast.error('Please select a campaign first.')
      return
    }

    try {
      await agentsApi.generateScript({
        campaign_id: selectedCampaignId,
        approach: activeApproach,
        custom_prompt: customPrompt,
      })
      toast.success(`Script Agent dispatched for ${activeApproach.replace('_', ' ')} approach!`)
      setCustomPrompt('')
      // Refresh scripts
      const res = await scriptsApi.list({ limit: 50 })
      setScripts(res.data)
      if (res.data.length > 0) setSelectedScript(res.data[0])
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to generate script')
    }
  }

  const handleApprove = async (id: string) => {
    try {
      const res = await scriptsApi.approve(id)
      toast.success('Script approved! Human checkpoint 2 cleared. Ready for video rendering.')
      setSelectedScript(res.data)
      setScripts((prev) => prev.map((s) => (s.id === id ? res.data : s)))
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to approve script')
    }
  }

  const handleReject = async (id: string) => {
    const reason = prompt('Please enter the reason for script rejection:')
    if (!reason) return

    try {
      const res = await scriptsApi.reject(id, reason)
      toast.error('Script marked as rejected.')
      setSelectedScript(res.data)
      setScripts((prev) => prev.map((s) => (s.id === id ? res.data : s)))
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to reject script')
    }
  }

  const handleDeleteScript = async (id: string) => {
    try {
      await scriptsApi.delete(id)
      toast.success('Script deleted successfully.')
      const res = await scriptsApi.list({ limit: 50 })
      setScripts(res.data)
      if (selectedScript?.id === id) {
        setSelectedScript(res.data.length > 0 ? res.data[0] : null)
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete script')
    }
  }

  const handleClearFailedScripts = async () => {
    try {
      const res = await scriptsApi.clearFailed()
      toast.success(res.data.message || 'Cleared failed and rejected scripts.')
      const listRes = await scriptsApi.list({ limit: 50 })
      setScripts(listRes.data)
      if (selectedScript && (selectedScript.status === 'failed' || selectedScript.status === 'rejected')) {
        setSelectedScript(listRes.data.length > 0 ? listRes.data[0] : null)
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to clear failed scripts')
    }
  }

  const openSceneEdit = (idx: number, scene: SceneSpec) => {
    setEditingSceneIdx(idx)
    setEditVisual(scene.visual_description)
    setEditVO(scene.voiceover)
    setEditOnScreen(scene.on_screen_text)
    setEditDuration(scene.duration_seconds)
  }

  const saveSceneEdit = async () => {
    if (!selectedScript || editingSceneIdx === null) return

    const updatedScenes = [...selectedScript.scenes]
    updatedScenes[editingSceneIdx] = {
      ...updatedScenes[editingSceneIdx],
      visual_description: editVisual,
      voiceover: editVO,
      on_screen_text: editOnScreen,
      duration_seconds: Number(editDuration),
    }

    try {
      const res = await scriptsApi.update(selectedScript.id, {
        scenes: updatedScenes,
      })
      toast.success('Scene updated!')
      setSelectedScript(res.data)
      setScripts((prev) => prev.map((s) => (s.id === selectedScript.id ? res.data : s)))
      setEditingSceneIdx(null)
    } catch (err) {
      toast.error('Failed to update scene')
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[#292E37]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#C5A46D] px-2 py-0.5 rounded bg-[#C5A46D]/10 border border-[#C5A46D]/20">
              Editorial Studio
            </span>
            <span className="text-xs text-[#727B89] font-mono">• Checkpoint 2 Human-in-the-Loop</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-[#F2F3F5] flex items-center gap-2">
            <FileVideo className="h-6 w-6 text-[#547DB8]" />
            AI Script & Storyboard Studio
          </h1>
          <p className="text-xs text-[#A0A7B2] mt-0.5">
            Cinematic advertising concepts with scene-by-scene storyboard controls and human approval gates.
          </p>
        </div>
      </div>

      {/* Script Generation Dispatcher Card */}
      <Card className="border-[#292E37] bg-[#15191F] p-5 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="space-y-1">
            <h3 className="text-sm font-semibold text-[#F2F3F5] flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-[#C5A46D]" />
              Generate Cinematic Commercial Script
            </h3>
            <p className="text-xs text-[#A0A7B2]">
              Select one of the 3 strategic approaches for CrowdWisdomTrading.
            </p>
          </div>

          {campaigns.length > 0 && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-[#A0A7B2]">Target Campaign:</span>
              <select
                className="bg-[#101216] border border-[#292E37] rounded-md px-3 py-1.5 text-xs font-medium text-[#F2F3F5] outline-none focus:border-[#547DB8]"
                value={selectedCampaignId}
                onChange={(e) => setSelectedCampaignId(e.target.value)}
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

        {/* 3 Approach Tabs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div
            onClick={() => setActiveApproach('pain_point')}
            className={`p-3 rounded-lg border cursor-pointer transition-all ${
              activeApproach === 'pain_point'
                ? 'bg-[#1B2028] border-[#D9A94F] text-[#F2F3F5]'
                : 'bg-[#101216] border-[#292E37] text-[#A0A7B2] hover:bg-[#1B2028]'
            }`}
          >
            <span className="font-semibold text-xs block text-[#D9A94F]">Approach A: Pain-Point</span>
            <p className="text-[11px] mt-1 text-[#A0A7B2]">
              Focuses on retail trader frustrations: noise, conflicting analyst calls, and sentiment whiplash.
            </p>
          </div>

          <div
            onClick={() => setActiveApproach('unique_data')}
            className={`p-3 rounded-lg border cursor-pointer transition-all ${
              activeApproach === 'unique_data'
                ? 'bg-[#1B2028] border-[#547DB8] text-[#F2F3F5]'
                : 'bg-[#101216] border-[#292E37] text-[#A0A7B2] hover:bg-[#1B2028]'
            }`}
          >
            <span className="font-semibold text-xs block text-[#7898C4]">Approach B: Unique-Data</span>
            <p className="text-[11px] mt-1 text-[#A0A7B2]">
              Highlights proprietary CrowdPulse and 30-day crowd shifts from thousands of vetted traders.
            </p>
          </div>

          <div
            onClick={() => setActiveApproach('product_value')}
            className={`p-3 rounded-lg border cursor-pointer transition-all ${
              activeApproach === 'product_value'
                ? 'bg-[#1B2028] border-[#36B58F] text-[#F2F3F5]'
                : 'bg-[#101216] border-[#292E37] text-[#A0A7B2] hover:bg-[#1B2028]'
            }`}
          >
            <span className="font-semibold text-xs block text-[#36B58F]">Approach C: Product-Value</span>
            <p className="text-[11px] mt-1 text-[#A0A7B2]">
              Communicates objective decision-support through Weekly/Daily Wisdom consensus trade plans.
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          <Input
            placeholder="Optional creative direction (e.g. institutional financial intelligence with high contrast dark graphics)..."
            className="text-xs bg-[#101216] border-[#292E37] text-[#F2F3F5]"
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
          />
          <Button variant="brand" size="sm" onClick={handleGenerateScript} className="text-xs whitespace-nowrap bg-[#547DB8] hover:bg-[#436494] text-white font-medium">
            <Play className="h-3 w-3 mr-1.5" />
            Generate Concept
          </Button>
        </div>
      </Card>

      {/* Main Workspace: Left List + Right Storyboard Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Scripts List */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-[#727B89] uppercase tracking-wider font-mono">
              Generated Scripts ({scripts.length})
            </h3>
            {scripts.some((s) => s.status === 'failed' || s.status === 'rejected') && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-[10px] text-[#D66C73] hover:text-[#D66C73] hover:bg-[#D66C73]/10"
                onClick={handleClearFailedScripts}
              >
                <Trash2 className="h-2.5 w-2.5 mr-1" /> Clear Failed
              </Button>
            )}
          </div>
          <div className="space-y-2 max-h-[700px] overflow-y-auto pr-1">
            {scripts.map((sc) => (
              <div
                key={sc.id}
                onClick={() => setSelectedScript(sc)}
                className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                  selectedScript?.id === sc.id
                    ? 'bg-[#1B2028] border-[#547DB8] shadow-md'
                    : 'bg-[#15191F] border-[#292E37] hover:bg-[#1B2028]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <Badge className={getStatusColor(sc.status)}>{sc.status.replace('_', ' ')}</Badge>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] font-mono text-[#727B89] tabular-nums">v{sc.version}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-5 w-5 p-0 text-[#727B89] hover:text-[#D66C73] hover:bg-[#D66C73]/10"
                      title="Delete script storyboard"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteScript(sc.id)
                      }}
                    >
                      <Trash2 className="h-2.5 w-2.5" />
                    </Button>
                  </div>
                </div>
                <h4 className="text-xs font-semibold text-[#F2F3F5] line-clamp-1">
                  {sc.campaign_title || 'Untitled Script'}
                </h4>
                <p className="text-[11px] text-[#A0A7B2] mt-1 capitalize font-mono">
                  Approach: {sc.approach.replace('_', ' ')}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Detailed Storyboard & Scene Editor */}
        <div className="lg:col-span-2 space-y-4">
          {selectedScript ? (
            <Card className="border-[#292E37] bg-[#15191F]">
              <CardHeader className="pb-4 border-b border-[#292E37]">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(selectedScript.status)}>
                        {selectedScript.status.replace('_', ' ')}
                      </Badge>
                      <span className="px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono capitalize bg-[#10141C] text-[#8E9EB5] border border-[#232B38]">
                        {selectedScript.approach.replace('_', ' ')}
                      </span>
                      <span className="text-xs text-[#727B89] font-mono tabular-nums">
                        ~{selectedScript.estimated_duration_seconds || 45}s Duration
                      </span>
                    </div>
                    <CardTitle className="text-lg font-semibold mt-2 text-[#F2F3F5]">
                      {selectedScript.campaign_title}
                    </CardTitle>
                    <CardDescription className="text-xs mt-1 text-[#A0A7B2]">
                      {selectedScript.core_message}
                    </CardDescription>
                  </div>

                  {/* Human Approval Checkpoint Controls */}
                  <div className="flex items-center gap-2">
                    {selectedScript.status === 'approved' && (
                      <Button
                        variant="brand"
                        size="sm"
                        className="bg-[#547DB8] hover:bg-[#436494] text-xs h-8 text-white font-medium"
                        onClick={() => handleDispatchToVideo(selectedScript.id)}
                        disabled={isDispatchingVideo}
                      >
                        <Film className="h-3.5 w-3.5 mr-1" />
                        {isDispatchingVideo ? 'Dispatching...' : 'Dispatch to Video Agent'}
                      </Button>
                    )}

                    {selectedScript.status !== 'approved' && (
                      <Button
                        variant="brand"
                        size="sm"
                        className="bg-[#36B58F] hover:bg-[#2d9676] text-xs h-8 text-[#080A0F] font-semibold"
                        onClick={() => handleApprove(selectedScript.id)}
                      >
                        <Check className="h-3.5 w-3.5 mr-1" />
                        Approve Script
                      </Button>
                    )}

                    {selectedScript.status !== 'rejected' && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-xs h-8 text-[#D9A94F] hover:bg-[#D9A94F]/10 border-[#D9A94F]/30"
                        onClick={() => handleReject(selectedScript.id)}
                      >
                        <X className="h-3.5 w-3.5 mr-1" />
                        Reject
                      </Button>
                    )}

                    <a
                      href={scriptsApi.getExportUrl(selectedScript.id)}
                      download={`script_${selectedScript.id}.json`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Button variant="outline" size="sm" className="text-xs h-8 border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]">
                        <Download className="h-3.5 w-3.5 mr-1" />
                        Export JSON
                      </Button>
                    </a>

                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs h-8 text-[#D66C73] hover:text-[#D66C73] hover:bg-[#D66C73]/10 border-[#D66C73]/30"
                      onClick={() => handleDeleteScript(selectedScript.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5 mr-1" />
                      Delete
                    </Button>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="pt-4 space-y-5">
                {/* Visual Hook Display */}
                {selectedScript.visual_hook && (
                  <div className="p-3.5 rounded-lg bg-[#101216] border border-[#292E37] text-xs">
                    <span className="font-semibold text-[#7898C4] block mb-1">
                      Cinematic Opening Hook (0:00 - 0:04):
                    </span>
                    <p className="text-[#A0A7B2]">{selectedScript.visual_hook}</p>
                  </div>
                )}

                {/* Scene-by-Scene Timeline */}
                <div>
                  <h4 className="text-xs font-semibold text-[#F2F3F5] uppercase tracking-wider mb-3 font-mono">
                    Scene-by-Scene Storyboard Editor ({selectedScript.scenes?.length || 0} Scenes)
                  </h4>

                  {(!selectedScript.scenes || selectedScript.scenes.length === 0) ? (
                    <div className="p-8 rounded-xl border border-dashed border-[#D9A94F]/30 bg-[#D9A94F]/5 text-center space-y-3">
                      <Clapperboard className="h-8 w-8 text-[#D9A94F] mx-auto animate-pulse" />
                      <h5 className="font-semibold text-sm text-[#F2F3F5]">
                        {selectedScript.status === 'generating' ? 'Generating Script Concept & AI Visuals...' : 'No scenes found for this script'}
                      </h5>
                      <p className="text-xs text-[#A0A7B2] max-w-md mx-auto">
                        {selectedScript.status === 'generating'
                          ? 'NousResearch Hermes AIAgent is generating trader pain points, composing scenes, and rendering 9:16 vertical commercial visuals...'
                          : 'Try generating a new storyboard or regenerating this script.'}
                      </p>
                      {selectedScript.status === 'generating' && (
                        <div className="flex items-center justify-center gap-2 text-xs text-[#D9A94F] font-mono">
                          <Sparkles className="h-3.5 w-3.5 animate-spin" />
                          <span>Generating scenes and visual cues...</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {selectedScript.scenes.map((scene, idx) => (
                        <div
                          key={idx}
                          className="p-3.5 rounded-xl bg-[#101216] border border-[#292E37] text-xs space-y-3 hover:border-[#547DB8]/40 transition-colors"
                        >
                          <div className="flex items-center justify-between pb-2 border-b border-[#292E37]">
                            <div className="flex items-center gap-2 font-mono text-[11px]">
                              <span className="font-bold text-[#7898C4]">SCENE 0{scene.scene_number}</span>
                              <span className="text-[#727B89] tabular-nums">• {scene.duration_seconds}s</span>
                              {scene.visual_asset_status === 'completed' && (
                                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-[3px] text-[9px] font-mono text-[#D8DCE4] bg-[#10141C] border border-[#232B38]">
                                  <span className="w-1.5 h-1.5 rounded-full bg-[#36B58F] shadow-[0_0_5px_#36B58F]" /> VISUAL READY
                                </span>
                              )}
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 px-2 text-[10px] text-[#A0A7B2] hover:text-[#F2F3F5]"
                              onClick={() => openSceneEdit(idx, scene)}
                            >
                              <Edit3 className="h-3 w-3 mr-1" /> Edit Scene
                            </Button>
                          </div>

                          <div className="flex flex-col sm:flex-row gap-3 text-[11px]">
                            {/* Scene Visual Preview Image */}
                            {scene.visual_asset_url ? (
                              <div className="relative w-full sm:w-40 h-28 rounded-lg overflow-hidden border border-[#292E37] bg-[#080A0F] shrink-0 group">
                                <img
                                  src={resolveMediaUrl(scene.visual_asset_url)}
                                  alt={`Scene ${scene.scene_number}`}
                                  className="w-full h-full object-cover transition-transform group-hover:scale-105 duration-300"
                                />
                                <div className="absolute top-1 left-1">
                                  <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[8px] font-semibold bg-[#36B58F] text-[#080A0F] shadow">
                                    FLUX 9:16
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
                            ) : (
                              <div className="w-full sm:w-40 h-28 rounded-lg border border-dashed border-[#292E37] bg-[#080A0F] flex flex-col items-center justify-center text-[10px] text-[#727B89] p-2 shrink-0">
                                <Camera className="h-5 w-5 mb-1 text-[#727B89]" />
                                <span>Visual Stills Ready</span>
                              </div>
                            )}

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 flex-1 text-[11px]">
                              <div>
                                <span className="text-[#727B89] font-semibold flex items-center gap-1 mb-0.5 font-mono">
                                  <Camera className="h-3 w-3 text-[#547DB8]" /> Visual & Camera:
                                </span>
                                <p className="text-[#F2F3F5]/90">{scene.visual_description}</p>
                                <span className="text-[#727B89] text-[10px] block mt-1">
                                  Direction: {scene.camera_direction}
                                </span>
                              </div>

                              <div>
                                <span className="text-[#727B89] font-semibold flex items-center gap-1 mb-0.5 font-mono">
                                  <Volume2 className="h-3 w-3 text-[#C5A46D]" /> Voiceover:
                                </span>
                                <p className="text-[#C5A46D]">"{scene.voiceover}"</p>
                                {scene.on_screen_text && (
                                  <span className="text-[#7898C4] font-mono text-[10px] block mt-1">
                                    Text Overlay: {scene.on_screen_text}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Call to Action & Audio Direction */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-3 rounded-lg bg-[#101216] border border-[#292E37] text-xs">
                  <div>
                    <span className="font-semibold text-[#727B89] block text-[10px] uppercase font-mono">
                      Call to Action (Final 5s):
                    </span>
                    <p className="text-[#F2F3F5] font-medium mt-0.5">{selectedScript.call_to_action}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-[#727B89] block text-[10px] uppercase font-mono">
                      Music Direction:
                    </span>
                    <p className="text-[#A0A7B2] mt-0.5">{selectedScript.music_direction}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="p-12 text-center border-dashed border-[#292E37] bg-[#15191F]">
              <FileVideo className="h-8 w-8 text-[#727B89] mx-auto mb-2 opacity-50" />
              <p className="text-xs text-[#A0A7B2]">Select a script from the left list to review its storyboard.</p>
            </Card>
          )}
        </div>
      </div>

      {/* Scene Edit Dialog */}
      <Dialog open={editingSceneIdx !== null} onOpenChange={() => setEditingSceneIdx(null)}>
        <DialogContent className="max-w-lg bg-[#15191F] border-[#292E37]">
          <DialogHeader>
            <DialogTitle className="text-sm text-[#F2F3F5]">Edit Storyboard Scene 0{editingSceneIdx !== null ? editingSceneIdx + 1 : ''}</DialogTitle>
            <DialogDescription className="text-xs text-[#727B89]">
              Modify the narration, visual direction, and screen overlays for this scene.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3 py-3 text-xs">
            <div className="space-y-1">
              <span className="font-semibold text-[#A0A7B2]">Visual Description</span>
              <Textarea
                rows={3}
                className="bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                value={editVisual}
                onChange={(e) => setEditVisual(e.target.value)}
              />
            </div>

            <div className="space-y-1">
              <span className="font-semibold text-[#A0A7B2]">Voiceover Script</span>
              <Textarea
                rows={2}
                className="bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                value={editVO}
                onChange={(e) => setEditVO(e.target.value)}
              />
            </div>

            <div className="space-y-1">
              <span className="font-semibold text-[#A0A7B2]">On-Screen Text Overlay</span>
              <Input
                className="bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                value={editOnScreen}
                onChange={(e) => setEditOnScreen(e.target.value)}
              />
            </div>

            <div className="space-y-1">
              <span className="font-semibold text-[#A0A7B2]">Duration (seconds)</span>
              <Input
                type="number"
                min="2"
                max="20"
                className="bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                value={editDuration}
                onChange={(e) => setEditDuration(Number(e.target.value))}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" size="sm" className="border-[#292E37] text-[#A0A7B2] hover:text-[#F2F3F5]" onClick={() => setEditingSceneIdx(null)}>
              Cancel
            </Button>
            <Button variant="brand" size="sm" className="bg-[#547DB8] hover:bg-[#436494] text-white font-medium" onClick={saveSceneEdit}>
              <Save className="h-3.5 w-3.5 mr-1" /> Save Scene
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
