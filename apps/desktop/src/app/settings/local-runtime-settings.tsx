import { useCallback, useEffect, useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  downloadLocalRuntimeCatalogModel,
  downloadLocalRuntimeModel,
  getLocalRuntime,
  getLocalRuntimeModels,
  importLocalRuntimeModel,
  installLocalRuntime,
  type LocalRuntimeBackend,
  type LocalRuntimeCatalogModel,
  type LocalRuntimeDoctor,
  type LocalRuntimeModel,
  startLocalRuntimeServer,
  stopLocalRuntimeServer
} from '@/hermes'
import { useI18n } from '@/i18n'
import { Cpu, Loader2 } from '@/lib/icons'
import { cn } from '@/lib/utils'

import { CONTROL_TEXT } from './constants'
import { SectionHeading } from './primitives'

const BACKENDS: readonly LocalRuntimeBackend[] = ['AUTO', 'CUDA', 'VULKAN', 'CPU']

function formatSize(size: number | undefined, unknownSize: string): string {
  if (!size || size <= 0) {
    return unknownSize
  }
  const units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
  let value = size
  let unit = 0
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024
    unit += 1
  }
  return `${value.toFixed(unit ? 1 : 0)} ${units[unit]}`
}

export function LocalRuntimeSettings() {
  const { t } = useI18n()
  const copy = t.settings.localRuntime
  const [doctor, setDoctor] = useState<LocalRuntimeDoctor | null>(null)
  const [models, setModels] = useState<LocalRuntimeModel[]>([])
  const [catalog, setCatalog] = useState<LocalRuntimeCatalogModel[]>([])
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
      setCatalog(nextModels.catalog || [])
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

  const downloadCatalogModel = (catalogModel: LocalRuntimeCatalogModel) =>
    run(`catalog:${catalogModel.id}`, async () => {
      const model = await downloadLocalRuntimeCatalogModel(catalogModel.id)
      setSelectedModel(model.id)
    })

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
      <SectionHeading icon={Cpu} title={copy.title} />
      <p className="mb-3 text-xs text-muted-foreground">{copy.description}</p>

      <div className="grid gap-2 rounded-lg border border-border/70 p-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-muted-foreground">{copy.backend}</span>
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
            {copy.installRuntime}
          </Button>
          <Button disabled={!!busy} onClick={() => void refresh()} size="sm" variant="ghost">
            {copy.refresh}
          </Button>
        </div>

        <div className="text-xs text-muted-foreground">
          {doctor?.runtime.installed
            ? copy.runtimeInstalled(doctor.runtime.version || copy.installed)
            : copy.runtimeNotInstalled}
          {doctor?.environment?.nvidia_present
            ? ` · ${copy.nvidiaPresent(String(doctor.environment.nvidia_name || 'GPU'))}`
            : ''}
          {doctor?.server?.ready
            ? ` · ${copy.servingModel(doctor.server.model_id || selectedModel || copy.modelFallback)}`
            : ''}
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
          {catalog.map(catalogModel => (
            <div className="grid gap-2 rounded-md border border-primary/30 bg-primary/5 p-3" key={catalogModel.id}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="grid gap-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-semibold">{catalogModel.name}</span>
                    {catalogModel.featured ? (
                      <span className="rounded bg-primary/15 px-1.5 py-0.5 text-[0.65rem] font-medium text-primary">
                        {copy.catalogDefault}
                      </span>
                    ) : null}
                  </div>
                  <span className="text-[0.7rem] text-muted-foreground">
                    {formatSize(catalogModel.size, copy.unknownSize)} · {catalogModel.license} ·{' '}
                    {catalogModel.source_type === 'ollama' ? 'Ollama' : 'Hugging Face'} · {catalogModel.repo_id}
                  </span>
                  <span className="text-[0.7rem] text-muted-foreground">
                    {copy.catalog[catalogModel.id]?.intendedUse || catalogModel.intended_use}
                  </span>
                  {catalogModel.requires_auth ? (
                    <span className="text-[0.7rem] text-amber-300">{copy.requiresHuggingFaceAuth}</span>
                  ) : null}
                  {catalogModel.resource_warning ? (
                    <span className="text-[0.7rem] text-amber-300">
                      {copy.catalog[catalogModel.id]?.resourceWarning || catalogModel.resource_warning}
                    </span>
                  ) : null}
                  {catalogModel.install_status === 'conflict' ? (
                    <span className="text-[0.7rem] text-destructive">{copy.catalogConflict}</span>
                  ) : null}
                </div>
                <Button
                  disabled={catalogModel.install_status !== 'downloadable' || !!busy}
                  onClick={() => void downloadCatalogModel(catalogModel)}
                  size="sm"
                  type="button"
                >
                  {busy === `catalog:${catalogModel.id}` && <Loader2 className="size-3.5 animate-spin" />}
                  {catalogModel.install_status === 'installed' ? copy.installed : copy.downloadVerified}
                </Button>
              </div>
            </div>
          ))}
          <div className="grid gap-1">
            <span className="text-xs font-medium">{copy.downloadTitle}</span>
            <span className="text-[0.7rem] text-muted-foreground">{copy.downloadDescription}</span>
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
                aria-label={copy.huggingFaceRepository}
                className="min-w-52 flex-1"
                disabled={!!busy}
                onChange={event => setDownloadRepo(event.target.value)}
                placeholder={copy.repositoryPlaceholder}
                value={downloadRepo}
              />
              <Input
                aria-label={copy.ggufFilename}
                className="min-w-60 flex-1"
                disabled={!!busy}
                onChange={event => setDownloadFilename(event.target.value)}
                placeholder="Model-Q4_K_M.gguf"
                value={downloadFilename}
              />
              <Input
                aria-label={copy.downloadedModelId}
                className="w-36"
                disabled={!!busy}
                onChange={event => setDownloadModelId(event.target.value)}
                placeholder={copy.modelIdOptional}
                value={downloadModelId}
              />
              <Button disabled={!downloadRepo.trim() || !downloadFilename.trim() || !!busy} size="sm" type="submit">
                {busy === 'download' && <Loader2 className="size-3.5 animate-spin" />}
                {copy.downloadGguf}
              </Button>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Input
                aria-label={copy.huggingFaceRevision}
                className="min-w-52 flex-1"
                disabled={!!busy}
                onChange={event => setDownloadRevision(event.target.value)}
                placeholder={copy.revisionOptional}
                value={downloadRevision}
              />
              <Input
                aria-label={copy.ggufChecksum}
                className="min-w-60 flex-1 font-mono"
                disabled={!!busy}
                onChange={event => setDownloadSha256(event.target.value)}
                placeholder={copy.checksumOptional}
                value={downloadSha256}
              />
            </div>
          </form>
          <div className="flex flex-wrap items-center gap-2">
            <Input
              className="min-w-60 flex-1"
              onChange={event => setModelPath(event.target.value)}
              placeholder={copy.modelPathPlaceholder}
              value={modelPath}
            />
            <Input
              className="w-36"
              onChange={event => setModelId(event.target.value)}
              placeholder={copy.modelIdOptional}
              value={modelId}
            />
            <Button disabled={!modelPath.trim() || !!busy} onClick={() => void importModel()} size="sm">
              {busy === 'import' && <Loader2 className="size-3.5 animate-spin" />}
              {copy.importGguf}
            </Button>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Select onValueChange={setSelectedModel} value={selectedModel}>
              <SelectTrigger className={cn('min-w-56', CONTROL_TEXT)}>
                <SelectValue placeholder={copy.selectLocalModel} />
              </SelectTrigger>
              <SelectContent>
                {models.map(model => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.id} · {formatSize(model.size, copy.unknownSize)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              className="w-24"
              onChange={event => setContextSize(event.target.value)}
              placeholder={copy.contextPlaceholder}
              value={contextSize}
            />
            <Input
              className="w-24"
              onChange={event => setGpuLayers(event.target.value)}
              placeholder={copy.gpuLayersPlaceholder}
              value={gpuLayers}
            />
            <Button disabled={!selectedModel || !!busy} onClick={() => void start()} size="sm">
              {busy === 'start' && <Loader2 className="size-3.5 animate-spin" />}
              {copy.loadStart}
            </Button>
            <Button
              disabled={!active || !!busy}
              onClick={() => void run('stop', stopLocalRuntimeServer)}
              size="sm"
              variant="text"
            >
              {busy === 'stop' && <Loader2 className="size-3.5 animate-spin" />}
              {copy.unloadStop}
            </Button>
          </div>
          {selected && <div className="font-mono text-[0.68rem] text-muted-foreground">{selected.path}</div>}
        </div>
        {error && <div className="text-xs text-destructive">{error}</div>}
      </div>
    </section>
  )
}
