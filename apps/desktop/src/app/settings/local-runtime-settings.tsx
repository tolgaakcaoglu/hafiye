import { useCallback, useEffect, useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  downloadLocalRuntimeModel,
  getLocalRuntime,
  getLocalRuntimeModels,
  importLocalRuntimeModel,
  installLocalRuntime,
  type LocalRuntimeBackend,
  type LocalRuntimeDoctor,
  type LocalRuntimeModel,
  startLocalRuntimeServer,
  stopLocalRuntimeServer
} from '@/hermes'
import { Cpu, Loader2 } from '@/lib/icons'
import { cn } from '@/lib/utils'

import { CONTROL_TEXT } from './constants'
import { SectionHeading } from './primitives'

const BACKENDS: readonly LocalRuntimeBackend[] = ['AUTO', 'CUDA', 'VULKAN', 'CPU']

function formatSize(size?: number): string {
  if (!size || size <= 0) {
    return 'unknown size'
  }
  const units = ['B', 'MiB', 'GiB']
  let value = size
  let unit = 0
  while (value >= 1024 * 1024 && unit < units.length - 1) {
    value /= 1024
    unit += 1
  }
  return `${value.toFixed(unit ? 1 : 0)} ${units[unit]}`
}

export function LocalRuntimeSettings() {
  const [doctor, setDoctor] = useState<LocalRuntimeDoctor | null>(null)
  const [models, setModels] = useState<LocalRuntimeModel[]>([])
  const [selectedModel, setSelectedModel] = useState('')
  const [backend, setBackend] = useState<LocalRuntimeBackend>('AUTO')
  const [modelPath, setModelPath] = useState('')
  const [modelId, setModelId] = useState('')
  const [downloadRepo, setDownloadRepo] = useState('')
  const [downloadFilename, setDownloadFilename] = useState('')
  const [downloadModelId, setDownloadModelId] = useState('')
  const [downloadRevision, setDownloadRevision] = useState('')
  const [downloadSha256, setDownloadSha256] = useState('')
  const [contextSize, setContextSize] = useState('4096')
  const [gpuLayers, setGpuLayers] = useState('')
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')

  const refresh = useCallback(async () => {
    // Older test doubles/remote Desktop backends may not expose the P4 API
    // yet. The real backend always does; hiding this section is preferable to
    // presenting controls that cannot mutate state.
    if (typeof getLocalRuntime !== 'function' || typeof getLocalRuntimeModels !== 'function') {
      return
    }
    try {
      const [nextDoctor, nextModels] = await Promise.all([getLocalRuntime(), getLocalRuntimeModels()])
      setDoctor(nextDoctor)
      setModels(nextModels.models || [])
      setSelectedModel(current => current || nextModels.models?.[0]?.id || '')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const active = doctor?.server?.running ? doctor.server.model_id || '' : ''
  const selected = useMemo(() => models.find(model => model.id === selectedModel), [models, selectedModel])

  const run = useCallback(
    async (label: string, operation: () => Promise<unknown>) => {
      setBusy(label)
      setError('')
      try {
        await operation()
        await refresh()
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err))
      } finally {
        setBusy('')
      }
    },
    [refresh]
  )

  const install = () => run('install', () => installLocalRuntime(backend))

  const importModel = () => {
    if (!modelPath.trim()) {
      return
    }
    return run('import', () =>
      importLocalRuntimeModel({ path: modelPath.trim(), model_id: modelId.trim() || undefined })
    )
  }

  const downloadModel = () => {
    if (!downloadRepo.trim() || !downloadFilename.trim()) {
      return
    }

    return run('download', async () => {
      const model = await downloadLocalRuntimeModel({
        filename: downloadFilename.trim(),
        model_id: downloadModelId.trim() || undefined,
        repo_id: downloadRepo.trim(),
        revision: downloadRevision.trim() || undefined,
        sha256: downloadSha256.trim() || undefined
      })
      setSelectedModel(model.id)
    })
  }

  const start = () => {
    if (!selectedModel) {
      return
    }
    const parsedContext = Number.parseInt(contextSize, 10)
    const parsedLayers = gpuLayers.trim() ? Number.parseInt(gpuLayers, 10) : undefined
    return run('start', () =>
      startLocalRuntimeServer({
        backend,
        context_size: Number.isFinite(parsedContext) ? parsedContext : 4096,
        gpu_layers: parsedLayers,
        model_id: selectedModel
      })
    )
  }

  // The server API is a machine-level capability. If a connected backend is
  // older and does not answer it, don't render dead controls in Desktop.
  if (!doctor && !error) {
    return null
  }

  return (
    <section data-slot="local-runtime-settings">
      <SectionHeading icon={Cpu} title="Local GGUF Runtime" />
      <p className="mb-3 text-xs text-muted-foreground">
        Managed llama.cpp server, local GGUF models, and the selected compute backend.
      </p>

      <div className="grid gap-2 rounded-lg border border-border/70 p-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-muted-foreground">Backend</span>
          <Select onValueChange={value => setBackend(value as LocalRuntimeBackend)} value={backend}>
            <SelectTrigger className={cn('w-28', CONTROL_TEXT)}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {BACKENDS.map(value => (
                <SelectItem key={value} value={value}>
                  {value}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button disabled={!!busy} onClick={install} size="sm" variant="textStrong">
            {busy === 'install' && <Loader2 className="size-3.5 animate-spin" />}
            Install / rebuild runtime
          </Button>
          <Button disabled={!!busy} onClick={() => void refresh()} size="sm" variant="ghost">
            Refresh
          </Button>
        </div>

        <div className="text-xs text-muted-foreground">
          {doctor?.runtime.installed
            ? `llama-server ${doctor.runtime.version || 'installed'}`
            : 'llama-server is not installed'}
          {doctor?.environment?.nvidia_present
            ? ` · NVIDIA ${String(doctor.environment.nvidia_name || 'present')}`
            : ''}
          {doctor?.server?.ready ? ` · serving ${doctor.server.model_id || 'model'}` : ''}
        </div>

        {doctor?.warnings?.map(warning => (
          <div className="text-xs text-amber-300" key={warning}>
            {warning}
          </div>
        ))}
        {doctor?.blockers?.map(blocker => (
          <div className="text-xs text-destructive" key={blocker}>
            {blocker}
          </div>
        ))}

        <div className="mt-2 grid gap-3 border-t border-border/60 pt-3">
          <div className="grid gap-1">
            <span className="text-xs font-medium">Download a GGUF model</span>
            <span className="text-[0.7rem] text-muted-foreground">
              Downloads one GGUF from Hugging Face, verifies an optional checksum, and registers it for llama.cpp.
              Hafiye does not use an Ollama model directory as its local runtime.
            </span>
          </div>
          <form
            className="grid gap-2"
            onSubmit={event => {
              event.preventDefault()
              void downloadModel()
            }}
          >
            <div className="flex flex-wrap items-center gap-2">
              <Input
                aria-label="Hugging Face repository"
                className="min-w-52 flex-1"
                disabled={!!busy}
                onChange={event => setDownloadRepo(event.target.value)}
                placeholder="owner/repository"
                value={downloadRepo}
              />
              <Input
                aria-label="GGUF filename"
                className="min-w-60 flex-1"
                disabled={!!busy}
                onChange={event => setDownloadFilename(event.target.value)}
                placeholder="Model-Q4_K_M.gguf"
                value={downloadFilename}
              />
              <Input
                aria-label="Downloaded model ID"
                className="w-36"
                disabled={!!busy}
                onChange={event => setDownloadModelId(event.target.value)}
                placeholder="model id (optional)"
                value={downloadModelId}
              />
              <Button disabled={!downloadRepo.trim() || !downloadFilename.trim() || !!busy} size="sm" type="submit">
                {busy === 'download' && <Loader2 className="size-3.5 animate-spin" />}
                Download GGUF
              </Button>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Input
                aria-label="Hugging Face revision"
                className="min-w-52 flex-1"
                disabled={!!busy}
                onChange={event => setDownloadRevision(event.target.value)}
                placeholder="revision (optional; branch or commit)"
                value={downloadRevision}
              />
              <Input
                aria-label="GGUF SHA-256 checksum"
                className="min-w-60 flex-1 font-mono"
                disabled={!!busy}
                onChange={event => setDownloadSha256(event.target.value)}
                placeholder="SHA-256 (optional)"
                value={downloadSha256}
              />
            </div>
          </form>
          <div className="flex flex-wrap items-center gap-2">
            <Input
              className="min-w-60 flex-1"
              onChange={event => setModelPath(event.target.value)}
              placeholder="/path/to/model.gguf"
              value={modelPath}
            />
            <Input
              className="w-36"
              onChange={event => setModelId(event.target.value)}
              placeholder="model id (optional)"
              value={modelId}
            />
            <Button disabled={!modelPath.trim() || !!busy} onClick={() => void importModel()} size="sm">
              {busy === 'import' && <Loader2 className="size-3.5 animate-spin" />}
              Import GGUF
            </Button>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Select onValueChange={setSelectedModel} value={selectedModel}>
              <SelectTrigger className={cn('min-w-56', CONTROL_TEXT)}>
                <SelectValue placeholder="Select a local model" />
              </SelectTrigger>
              <SelectContent>
                {models.map(model => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.id} · {formatSize(model.size)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              className="w-24"
              onChange={event => setContextSize(event.target.value)}
              placeholder="context"
              value={contextSize}
            />
            <Input
              className="w-24"
              onChange={event => setGpuLayers(event.target.value)}
              placeholder="GPU layers"
              value={gpuLayers}
            />
            <Button disabled={!selectedModel || !!busy} onClick={() => void start()} size="sm">
              {busy === 'start' && <Loader2 className="size-3.5 animate-spin" />}
              Load / start
            </Button>
            <Button
              disabled={!active || !!busy}
              onClick={() => void run('stop', stopLocalRuntimeServer)}
              size="sm"
              variant="text"
            >
              {busy === 'stop' && <Loader2 className="size-3.5 animate-spin" />}
              Unload / stop
            </Button>
          </div>
          {selected && <div className="font-mono text-[0.68rem] text-muted-foreground">{selected.path}</div>}
        </div>
        {error && <div className="text-xs text-destructive">{error}</div>}
      </div>
    </section>
  )
}
