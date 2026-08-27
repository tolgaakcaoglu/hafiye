import { hermesApi } from './client'

export type LocalRuntimeBackend = 'AUTO' | 'CPU' | 'CUDA' | 'VULKAN'

export interface LocalRuntimeModel {
  available?: boolean
  id: string
  name?: string
  path: string
  sha256?: string
  size?: number
  source?: string
  updated_at?: string
}

export interface LocalRuntimeCatalogModel {
  download_files: Array<{ filename: string; sha256: string; size: number; url: string }>
  featured: boolean
  filename: string
  id: string
  install_status: 'conflict' | 'downloadable' | 'installed'
  intended_use: string
  license: string
  name: string
  qualification: 'pending' | 'qualified'
  requires_auth: boolean
  repo_id: string
  resource_warning?: string
  revision: string
  sha256: string
  size: number
  source_url: string
  source_type: 'huggingface' | 'ollama'
}

export interface LocalRuntimeModelsResponse {
  catalog: LocalRuntimeCatalogModel[]
  models: LocalRuntimeModel[]
}

export interface LocalRuntimeServerHealth {
  endpoint?: string
  health_response?: unknown
  health_status?: number
  log_tail?: string[]
  memory?: Record<string, string>
  model_id?: string
  pid?: number
  port?: number
  ready: boolean
  requested_backend?: string
  running: boolean
  selected_backend?: string
}

export interface LocalRuntimeDoctor {
  blockers: string[]
  environment: Record<string, unknown>
  paths: Record<string, string>
  runtime: {
    installed: boolean
    manifest?: Record<string, unknown>
    version?: string
  }
  server: LocalRuntimeServerHealth
  warnings: string[]
}

export interface LocalRuntimeModelImportRequest {
  id?: string
  model_id?: string
  path: string
}

export interface LocalRuntimeModelDownloadRequest {
  filename: string
  model_id?: string
  repo_id: string
  revision?: string
  sha256?: string
}

export interface LocalRuntimeServerRequest {
  backend?: LocalRuntimeBackend
  context_size?: number
  gpu_layers?: number
  model_id: string
  port?: number
}

export function getLocalRuntime(): Promise<LocalRuntimeDoctor> {
  return hermesApi<LocalRuntimeDoctor>({ path: '/api/local-runtime' })
}

export function getLocalRuntimeModels(): Promise<LocalRuntimeModelsResponse> {
  return hermesApi<LocalRuntimeModelsResponse>({ path: '/api/local-runtime/models' })
}

export function installLocalRuntime(backend: LocalRuntimeBackend = 'AUTO', sourceRef = 'master') {
  return hermesApi<Record<string, unknown>>({
    path: '/api/local-runtime/install',
    method: 'POST',
    body: { backend, source_ref: sourceRef },
    // Building llama.cpp is an explicit first-run operation and can take many
    // minutes on a clean host. Keep the Desktop request alive for the same
    // bounded duration as the voice runtime installers.
    timeoutMs: 1_800_000
  })
}

export function importLocalRuntimeModel(body: LocalRuntimeModelImportRequest) {
  return hermesApi<LocalRuntimeModel>({
    path: '/api/local-runtime/models/import',
    method: 'POST',
    body
  })
}

export function downloadLocalRuntimeModel(body: LocalRuntimeModelDownloadRequest) {
  return hermesApi<LocalRuntimeModel>({
    path: '/api/local-runtime/models/download',
    method: 'POST',
    body,
    // Multi-gigabyte GGUF downloads legitimately take much longer than the
    // generic API timeout. The backend still streams to a resumable .part.
    timeoutMs: 21_600_000
  })
}

export function downloadLocalRuntimeCatalogModel(modelId: string) {
  return hermesApi<LocalRuntimeModel>({
    path: `/api/local-runtime/models/catalog/${encodeURIComponent(modelId)}/download`,
    method: 'POST',
    timeoutMs: 21_600_000
  })
}

export function deleteLocalRuntimeModel(modelId: string) {
  return hermesApi<{ id: string; ok: boolean }>({
    path: `/api/local-runtime/models/${encodeURIComponent(modelId)}`,
    method: 'DELETE'
  })
}

export function getLocalRuntimeServerHealth() {
  return hermesApi<LocalRuntimeServerHealth>({ path: '/api/local-runtime/server/health' })
}

export function startLocalRuntimeServer(body: LocalRuntimeServerRequest) {
  return hermesApi<LocalRuntimeServerHealth>({
    path: '/api/local-runtime/server/start',
    method: 'POST',
    body
  })
}

export function stopLocalRuntimeServer() {
  return hermesApi<{ ok: boolean; stopped: boolean }>({
    path: '/api/local-runtime/server/stop',
    method: 'POST'
  })
}

export function restartLocalRuntimeServer(body: LocalRuntimeServerRequest) {
  return hermesApi<LocalRuntimeServerHealth>({
    path: '/api/local-runtime/server/restart',
    method: 'POST',
    body
  })
}
