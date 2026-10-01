export type UserPlan = 'FREE' | 'PRO' | 'CREATOR'
export type UserRole = 'USER' | 'ADMIN'
export type ProjectStatus =
  | 'DRAFT'
  | 'SCRIPT_READY'
  | 'VOICEOVER_READY'
  | 'VISUALS_READY'
  | 'CAPTIONS_READY'
  | 'RENDERING'
  | 'COMPLETE'
  | 'FAILED'
export type RenderJobStatus = 'PENDING' | 'PROCESSING' | 'COMPLETE' | 'FAILED'
export type SubscriptionStatus = 'ACTIVE' | 'CANCELED' | 'PAST_DUE' | 'TRIALING'

export interface User {
  id: string
  email: string
  name: string | null
  image: string | null
  plan: UserPlan
  role: UserRole
  creditsRemaining: number
  creditsUsed: number
  stripeCustomerId: string | null
  stripeSubscriptionId: string | null
  createdAt: Date
  updatedAt: Date
}

export interface Project {
  id: string
  userId: string
  title: string | null
  scriptJson: ScriptJson
  status: ProjectStatus
  duration: number | null
  thumbnailUrl: string | null
  createdAt: Date
  updatedAt: Date
  completedAt: Date | null
}

export interface ScriptSegment {
  id: string
  orderIndex: number
  text: string
  visualKeywords: string[]
  durationEstimate: number | null
  voiceoverUrl: string | null
  voiceoverDuration: number | null
  visualUrl: string | null
  visualDuration: number | null
  visualProvider: string | null
  captionStart: number | null
  captionEnd: number | null
}

export interface ScriptJson {
  segments: ScriptSegment[]
  totalDurationEstimate: number
  topic: string
  tone?: string
  language: string
}

export interface Segment {
  id: string
  projectId: string
  orderIndex: number
  text: string
  visualKeywords: string[]
  durationEstimate: number | null
  voiceoverUrl: string | null
  voiceoverDuration: number | null
  visualUrl: string | null
  visualDuration: number | null
  visualProvider: string | null
  captionStart: number | null
  captionEnd: number | null
  createdAt: Date
  updatedAt: Date
}

export interface RenderJob {
  id: string
  projectId: string
  userId: string
  status: RenderJobStatus
  priority: number
  outputVideoUrl: string | null
  thumbnailUrl: string | null
  duration: number | null
  fileSize: bigint | null
  costIncurred: number
  errorMessage: string | null
  startedAt: Date | null
  completedAt: Date | null
  createdAt: Date
  updatedAt: Date
}

export interface Subscription {
  id: string
  userId: string
  stripeSubscriptionId: string
  stripePriceId: string
  stripeCurrentPeriodEnd: Date
  status: SubscriptionStatus
  cancelAtPeriodEnd: boolean
  createdAt: Date
  updatedAt: Date
}

export interface UsageLog {
  id: string
  userId: string
  action: string
  creditsCost: number
  metadata: Record<string, unknown> | null
  createdAt: Date
}

// API Request/Response Types
export interface GenerateScriptRequest {
  topic: string
  tone?: string
  lengthSeconds?: number
  language?: string
}

export interface GenerateScriptResponse {
  script: string
  segments: ScriptSegment[]
}

export interface GenerateVoiceoverRequest {
  projectId: string
  segments: VoiceoverSegmentRequest[]
  voiceSettings: VoiceSettings
}

export interface VoiceoverSegmentRequest {
  text: string
  voiceId: string
  pace: number
}

export interface VoiceSettings {
  defaultVoiceId: string
  defaultPace: number
}

export interface GenerateVoiceoverResponse {
  segmentAudioUrls: string[]
  totalDuration: number
  costEstimate: number
}

export interface VisualSearchRequest {
  projectId: string
  segments: VisualSegmentRequest[]
}

export interface VisualSegmentRequest {
  keywords: string[]
  duration: number
  styleTemplate: VisualStyleTemplate
}

export type VisualStyleTemplate = 'MINIMAL' | 'STOCK_MONTAGE' | 'AI_SCENES'

export interface VisualOption {
  providerUrl: string
  previewUrl: string
  duration: number
  cost: number
  provider: string
}

export interface VisualSearchResponse {
  segmentOptions: VisualOption[][]
}

export interface VisualSelectRequest {
  projectId: string
  selections: VisualSelection[]
}

export interface VisualSelection {
  segmentIndex: number
  providerUrl: string
}

export interface CaptionStyle {
  font: 'Inter' | 'Montserrat' | 'Bebas Neue' | 'Anton'
  fontSize: number
  color: string
  highlightColor: string
  strokeWidth: number
  strokeColor: string
  position: 'bottom' | 'center' | 'top'
  animation: 'none' | 'fade' | 'pop' | 'karaoke'
  maxLines: 1 | 2
}

export interface GenerateCaptionsRequest {
  projectId: string
  audioUrl: string
  style: CaptionStyle
}

export interface GenerateCaptionsResponse {
  srtContent: string
  wordTimestamps: WordTimestamp[]
  styleApplied: CaptionStyle
}

export interface WordTimestamp {
  word: string
  start: number
  end: number
  confidence: number
}

export interface ExportRequest {
  quality: '1080p'
  includeWatermark: boolean
}

export interface ExportResponse {
  downloadUrl: string
  expiresAt: Date
}

export interface RenderProgress {
  jobId: string
  progress: number
  stage: RenderStage
  message: string
}

export type RenderStage =
  | 'DOWNLOADING_ASSETS'
  | 'BUILDING_FILTER_GRAPH'
  | 'RENDERING_VIDEO'
  | 'UPLOADING_RESULT'
  | 'COMPLETE'
  | 'FAILED'

// Plan limits
export const PLAN_LIMITS: Record<UserPlan, { monthlyCredits: number; maxVideoLength: number; watermark: boolean }> = {
  FREE: { monthlyCredits: 3, maxVideoLength: 60, watermark: true },
  PRO: { monthlyCredits: 50, maxVideoLength: 90, watermark: false },
  CREATOR: { monthlyCredits: 200, maxVideoLength: 90, watermark: false },
}

// Cost estimates (USD)
export const COST_ESTIMATES = {
  scriptGeneration: 0.001,
  ttsPer1kChars: 0.18, // ElevenLabs
  ttsGooglePer1kChars: 0.016,
  stockVisual: 0,
  aiVisualPerClip: 0.25,
  whisperCaption: 0,
  ffmpegRender: 0.002,
  storagePerVideo: 0.001,
} as const

// Video specs
export const VIDEO_SPECS = {
  width: 1080,
  height: 1920,
  fps: 30,
  aspectRatio: '9:16',
  codec: 'libx264',
  preset: 'medium',
  crf: 23,
  audioCodec: 'aac',
  audioBitrate: '128k',
} as const