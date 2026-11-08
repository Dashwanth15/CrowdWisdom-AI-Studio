export interface User {
  id: string
  email: string
  username: string
  full_name?: string
  role?: 'admin' | 'marketing_manager' | 'creative_editor' | 'viewer'
  is_active?: boolean
  created_at?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface AudienceConfig {
  segments?: string[]
  age_range?: string
  interests?: string[]
  custom_description?: string
}

export type CampaignStatus = 'draft' | 'active' | 'paused' | 'completed' | 'archived'
export type ScriptApproach = 'pain_point' | 'unique_data' | 'product_value'
export type VideoAspectRatio = '9:16' | '16:9' | '1:1'

export interface Campaign {
  id: string
  name: string
  description?: string
  objective: string
  status: CampaignStatus
  audience?: AudienceConfig
  research_approaches?: ScriptApproach[]
  video_duration_seconds: number
  video_aspect_ratio: VideoAspectRatio
  creative_direction?: string
  additional_instructions?: string
  compliance_rules?: string[]
  owner_id?: string
  created_at: string
  updated_at?: string
  ads_researched: number
  scripts_generated: number
  videos_generated: number
}

export interface SceneSpec {
  scene_number: number
  duration_seconds: number
  visual_description: string
  visual_asset_path?: string
  visual_asset_url?: string
  visual_asset_status?: 'pending' | 'generating' | 'completed' | 'failed'
  visual_asset_provider?: string
  camera_direction: string
  camera_motion?: string
  animation?: string
  voiceover: string
  on_screen_text: string
  audio_direction?: string
  transition?: string
  asset_references?: string[]
}

export type ScriptStatus = 'draft' | 'generating' | 'pending_approval' | 'approved' | 'rejected' | 'in_production' | 'failed'

export interface CreativeBrief {
  id: string
  campaign_id: string
  research_job_id?: string
  status: 'pending_approval' | 'approved' | 'rejected'
  version: number
  content: {
    title?: string
    executive_summary?: string
    target_audience_deep_dive?: {
      primary_persona?: string
      psychological_state?: string
      core_desire?: string
    }
    creative_angles?: Array<{
      angle_id: string
      name: string
      hook: string
      visual_metaphor: string
      emotional_arc: string
      narrative_theme: string
    }>
    compliance_guardrails?: string[]
    sound_and_tone_direction?: string
    [key: string]: any
  }
  approved_by?: string
  approved_at?: string
  created_at: string
  updated_at?: string
}

export interface Script {
  id: string
  campaign_id: string
  approach: ScriptApproach
  status: ScriptStatus
  version: number
  title?: string
  campaign_title?: string
  target_audience?: string
  pain_point?: string
  marketing_angle?: string
  core_message?: string
  unique_selling_proposition?: string
  emotional_direction?: string
  visual_hook?: string
  full_script?: string
  scenes: SceneSpec[]
  voiceover_full?: string
  on_screen_texts?: string[]
  music_direction?: string
  sound_effects?: string[]
  call_to_action?: string
  estimated_duration_seconds?: number
  research_references?: string[]
  supporting_evidence?: string[]
  approved_by?: string
  approved_at?: string
  rejection_reason?: string
  created_at: string
  updated_at?: string
}

export type VideoJobStatus = 'queued' | 'processing' | 'composing' | 'rendering' | 'completed' | 'failed'

export interface VideoJob {
  id: string
  campaign_id: string
  script_id: string
  status: VideoJobStatus
  aspect_ratio: string
  duration_seconds: number
  quality: string
  progress_percent: number
  current_stage?: string
  video_path?: string
  thumbnail_path?: string
  video_url?: string
  duration_actual?: number
  file_size_mb?: number
  error_message?: string
  production_log?: string[]
  started_at?: string
  completed_at?: string
  created_at: string
}

export type ExecutionStatus = 'pending' | 'running' | 'awaiting_approval' | 'completed' | 'failed' | 'cancelled' | 'paused'
export type AgentType = 'ads_manager' | 'script' | 'video_production'

export interface AgentExecution {
  id: string
  campaign_id: string
  agent_type: AgentType
  task_name: string
  status: ExecutionStatus
  execution_mode?: 'native_hermes' | 'llm_fallback' | 'failed' | 'unconfigured' | string
  framework_version?: string
  input_data?: Record<string, any>
  output_data?: Record<string, any>
  error_message?: string
  duration_seconds?: number
  tool_calls?: Record<string, any>[]
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface ResearchJob {
  id: string
  campaign_id: string
  status: ExecutionStatus
  keywords: string[]
  competitor_names?: string[]
  date_range_days: number
  ads_found: number
  ads_evaluated: number
  insights_extracted: number
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface AdEvaluationScore {
  overall: number
  hook_strength: number
  emotional_appeal: number
  clarity: number
  cta_effectiveness: number
  evidence_basis: string
  rationale: string
}

export interface Advertisement {
  id: string
  campaign_id: string
  research_job_id?: string
  ad_id: string
  source: string
  advertiser: string
  ad_text?: string
  creative_reference?: string
  first_seen?: string
  last_seen?: string
  published_at?: string
  published_at_raw?: string
  published_date_source?: string
  scraped_at?: string
  date_verification_status?: 'verified' | 'unverified'
  age_days?: number
  meta_ads_url?: string
  landing_page?: string
  target_audience_hypothesis?: string
  marketing_angle?: string
  pain_point?: string
  hook?: string
  evaluation_score?: AdEvaluationScore
  created_at: string
}

export interface MarketingInsight {
  id: string
  campaign_id: string
  research_job_id?: string
  category: 'pain_point' | 'angle' | 'hook' | 'audience' | 'competitor' | 'pattern'
  title: string
  description: string
  evidence: string[]
  source_ad_ids?: string[]
  confidence: number
  created_at: string
}

export type TaskStatus = 'backlog' | 'pending' | 'running' | 'awaiting_approval' | 'completed' | 'failed'

export interface WorkflowTask {
  id: string
  campaign_id: string
  task_name: string
  description?: string
  agent_type?: AgentType
  status: TaskStatus
  priority: number
  depends_on?: string[]
  execution_id?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export type AssetType = 'video' | 'thumbnail' | 'image' | 'audio' | 'script_json' | 'research_json' | 'storyboard'

export interface MediaAsset {
  id: string
  campaign_id?: string
  asset_type: AssetType
  filename: string
  file_path?: string
  url?: string
  file_size_bytes?: number
  duration_seconds?: number
  width?: number
  height?: number
  mime_type?: string
  tags?: string[]
  created_at: string
}

export type IntegrationStatus = 'configured' | 'unconfigured' | 'error' | 'testing'

export interface Integration {
  id: string
  provider_name: string
  display_name: string
  category: 'llm' | 'research' | 'video'
  status: IntegrationStatus
  is_active: boolean
  api_key_configured: boolean
  api_key_masked?: string
  model_name?: string
  extra_config?: Record<string, any>
  last_tested_at?: string
  test_result?: string
  updated_at: string
}

export interface DashboardStats {
  total_campaigns: number
  active_campaigns: number
  ads_researched: number
  insights_generated: number
  scripts_generated: number
  scripts_pending_approval: number
  videos_generated: number
  videos_in_progress: number
  agent_success_rate: number
  recent_activity: Array<{
    id: string
    agent_type: string
    task_name: string
    status: string
    campaign_id: string
    created_at: string
  }>
}

export interface WSEvent {
  type: string
  message?: string
  job_id?: string
  job_type?: string
  campaign_id?: string
  status?: string
  progress_percent?: number
  current_stage?: string
  data?: any
  timestamp?: string
  [key: string]: any
}
