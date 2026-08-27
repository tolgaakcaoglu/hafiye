import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { I18nProvider } from '@/i18n'

const mocks = vi.hoisted(() => ({
  downloadLocalRuntimeCatalogModel: vi.fn(),
  downloadLocalRuntimeModel: vi.fn(),
  getLocalRuntime: vi.fn(),
  getLocalRuntimeModels: vi.fn(),
  importLocalRuntimeModel: vi.fn(),
  installLocalRuntime: vi.fn(),
  startLocalRuntimeServer: vi.fn(),
  stopLocalRuntimeServer: vi.fn()
}))

vi.mock('@/hermes', () => ({
  downloadLocalRuntimeCatalogModel: mocks.downloadLocalRuntimeCatalogModel,
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
  mocks.getLocalRuntimeModels.mockResolvedValue({ catalog: [], models: [] })
  mocks.downloadLocalRuntimeModel.mockResolvedValue({
    id: 'qwen3-test',
    path: '/managed/models/qwen3-test.gguf',
    size: 123
  })
  mocks.downloadLocalRuntimeCatalogModel.mockResolvedValue({
    id: 'qwen3.8-27b-ud-iq1_s',
    path: '/managed/models/qwen3.8-27b-ud-iq1_s.gguf',
    size: 6_192_222_208
  })
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

function catalogModel(overrides: Record<string, unknown> = {}) {
  return {
    download_files: [],
    featured: false,
    filename: 'model.gguf',
    id: 'catalog-model',
    install_status: 'downloadable',
    intended_use: 'Local model evaluation',
    license: 'Apache-2.0',
    name: 'Catalog model',
    qualification: 'pending',
    requires_auth: false,
    repo_id: 'owner/repository',
    resource_warning: 'Agent qualification is pending.',
    revision: 'pinned-revision',
    sha256: 'pinned-sha256',
    size: 6_192_222_208,
    source_url: 'https://models.example/catalog',
    source_type: 'huggingface',
    ...overrides
  }
}

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

  it('downloads the pinned production catalog model with integrity metadata', async () => {
    mocks.getLocalRuntimeModels.mockResolvedValue({
      catalog: [
        catalogModel({
          featured: true,
          filename: 'Qwen3.8-27B-UD-IQ1_S.gguf',
          id: 'qwen3.8-27b-ud-iq1_s',
          intended_use: 'General local-agent qualification candidate',
          name: 'Qwen3.8 27B UD-IQ1_S',
          repo_id: 'unsloth/Qwen3.8-27B-GGUF',
          revision: '4ca720788d1e01f1bff70c033e0d0028fd02e502',
          sha256: '3895b6eaa91e705c06ad1938d16c22e86f073c6a67df86260a1da79be3d1f887',
          source_url: 'https://huggingface.co/example'
        })
      ],
      models: []
    })

    const { LocalRuntimeSettings } = await import('./local-runtime-settings')
    render(<LocalRuntimeSettings />)

    expect(await screen.findByText(/5\.8 GiB/)).toBeTruthy()
    fireEvent.click(await screen.findByRole('button', { name: 'Download verified GGUF' }))

    await waitFor(() => {
      expect(mocks.downloadLocalRuntimeCatalogModel).toHaveBeenCalledWith('qwen3.8-27b-ud-iq1_s')
    })
  })

  it('shows and downloads the Ollama-source and gated security catalog entries by trusted ID', async () => {
    mocks.getLocalRuntimeModels.mockResolvedValue({
      catalog: [
        catalogModel({
          id: 'qwen3.8-27b-uncensored-q4_k_m',
          name: 'Qwen3.8 27B Uncensored Q4_K_M',
          repo_id: 'orcarouter/Qwen3.8-27B-Uncensored',
          source_type: 'ollama'
        }),
        catalogModel({
          id: 'qwen3.8-flash-next-uncensored-iq2_m',
          intended_use: 'Security researchers, red teams, and blue teams',
          name: 'Qwen3.8 Flash Next Uncensored IQ2_M',
          repo_id: 'orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF',
          requires_auth: true,
          size: 80_086_292_992
        })
      ],
      models: []
    })

    const { LocalRuntimeSettings } = await import('./local-runtime-settings')
    render(<LocalRuntimeSettings />)

    expect(await screen.findByText(/Ollama · orcarouter\/Qwen3\.8-27B-Uncensored/)).toBeTruthy()
    expect(screen.getByText('Security researchers, red teams, and blue teams')).toBeTruthy()
    expect(screen.getByText(/Requires approved Hugging Face access/)).toBeTruthy()

    const buttons = screen.getAllByRole('button', { name: 'Download verified GGUF' })
    fireEvent.click(buttons[0])
    await waitFor(() => {
      expect(mocks.downloadLocalRuntimeCatalogModel).toHaveBeenCalledWith('qwen3.8-27b-uncensored-q4_k_m')
    })
    fireEvent.click(screen.getAllByRole('button', { name: 'Download verified GGUF' })[1])
    await waitFor(() => {
      expect(mocks.downloadLocalRuntimeCatalogModel).toHaveBeenCalledWith('qwen3.8-flash-next-uncensored-iq2_m')
    })
  })

  it('renders the runtime controls and trusted catalog copy in Turkish', async () => {
    mocks.getLocalRuntime.mockResolvedValue({
      blockers: [],
      environment: { nvidia_name: 'GeForce RTX 3080', nvidia_present: true },
      paths: {},
      runtime: {
        installed: true,
        version: 'version: 0.2.0-dev (build 1, commit c060ca9) built with GNU 15.2.0 for Linux x86_64'
      },
      server: { model_id: 'qwen3.8-27b-ud-iq1_s', ready: true, running: true },
      warnings: []
    })
    mocks.getLocalRuntimeModels.mockResolvedValue({
      catalog: [
        catalogModel({
          featured: true,
          id: 'qwen3.8-27b-ud-iq1_s',
          intended_use: 'General local-agent qualification candidate',
          name: 'Qwen3.8 27B UD-IQ1_S'
        }),
        catalogModel({
          id: 'qwen3.8-flash-next-uncensored-iq2_m',
          intended_use: 'Security researchers, red teams, and blue teams',
          name: 'Qwen3.8 Flash Next Uncensored IQ2_M',
          requires_auth: true
        })
      ],
      models: []
    })

    const { LocalRuntimeSettings } = await import('./local-runtime-settings')
    render(
      <I18nProvider configClient={null} initialLocale="tr">
        <LocalRuntimeSettings />
      </I18nProvider>
    )

    expect(await screen.findByText('Yerel GGUF Çalışma Zamanı')).toBeTruthy()
    expect(screen.getByText('İşlem backend’i')).toBeTruthy()
    expect(screen.getByText(/llama-server sürüm: 0\.2\.0-dev \(derleme 1, commit c060ca9\)/)).toBeTruthy()
    expect(screen.getByText(/NVIDIA GeForce RTX 3080/)).toBeTruthy()
    expect(screen.queryByText(/built with/)).toBeNull()
    expect(screen.queryByText(/NVIDIA NVIDIA/)).toBeNull()
    expect(screen.getByRole('button', { name: 'Çalışma zamanını kur / yeniden derle' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Yenile' })).toBeTruthy()
    expect(screen.getByText('Hafiye katalog varsayılanı')).toBeTruthy()
    expect(screen.getByText('Genel yerel-agent yeterlilik adayı')).toBeTruthy()
    expect(screen.getByText('Güvenlik araştırmacıları, kırmızı takımlar ve mavi takımlar')).toBeTruthy()
    expect(screen.getByText(/Onaylı Hugging Face erişimi/)).toBeTruthy()
    expect(screen.getAllByRole('button', { name: 'Doğrulanmış GGUF’u indir' })).toHaveLength(2)
    expect(screen.getByText('GGUF modeli indir')).toBeTruthy()
    expect(screen.queryByText('Download verified GGUF')).toBeNull()
    expect(screen.queryByText('General local-agent qualification candidate')).toBeNull()
  })
})
