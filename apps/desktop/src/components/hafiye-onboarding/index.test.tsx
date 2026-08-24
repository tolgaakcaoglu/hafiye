// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { HafiyeOnboardingState } from '@/hermes'

const mocks = vi.hoisted(() => ({
  getHafiyeOnboarding: vi.fn(),
  updateHafiyeOnboarding: vi.fn(),
  getHafiyeOnboardingEnvironment: vi.fn(),
  getHafiyeOnboardingDoctor: vi.fn(),
  getLocalRuntime: vi.fn(),
  getLocalRuntimeModels: vi.fn(),
  getVoiceRuntime: vi.fn(),
  getHafiyeAutostartStatus: vi.fn(),
  getHermesConfigRecord: vi.fn(),
  saveHermesConfig: vi.fn(),
  completeHafiyeOnboarding: vi.fn()
}))

vi.mock('@/hermes', () => ({
  completeHafiyeOnboarding: mocks.completeHafiyeOnboarding,
  getHafiyeAutostartStatus: mocks.getHafiyeAutostartStatus,
  getHafiyeOnboarding: mocks.getHafiyeOnboarding,
  getHafiyeOnboardingDoctor: mocks.getHafiyeOnboardingDoctor,
  getHafiyeOnboardingEnvironment: mocks.getHafiyeOnboardingEnvironment,
  getHermesConfigRecord: mocks.getHermesConfigRecord,
  getLocalRuntime: mocks.getLocalRuntime,
  getLocalRuntimeModels: mocks.getLocalRuntimeModels,
  getVoiceRuntime: mocks.getVoiceRuntime,
  saveHermesConfig: mocks.saveHermesConfig,
  updateHafiyeOnboarding: mocks.updateHafiyeOnboarding
}))

vi.mock('@/lib/voice-input-device', () => ({
  getSelectedVoiceInputDeviceId: () => '',
  getVoiceInputStream: vi.fn(),
  listVoiceInputDevices: vi.fn(),
  requestVoiceInputPermission: vi.fn(),
  setSelectedVoiceInputDeviceId: vi.fn()
}))

vi.mock('@/lib/oneshot', () => ({ requestOneShot: vi.fn() }))

import { HafiyeOnboardingWizard } from './index'

const STEPS = [
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

function state(overrides: Partial<HafiyeOnboardingState> = {}): HafiyeOnboardingState {
  return {
    choices: {},
    completed: false,
    completed_steps: [],
    current_step: 'welcome',
    required: true,
    steps: [...STEPS],
    ...overrides
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.getHafiyeOnboarding.mockResolvedValue(state())
  mocks.getHafiyeOnboardingEnvironment.mockResolvedValue({
    audio: { wpctl: '/usr/bin/wpctl' },
    cpu: 'test CPU',
    cpu_count: 8,
    desktop: 'GNOME',
    gnome_version: 'GNOME Shell 46',
    kernel: '6.8.0-test',
    memory: { total: 16 * 1024 ** 3 },
    node: 'v22',
    platform: 'Linux',
    python: '3.12',
    session_type: 'wayland',
    wayland: true,
    x11: false
  })
  mocks.getHafiyeOnboardingDoctor.mockResolvedValue({
    autostart: { active: true, available: true, enabled: true, service: 'hafiye-gateway.service' },
    blockers: [],
    computer: { ready: true, readiness: {} },
    environment: { platform: 'Linux', wayland: true },
    local_runtime: { server: { ready: true } },
    ok: true,
    voice: { blockers: [], ok: true, piper: { ready: true }, whisper: { ready: true } }
  })
  mocks.updateHafiyeOnboarding.mockImplementation(async (body: Partial<HafiyeOnboardingState>) =>
    state({
      choices: body.choices ?? {},
      completed_steps: body.completed_steps ?? [],
      current_step: body.current_step ?? 'environment'
    })
  )
  mocks.getLocalRuntime.mockResolvedValue({
    blockers: [],
    environment: { cuda_build_available: true, expected_auto_backend: 'CUDA', vulkan_build_available: true },
    paths: {},
    runtime: { installed: true },
    server: { ready: true, running: true },
    warnings: []
  })
  mocks.getLocalRuntimeModels.mockResolvedValue({ models: [] })
  mocks.getVoiceRuntime.mockResolvedValue({ blockers: [], ok: true, piper: { ready: true }, whisper: { ready: true } })
  mocks.getHafiyeAutostartStatus.mockResolvedValue({
    active: true,
    available: true,
    enabled: true,
    service: 'hafiye-gateway.service'
  })
  mocks.getHermesConfigRecord.mockResolvedValue({
    hafiye: { privacy_mode: 'NORMAL', execution_policy: 'FULL_AUTONOMOUS' }
  })
  mocks.saveHermesConfig.mockResolvedValue({ ok: true })
})

afterEach(() => cleanup())

describe('Hafiye first-run onboarding wizard', () => {
  it('does not render in a development checkout when onboarding is not required', async () => {
    mocks.getHafiyeOnboarding.mockResolvedValue(state({ required: false }))

    render(<HafiyeOnboardingWizard />)

    await waitFor(() => expect(mocks.getHafiyeOnboarding).toHaveBeenCalled())
    expect(screen.queryByText('Hafiye’ye hoş geldiniz')).toBeNull()
  })

  it('renders the packaged welcome step and advances through the real environment probe', async () => {
    render(<HafiyeOnboardingWizard />)

    expect(await screen.findByText('Hafiye’ye hoş geldiniz')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Kuruluma başla' }))

    expect(await screen.findByText('Linux ortamını doğrula')).toBeTruthy()
    expect(await screen.findByText('6.8.0-test')).toBeTruthy()
    expect(mocks.getHafiyeOnboardingEnvironment).toHaveBeenCalledTimes(1)
  })

  it('does not advance when computer-use-linux readiness reports a blocker', async () => {
    mocks.getHafiyeOnboarding.mockResolvedValue(state({ current_step: 'computer' }))
    mocks.getHafiyeOnboardingDoctor.mockResolvedValue({
      autostart: { active: false, available: true, enabled: false, service: 'hafiye-gateway.service' },
      blockers: ['AT-SPI is unavailable'],
      computer: {
        blockers: ['AT-SPI is unavailable'],
        readiness: { can_build_accessibility_tree: false, can_query_windows: true },
        ready: false
      },
      environment: { platform: 'Linux', wayland: true },
      local_runtime: { server: { ready: false } },
      ok: false,
      voice: { blockers: [], ok: true }
    })

    render(<HafiyeOnboardingWizard />)

    expect(await screen.findByText('Masaüstü kontrolünü doğrula')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Doctor sonucunu doğrula' }))

    expect(await screen.findByText('AT-SPI is unavailable')).toBeTruthy()
    expect(mocks.updateHafiyeOnboarding).not.toHaveBeenCalled()
  })
})
