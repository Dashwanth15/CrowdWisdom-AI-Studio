"""
CrowdWisdom AI Studio — Pydantic Models
Complete data models for all MongoDB collections.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


# --- Helpers ---

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError(f"Invalid ObjectId: {v}")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)


# --- Enums ---

class UserRole(str, Enum):
    ADMIN = "admin"
    MARKETING_MANAGER = "marketing_manager"
    CREATIVE_EDITOR = "creative_editor"
    VIEWER = "viewer"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AgentType(str, Enum):
    ADS_MANAGER = "ads_manager"
    SCRIPT = "script"
    VIDEO_PRODUCTION = "video_production"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ScriptStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PRODUCTION = "in_production"
    FAILED = "failed"


class VideoJobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPOSING = "composing"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class ScriptApproach(str, Enum):
    PAIN_POINT = "pain_point"
    UNIQUE_DATA = "unique_data"
    PRODUCT_VALUE = "product_value"


class VideoAspectRatio(str, Enum):
    VERTICAL = "9:16"
    LANDSCAPE = "16:9"
    SQUARE = "1:1"


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


# --- User Models ---

class UserCreate(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    role: UserRole = UserRole.CREATIVE_EDITOR


class UserOut(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TargetCountry(str, Enum):
    INDIA = "IN"
    PHILIPPINES = "PH"
    BOTH = "BOTH"
    GLOBAL = "GLOBAL"


# --- Campaign Models ---

class AudienceConfig(BaseModel):
    segments: List[str] = ["retail_traders", "options_traders"]
    target_country: Optional[str] = "IN"
    target_region: Optional[str] = None
    age_range: Optional[str] = "25-55"
    interests: List[str] = ["trading", "investing", "market_analysis"]
    experience_level: Optional[str] = "all"
    preferred_language: Optional[str] = "en"
    trading_interests: Optional[List[str]] = None
    financial_education_interests: Optional[List[str]] = None
    marketing_channels: Optional[List[str]] = None
    custom_description: Optional[str] = None


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    target_country: Optional[str] = "IN"
    objective: str = "brand_awareness"
    audience: AudienceConfig = AudienceConfig()
    research_approaches: List[ScriptApproach] = [ScriptApproach.PAIN_POINT]
    video_duration_seconds: int = Field(default=45, ge=15, le=120)
    video_aspect_ratio: VideoAspectRatio = VideoAspectRatio.VERTICAL
    creative_direction: Optional[str] = None
    additional_instructions: Optional[str] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_country: Optional[str] = None
    objective: Optional[str] = None
    audience: Optional[AudienceConfig] = None
    status: Optional[CampaignStatus] = None
    research_approaches: Optional[List[ScriptApproach]] = None
    video_duration_seconds: Optional[int] = None
    video_aspect_ratio: Optional[VideoAspectRatio] = None
    creative_direction: Optional[str] = None
    additional_instructions: Optional[str] = None


class CampaignOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    target_country: Optional[str] = "IN"
    objective: str = "brand_awareness"
    status: Union[CampaignStatus, str] = CampaignStatus.DRAFT
    audience: Union[AudienceConfig, Dict[str, Any]] = Field(default_factory=dict)
    research_approaches: List[Union[ScriptApproach, str]] = Field(default_factory=list)
    video_duration_seconds: int = 45
    video_aspect_ratio: Union[VideoAspectRatio, str] = VideoAspectRatio.VERTICAL
    creative_direction: Optional[str] = None
    additional_instructions: Optional[str] = None
    owner_id: str = ""
    created_at: datetime
    updated_at: datetime
    # Stats
    ads_researched: int = 0
    scripts_generated: int = 0
    videos_generated: int = 0


# --- Advertisement Models ---

class AdEvaluationScore(BaseModel):
    overall: float = Field(default=8.0, ge=0, le=10)
    hook_strength: float = Field(default=8.0, ge=0, le=10)
    emotional_appeal: Optional[float] = Field(default=7.5, ge=0, le=10)
    clarity: Optional[float] = Field(default=8.0, ge=0, le=10)
    cta_effectiveness: Optional[float] = Field(default=7.5, ge=0, le=10)
    compliance_score: Optional[float] = Field(default=9.0, ge=0, le=10)
    emotional_resonance: Optional[float] = Field(default=8.0, ge=0, le=10)
    offer_clarity: Optional[float] = Field(default=8.0, ge=0, le=10)
    evidence_basis: Optional[str] = "ai_assessment"
    rationale: Optional[str] = "Evaluated by AI advertising analyst."


class AdvertisementOut(BaseModel):
    id: str
    campaign_id: str
    research_job_id: Optional[str] = ""
    ad_id: Optional[str] = ""
    source: Optional[str] = "meta_ads_library"
    advertiser: Optional[str] = "Unknown"
    ad_text: Optional[str] = None
    creative_reference: Optional[str] = None
    cta: Optional[str] = None
    creative_format: Optional[str] = "video"
    active_status: Optional[str] = "active"
    targeting_evidence: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = "meta_ads_library"
    is_benchmark: bool = False
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    published_at: Optional[datetime] = None
    published_at_raw: Optional[str] = None
    published_date_source: Optional[str] = None
    scraped_at: Optional[datetime] = None
    date_verification_status: str = "unverified"
    age_days: Optional[int] = None
    meta_ads_url: Optional[str] = None
    landing_page: Optional[str] = None
    target_audience_hypothesis: Optional[str] = None
    marketing_angle: Optional[str] = None
    pain_point: Optional[str] = None
    hook: Optional[str] = None
    observed_facts: Optional[List[str]] = Field(default_factory=list)
    ai_interpretation: Optional[Dict[str, Any]] = Field(default_factory=dict)
    evaluation_score: Optional[AdEvaluationScore] = None
    raw_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


# --- Script Models ---

class SceneSpec(BaseModel):
    scene_number: int = 1
    duration_seconds: float = 5.0
    visual_description: Optional[str] = "Cinematic visualization"
    visual_asset_path: Optional[str] = None
    visual_asset_url: Optional[str] = None
    visual_asset_status: str = "pending"
    visual_asset_provider: Optional[str] = None
    camera_direction: Optional[str] = "Slow push-in"
    camera_motion: Optional[str] = "slow_zoom_in"
    animation: Optional[str] = "animated_charts"
    voiceover: Optional[str] = ""
    on_screen_text: Optional[str] = ""
    audio_direction: Optional[str] = "Subtle ambient synthesizer"
    transition: Optional[str] = "cinematic_crossfade"
    asset_references: List[str] = []


class ScriptCreate(BaseModel):
    campaign_id: str
    approach: ScriptApproach
    custom_prompt: Optional[str] = None


class ScriptOut(BaseModel):
    id: str
    campaign_id: str
    approach: ScriptApproach
    status: ScriptStatus
    version: int
    # Creative content
    title: Optional[str] = None
    campaign_title: Optional[str] = None
    target_audience: Optional[Union[str, List[str]]] = None
    pain_point: Optional[str] = None
    marketing_angle: Optional[str] = None
    core_message: Optional[str] = None
    unique_selling_proposition: Optional[str] = None
    emotional_direction: Optional[str] = None
    visual_hook: Optional[str] = None
    full_script: Optional[str] = None
    scenes: List[SceneSpec] = []
    voiceover_full: Optional[str] = None
    on_screen_texts: List[str] = []
    music_direction: Optional[str] = None
    sound_effects: List[str] = []
    call_to_action: Optional[str] = None
    estimated_duration_seconds: Optional[int] = None
    research_references: List[str] = []
    supporting_evidence: List[str] = []
    # Approval
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# --- Video Job Models ---

class VideoJobCreate(BaseModel):
    campaign_id: Optional[str] = None
    script_id: str
    aspect_ratio: VideoAspectRatio = VideoAspectRatio.VERTICAL
    duration_seconds: int = Field(default=45, ge=15, le=120)
    quality: str = "high"


class VideoJobOut(BaseModel):
    id: str
    campaign_id: str
    script_id: str
    status: VideoJobStatus
    aspect_ratio: str
    duration_seconds: int
    quality: str
    progress_percent: int = 0
    current_stage: Optional[str]
    video_path: Optional[str]
    thumbnail_path: Optional[str]
    video_url: Optional[str]
    duration_actual: Optional[float]
    file_size_mb: Optional[float]
    error_message: Optional[str]
    production_log: List[str] = []
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


# --- Research Job Models ---

class ResearchJobCreate(BaseModel):
    campaign_id: str
    keywords: List[str] = ["trading", "investing", "market sentiment"]
    competitor_names: Optional[List[str]] = None
    date_range_days: int = Field(default=30, ge=1, le=365)


class ResearchJobOut(BaseModel):
    id: str
    campaign_id: str
    status: ExecutionStatus
    keywords: List[str]
    competitor_names: Optional[List[str]]
    date_range_days: int
    ads_found: int = 0
    ads_evaluated: int = 0
    insights_extracted: int = 0
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


# --- Agent Execution Models ---

class AgentExecutionOut(BaseModel):
    id: str
    campaign_id: str
    agent_type: Union[AgentType, str]
    task_name: str
    status: Union[ExecutionStatus, str]
    execution_mode: Optional[str] = "native_hermes"
    framework_version: Optional[str] = "NousResearch/hermes-agent@c55af2c9"
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    tool_calls: List[Dict[str, Any]] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


# --- Workflow Task Models ---

class WorkflowTaskOut(BaseModel):
    id: str
    campaign_id: str
    task_name: str
    description: Optional[str]
    agent_type: Optional[AgentType]
    status: TaskStatus
    priority: int = 0
    depends_on: List[str] = []
    execution_id: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


# --- Marketing Insight Models ---

class MarketingInsightOut(BaseModel):
    id: str
    campaign_id: str
    research_job_id: str
    category: str  # competitor_positioning | common_marketing_hooks | customer_pain_points | value_propositions | audience_objections | content_strategies | market_opportunities | gaps_in_messaging | pain_point | angle | hook | audience | competitor | pattern
    title: str
    description: str
    evidence: List[str] = []
    observed_evidence: List[str] = Field(default_factory=list)
    ai_interpretation: Optional[str] = None
    source_ad_ids: List[str] = []
    confidence: float = Field(..., ge=0, le=1)
    created_at: datetime


# --- Integration Models ---

class IntegrationStatus(str, Enum):
    CONFIGURED = "configured"
    UNCONFIGURED = "unconfigured"
    ERROR = "error"
    TESTING = "testing"


class IntegrationOut(BaseModel):
    id: str
    provider_name: str
    display_name: str
    category: str  # llm | research | video
    status: IntegrationStatus
    is_active: bool
    # Never return raw API keys — only masked versions
    api_key_configured: bool
    api_key_masked: Optional[str]
    model_name: Optional[str]
    extra_config: Optional[Dict[str, Any]]
    last_tested_at: Optional[datetime]
    test_result: Optional[str]
    updated_at: datetime


class IntegrationUpdate(BaseModel):
    api_key: Optional[str] = None  # Raw key — only sent backend→DB, never frontend←backend
    model_name: Optional[str] = None
    extra_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


# --- Media Asset Models ---

class AssetType(str, Enum):
    VIDEO = "video"
    THUMBNAIL = "thumbnail"
    IMAGE = "image"
    AUDIO = "audio"
    SCRIPT_JSON = "script_json"
    RESEARCH_JSON = "research_json"
    STORYBOARD = "storyboard"


class MediaAssetOut(BaseModel):
    id: str
    campaign_id: Optional[str]
    asset_type: AssetType
    filename: str
    file_path: str
    url: Optional[str]
    file_size_bytes: Optional[int]
    duration_seconds: Optional[float]
    width: Optional[int]
    height: Optional[int]
    mime_type: Optional[str]
    tags: List[str] = []
    created_at: datetime


# --- Notification Models ---

class NotificationOut(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    category: str
    is_read: bool
    action_url: Optional[str]
    created_at: datetime


# --- Dashboard Stats ---

class DashboardStats(BaseModel):
    total_campaigns: int
    active_campaigns: int
    ads_researched: int
    insights_generated: int
    scripts_generated: int
    scripts_pending_approval: int
    videos_generated: int
    videos_in_progress: int
    agent_success_rate: float
    recent_activity: List[Dict[str, Any]]


# --- Market Intelligence Models ---

class CountryOverviewOut(BaseModel):
    country_code: str
    country_name: str
    currency: Dict[str, Any]
    timezone: str
    market_hours: str
    market_ecosystem: Dict[str, Any]
    regulator: str
    key_segments_count: int
    dominant_languages: Dict[str, Any]
    research_freshness: str
    updated_at: str


class AudienceSegmentOut(BaseModel):
    segment_id: str
    name: str
    experience_level: str
    typical_age: str
    primary_focus: List[str]
    pain_points: List[str]
    content_preferences: str
    preferred_languages: List[str]
    dominant_channels: List[str]


class MarketEvidenceOut(BaseModel):
    id: Optional[str] = None
    country: str
    topic: str
    finding: str
    source_url: str
    publisher: str
    publication_date: Optional[str] = None
    retrieval_date: str
    confidence_level: str
    confidence_score: float
    evidence_type: str
    relevant_audience_segment: Optional[str] = None
    is_verified_fact: bool = True
    discovery_provider: Optional[str] = None


class MarketResearchRequest(BaseModel):
    country_code: str = "IN"
    topic: str = "retail trading sentiment"
    force_refresh: bool = False


class ComplianceValidationRequest(BaseModel):
    country_code: str = "IN"
    text_content: str
    content_type: str = "script"


class ComplianceValidationOut(BaseModel):
    country_code: str
    regulator: str
    compliance_score: float
    is_compliant: bool
    requires_human_review: bool
    violations: List[Dict[str, str]]
    warnings: List[Dict[str, str]]
    mandatory_disclaimers: List[str]
    required_labeling: str


