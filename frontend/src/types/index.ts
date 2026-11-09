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

export type TargetCountry = 'IN' | 'PH' | 'BOTH' | 'GLOBAL'

export interface AudienceConfig {
  target_country?: TargetCountry
  target_region?: string
  experience_level?: string
  preferred_language?: string
  trading_interests?: string[]
  financial_education_interests?: string[]
  marketing_channels?: string[]
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
  target_country?: TargetCountry
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
  data_source?: string
  ad_classification?: 'LIVE_META_AD' | 'HISTORICAL_META_AD' | 'CACHED_AD' | 'VERIFIED_DOMAIN_BENCHMARK' | 'AI_GENERATED_HYPOTHESIS'
  is_benchmark?: boolean
  relevance_category?: 'DIRECT_COMPETITOR' | 'INDIRECT_COMPETITOR' | 'FINANCIAL_PLATFORM' | 'BROKER_OR_TRADING_PLATFORM' | 'FINANCIAL_EDUCATION' | 'UNRELATED_ADVERTISER' | 'UNKNOWN'
  relevance_explanation?: string
  is_competitor?: boolean
  country_evidence_type?: string
  country_evidence_details?: string
  country?: string
  advertiser: string
  headline?: string
  ad_text?: string
  creative_reference?: string
  cta?: string
  creative_format?: string
  active_status?: string
  targeting_evidence?: Record<string, any>
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
  observed_facts?: string[]
  ai_interpretation?: Record<string, any>
  evaluation_score?: AdEvaluationScore
  created_at: string
}

export interface MarketingInsight {
  id: string
  campaign_id: string
  research_job_id?: string
  category: 'competitor_positioning' | 'common_marketing_hooks' | 'customer_pain_points' | 'value_propositions' | 'audience_objections' | 'content_strategies' | 'market_opportunities' | 'gaps_in_messaging' | 'pain_point' | 'angle' | 'hook' | 'audience' | 'competitor' | 'pattern' | string
  title: string
  description: string
  evidence: string[]
  observed_evidence?: string[]
  ai_interpretation?: string
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

export interface MarketProfile {
  country_code: string
  country_name: string
  currency: string
  timezone?: string
  market_hours?: string
  market_ecosystem?: Record<string, any>
  regulator: string
  key_segments_count?: number
  dominant_languages?: Record<string, any>
  research_freshness?: string
  updated_at?: string
  [key: string]: any
}

export interface AudienceSegment {
  segment_id: string
  name: string
  experience_level: string
  typical_age: string
  primary_focus: string[]
  pain_points: string[]
  content_preferences: string
  preferred_languages: string[]
  dominant_channels: string[]
  [key: string]: any
}

export interface MarketEvidence {
  id?: string
  country: string
  topic: string
  finding: string
  source_url: string
  publisher: string
  publication_date?: string
  retrieval_date?: string
  confidence_level?: string
  confidence_score: number
  evidence_type?: string
  relevant_audience_segment?: string
  is_verified_fact?: boolean
  discovery_provider?: string
  [key: string]: any
}

export interface ComplianceValidationResult {
  country_code: string
  regulator: string
  compliance_score: number
  is_compliant: boolean
  requires_human_review: boolean
  violations: Array<Record<string, string>>
  warnings: Array<Record<string, string>>
  mandatory_disclaimers: string[]
  required_labeling: string
}
