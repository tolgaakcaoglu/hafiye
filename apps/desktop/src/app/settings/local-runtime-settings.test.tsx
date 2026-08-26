import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  downloadLocalRuntimeModel: vi.fn(),
  getLocalRuntime: vi.fn(),
  getLocalRuntimeModels: vi.fn(),
  importLocalRuntimeModel: vi.fn(),
  installLocalRuntime: vi.fn(),
  startLocalRuntimeServer: vi.fn(),
  stopLocalRuntimeServer: vi.fn()
}))

vi.mock('@/hermes', () => ({
  downloadLocalRuntimeModel: mocks.downloadLocalRuntimeModel,
  getLocalRuntime: mocks.getLocalRuntime,
  getLocalRuntimeModels: mocks.getLocalRuntimeModels,
  importLocalRuntimeModel: mocks.importLocalRuntimeModel,
  installLocalRuntime: mocks.installLocalRuntime,
  startLocalRuntimeServer: mocks.startLocalRuntimeServer,
  stopLocalRuntimeServer: mocks.stopLocalRuntimeServer
}))

beforeEach(() => {
  mocks.getLocalRuntime.mockResolvedValue({
    blockers: [],
    environment: {},
    paths: {},
    runtime: { installed: true, version: 'test' },
    server: { ready: false, running: false },
    warnings: []
  })
  mocks.getLocalRuntimeModels.mockResolvedValue({ models: [] })
  mocks.downloadLocalRuntimeModel.mockResolvedValue({
    id: 'qwen3-test',
    path: '/managed/models/qwen3-test.gguf',
    size: 123
  })
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('LocalRuntimeSettings', () => {
  it('downloads a GGUF model through the managed runtime API', async () => {
    const { LocalRuntimeSettings } = await import('./local-runtime-settings')

    render(<LocalRuntimeSettings />)

    expect(await screen.findByText('Download a GGUF model')).toBeTruthy()
    const downloadButton = screen.getByRole('button', { name: 'Download GGUF' })
    expect((downloadButton as HTMLButtonElement).disabled).toBe(true)

    fireEvent.change(screen.getByRole('textbox', { name: 'Hugging Face repository' }), {
      target: { value: 'Qwen/Qwen3-GGUF' }
    })
    fireEvent.change(screen.getByRole('textbox', { name: 'GGUF filename' }), {
      target: { value: 'Qwen3-14B-Q4_K_M.gguf' }
    })
    fireEvent.change(screen.getByRole('textbox', { name: 'Downloaded model ID' }), {
      target: { value: 'qwen3-14b-q4_k_m' }
    })
    fireEvent.change(screen.getByRole('textbox', { name: 'Hugging Face revision' }), {
      target: { value: '530227a7d994db8eca5ab5ced2fb692b614357fd' }
    })
    fireEvent.change(screen.getByRole('textbox', { name: 'GGUF SHA-256 checksum' }), {
      target: { value: 'abc123' }
    })

    expect((downloadButton as HTMLButtonElement).disabled).toBe(false)
    fireEvent.click(downloadButton)

    await waitFor(() => {
      expect(mocks.downloadLocalRuntimeModel).toHaveBeenCalledWith({
        filename: 'Qwen3-14B-Q4_K_M.gguf',
        model_id: 'qwen3-14b-q4_k_m',
        repo_id: 'Qwen/Qwen3-GGUF',
        revision: '530227a7d994db8eca5ab5ced2fb692b614357fd',
        sha256: 'abc123'
      })
    })
  })
})
