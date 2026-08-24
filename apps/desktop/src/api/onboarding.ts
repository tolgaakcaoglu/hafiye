import { hermesApi, STARTUP_REQUEST_TIMEOUT_MS } from './client'

export const HAFIYE_ONBOARDING_STEPS = [
  'welcome',
  'environment',
  'computer',
  'compute',
  'llama-runtime',
  'local-model',
  'local-server',
  'remote-provider',
  'gemini',
  'routing',
  'microphone',
  'whisper',
  'stt',
  'piper',
  'tts',
  'wake-word',
  'test-hafiye',
  'execution-policy',
  'autostart',
  'doctor'
] as const

export type HafiyeOnboardingStep = (typeof HAFIYE_ONBOARDING_STEPS)[number]
export type OnboardingChoiceValue = boolean | number | string

export interface HafiyeOnboardingState {
  choices: Record<string, OnboardingChoiceValue>
  completed: boolean
  completed_steps: HafiyeOnboardingStep[]
  current_step: HafiyeOnboardingStep
  package_root?: string
  required: boolean
  state_path?: string
  steps: HafiyeOnboardingStep[]
  updated_at?: string
}

export interface HafiyeEnvironmentProbe {
  architecture?: string
  audio?: Record<string, string>
  compute?: Record<string, unknown>
  cpu?: string
  cpu_count?: number
  desktop?: string
  gnome_version?: string
  kernel?: string
  memory?: Record<string, number>
  node?: string
  os_release?: string
  platform?: string
  python?: string
  session_type?: string
  wayland?: boolean
  x11?: boolean
  [key: string]: unknown
}

export interface HafiyeAutostartStatus {
  active: boolean
  available: boolean
  enabled: boolean
  message?: string
  service: string
  [key: string]: unknown
}

export interface VoiceRuntimeDoctor {
  blockers: string[]
  environment?: Record<string, unknown>
  ok: boolean
  piper?: Record<string, unknown>
  warnings?: string[]
  whisper?: Record<string, unknown>
  [key: string]: unknown
}

export interface HafiyeOnboardingDoctor {
  autostart: HafiyeAutostartStatus
  blockers: string[]
  computer: Record<string, unknown>
  environment: HafiyeEnvironmentProbe
  local_runtime: Record<string, unknown>
  ok: boolean
  voice: VoiceRuntimeDoctor
}

export function getHafiyeOnboarding(): Promise<HafiyeOnboardingState> {
  return hermesApi<HafiyeOnboardingState>({ path: '/api/hafiye/onboarding', timeoutMs: STARTUP_REQUEST_TIMEOUT_MS })
}

export function updateHafiyeOnboarding(body: {
  choices?: Record<string, OnboardingChoiceValue>
  completed_steps?: HafiyeOnboardingStep[]
  current_step?: HafiyeOnboardingStep
}): Promise<HafiyeOnboardingState> {
  return hermesApi<HafiyeOnboardingState>({
    path: '/api/hafiye/onboarding',
    method: 'PUT',
    body,
    timeoutMs: STARTUP_REQUEST_TIMEOUT_MS
  })
}

export function completeHafiyeOnboarding(): Promise<HafiyeOnboardingState> {
  return hermesApi<HafiyeOnboardingState>({
    path: '/api/hafiye/onboarding/complete',
    method: 'POST',
    timeoutMs: STARTUP_REQUEST_TIMEOUT_MS
  })
}

export function getHafiyeOnboardingEnvironment(): Promise<HafiyeEnvironmentProbe> {
  return hermesApi<HafiyeEnvironmentProbe>({ path: '/api/hafiye/onboarding/environment' })
}

export function getHafiyeAutostartStatus(): Promise<HafiyeAutostartStatus> {
  return hermesApi<HafiyeAutostartStatus>({ path: '/api/hafiye/onboarding/autostart' })
}

export function enableHafiyeAutostart(): Promise<HafiyeAutostartStatus> {
  return hermesApi<HafiyeAutostartStatus>({
    path: '/api/hafiye/onboarding/autostart',
    method: 'POST',
    timeoutMs: STARTUP_REQUEST_TIMEOUT_MS
  })
}

export function getHafiyeOnboardingDoctor(): Promise<HafiyeOnboardingDoctor> {
  return hermesApi<HafiyeOnboardingDoctor>({
    path: '/api/hafiye/onboarding/doctor',
    timeoutMs: STARTUP_REQUEST_TIMEOUT_MS
  })
}

export function getVoiceRuntime(): Promise<VoiceRuntimeDoctor> {
  return hermesApi<VoiceRuntimeDoctor>({ path: '/api/voice-runtime', timeoutMs: STARTUP_REQUEST_TIMEOUT_MS })
}

export function installWhisperRuntime(backend: 'AUTO' | 'CPU' | 'CUDA' | 'VULKAN' = 'AUTO', model = 'base') {
  return hermesApi<Record<string, unknown>>({
    path: '/api/voice-runtime/install-whisper',
    method: 'POST',
    body: { backend, model, source_ref: 'master' },
    timeoutMs: 1_800_000
  })
}

export function installPiperRuntime(voice = 'tr_TR-dfki-medium') {
  return hermesApi<Record<string, unknown>>({
    path: '/api/voice-runtime/install-piper',
    method: 'POST',
    body: { voice },
    timeoutMs: 1_800_000
  })
}
