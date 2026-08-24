import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router'

import { LogTail } from '@/components/chat/log-tail'
import { Button } from '@/components/ui/button'
import { SearchField } from '@/components/ui/search-field'
import { ResponsiveTabs } from '@/components/ui/tab-dropdown'
import {
  getComputerUseStatus,
  getCronJobs,
  getHermesConfigRecord,
  getLogs,
  getStatus,
  pauseCronJob,
  resumeCronJob,
  triggerCronJob
} from '@/hermes'
import {
  Activity,
  AlertTriangle,
  Box,
  Brain,
  Clock,
  Cpu,
  Eye,
  Globe,
  Info,
  Lock,
  MessageCircle,
  MessageCode,
  Mic,
  Network,
  RefreshCw,
  SlidersHorizontal,
  Terminal,
  Wrench,
  Zap
} from '@/lib/icons'
import { notify, notifyError } from '@/store/notifications'
import type { ComputerUseStatus, CronJob, StatusResponse } from '@/types/hermes'

import { MaintenancePanel } from '../command-center/maintenance'
import { useRouteEnumParam } from '../hooks/use-route-enum-param'
import { OverlayMain, OverlayNav, type OverlayNavGroup, OverlaySplitLayout } from '../overlays/overlay-split-layout'
import { OverlayView } from '../overlays/overlay-view'
import { CRON_ROUTE } from '../routes'
import { AboutSettings } from '../settings/about-settings'
import { ComputerSettings } from '../settings/computer-settings'
import { ConfigSettings } from '../settings/config-settings'
import { ProvidersSettings, type ProviderView } from '../settings/providers-settings'
import { SkillsView } from '../skills'

const PAGE_IDS = [
  'overview',
  'chat',
  'tasks',
  'models',
  'providers',
  'routing',
  'voice',
  'computer',
  'browser',
  'coding',
  'memory',
  'skills',
  'mcp',
  'automation',
  'permissions',
  'privacy',
  'logs',
  'developer',
  'about'
] as const

export type ControlCenterPage = (typeof PAGE_IDS)[number]

const PAGE_DEFINITIONS: readonly {
  description: string
  icon: typeof Activity
  id: ControlCenterPage
  label: string
}[] = [
  { description: 'Gateway health, runtime policy, and quick actions.', icon: Activity, id: 'overview', label: 'Overview' },
  { description: 'Conversation behavior and chat presentation.', icon: MessageCircle, id: 'chat', label: 'Chat' },
  { description: 'Task lifecycle, actions, and operational history.', icon: Clock, id: 'tasks', label: 'Tasks' },
  { description: 'Local model and active model settings.', icon: Box, id: 'models', label: 'Models' },
  { description: 'Provider accounts, credentials, and endpoints.', icon: Globe, id: 'providers', label: 'Providers' },
  { description: 'Route slots, locality, privacy, and fallbacks.', icon: SlidersHorizontal, id: 'routing', label: 'Routing' },
  { description: 'Speech recognition, wake word, and synthesis.', icon: Mic, id: 'voice', label: 'Voice' },
  { description: 'Managed Linux desktop-control readiness.', icon: Cpu, id: 'computer', label: 'Computer' },
  { description: 'Browser privacy and local URL policy.', icon: Globe, id: 'browser', label: 'Browser' },
  { description: 'OpenHands delegation and coding execution policy.', icon: MessageCode, id: 'coding', label: 'Coding' },
  { description: 'Memory, context compression, and recall.', icon: Brain, id: 'memory', label: 'Memory' },
  { description: 'Installed skills and enabled toolsets.', icon: Zap, id: 'skills', label: 'Skills' },
  { description: 'MCP servers and tool registration.', icon: Network, id: 'mcp', label: 'MCP' },
  { description: 'Scheduled jobs and recurring automation.', icon: Clock, id: 'automation', label: 'Automation' },
  { description: 'Approvals, host access, and command policy.', icon: Lock, id: 'permissions', label: 'Permissions' },
  { description: 'Privacy mode and secret-redaction policy.', icon: Eye, id: 'privacy', label: 'Privacy' },
  { description: 'Gateway and Desktop operational logs.', icon: Terminal, id: 'logs', label: 'Logs' },
  { description: 'Advanced runtime, delegation, and developer settings.', icon: Wrench, id: 'developer', label: 'Developer' },
  { description: 'Hafiye Desktop version and update status.', icon: Info, id: 'about', label: 'About' }
]

const CONFIG_SECTION_BY_PAGE: Partial<Record<ControlCenterPage, string>> = {
  browser: 'safety',
  chat: 'chat',
  coding: 'advanced',
  developer: 'advanced',
  memory: 'memory',
  models: 'model',
  permissions: 'safety',
  privacy: 'hafiye',
  routing: 'hafiye',
  voice: 'voice'
}

interface ControlCenterProps {
  onClose: () => void
  onConfigSaved?: () => void
  onMainModelChanged?: (provider: string, model: string) => void
}

export function ControlCenterView({ onClose, onConfigSaved, onMainModelChanged }: ControlCenterProps) {
  const navigate = useNavigate()
  const [page, setPage] = useRouteEnumParam('page', PAGE_IDS, 'overview')
  const [providerView, setProviderView] = useState<ProviderView>('accounts')
  const importInputRef = useRef<HTMLInputElement | null>(null)

  const navGroups = useMemo<OverlayNavGroup[]>(
    () =>
      PAGE_DEFINITIONS.map(definition => ({
        active: page === definition.id,
        icon: definition.icon,
        id: definition.id,
        label: definition.label,
        onSelect: () => setPage(definition.id)
      })),
    [page, setPage]
  )

  const definition = PAGE_DEFINITIONS.find(item => item.id === page) ?? PAGE_DEFINITIONS[0]

  return (
    <OverlayView closeLabel="Close Control Center" onClose={onClose}>
      <OverlaySplitLayout>
        <OverlayNav groups={navGroups} />
        <OverlayMain className="px-0 pb-0">
          <ControlCenterPageHeader description={definition.description} title={definition.label} />
          <div className="min-h-0 flex-1 overflow-hidden">
            <ControlCenterContent
              importInputRef={importInputRef}
              onClose={onClose}
              onConfigSaved={onConfigSaved}
              onMainModelChanged={onMainModelChanged}
              onOpenAutomation={() => navigate(CRON_ROUTE)}
              page={page}
              providerView={providerView}
              setPage={setPage}
              setProviderView={setProviderView}
            />
          </div>
        </OverlayMain>
      </OverlaySplitLayout>
    </OverlayView>
  )
}

function ControlCenterPageHeader({ description, title }: { description: string; title: string }) {
  return (
    <header className="mb-4 shrink-0 px-1 max-[47.5rem]:mb-2">
      <h1 className="text-xl font-semibold tracking-tight" data-testid="control-center-page-title">
        {title}
      </h1>
      <p className="mt-1 text-sm text-muted-foreground">{description}</p>
    </header>
  )
}

interface ControlCenterContentProps {
  importInputRef: React.RefObject<HTMLInputElement | null>
  onConfigSaved?: () => void
  onClose: () => void
  onMainModelChanged?: (provider: string, model: string) => void
  onOpenAutomation: () => void
  page: ControlCenterPage
  providerView: ProviderView
  setPage: (page: ControlCenterPage) => void
  setProviderView: (view: ProviderView) => void
}

function ControlCenterContent({
  importInputRef,
  onConfigSaved,
  onClose,
  onMainModelChanged,
  onOpenAutomation,
  page,
  providerView,
  setPage,
  setProviderView
}: ControlCenterContentProps) {
  const configSection = CONFIG_SECTION_BY_PAGE[page]

  if (page === 'overview') {
    return <OverviewPage onNavigate={setPage} />
  }

  if (page === 'tasks') {
    return (
      <div className="h-full min-h-0 overflow-y-auto pr-1">
        <MaintenancePanel />
      </div>
    )
  }

  if (page === 'providers') {
    return (
      <div className="h-full min-h-0 overflow-y-auto pr-1">
        <ProvidersSettings
          onClose={onClose}
          onConfigSaved={onConfigSaved}
          onMainModelChanged={onMainModelChanged}
          onViewChange={setProviderView}
          view={providerView}
        />
      </div>
    )
  }

  if (page === 'computer') {
    return (
      <div className="h-full min-h-0 overflow-y-auto pr-1">
        <ComputerSettings />
      </div>
    )
  }

  if (page === 'skills' || page === 'mcp') {
    return (
      <div className="h-full min-h-0 overflow-hidden pr-1">
        <SkillsView embedded initialMode={page === 'mcp' ? 'mcp' : 'skills'} key={page} />
      </div>
    )
  }

  if (page === 'automation') {
    return <AutomationPage onOpenScheduler={onOpenAutomation} />
  }

  if (page === 'logs') {
    return <LogsPage />
  }

  if (page === 'about') {
    return (
      <div className="h-full min-h-0 overflow-y-auto pr-1">
        <AboutSettings />
      </div>
    )
  }

  if (configSection) {
    return (
      <ConfigSettings
        activeSectionId={configSection}
        importInputRef={importInputRef}
        onConfigSaved={onConfigSaved}
        onMainModelChanged={onMainModelChanged}
      />
    )
  }

  return null
}

function OverviewPage({ onNavigate }: { onNavigate: (page: ControlCenterPage) => void }) {
  const [status, setStatus] = useState<null | StatusResponse>(null)
  const [computer, setComputer] = useState<ComputerUseStatus | null>(null)
  const [config, setConfig] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const [nextStatus, nextComputer, nextConfig] = await Promise.all([
        getStatus(),
        getComputerUseStatus(),
        getHermesConfigRecord()
      ])

      setStatus(nextStatus)
      setComputer(nextComputer)
      setConfig(nextConfig)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const privacyMode = configValue(config, 'hafiye.privacy_mode') || 'NORMAL'
  const executionPolicy = configValue(config, 'hafiye.execution_policy') || 'FULL_AUTONOMOUS'

  return (
    <div className="h-full min-h-0 overflow-y-auto pr-1">
      <div className="mb-4 flex items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">Live state from the connected Hafiye gateway.</p>
        <Button disabled={loading} onClick={() => void refresh()} size="sm" variant="text">
          <RefreshCw className={loading ? 'size-3.5 animate-spin' : 'size-3.5'} />
          Refresh
        </Button>
      </div>

      {error && (
        <div className="mb-4 flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
          <AlertTriangle className="mt-0.5 size-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        <OverviewCard
          detail={status ? `${status.version} · ${status.active_sessions} active sessions` : ''}
          label="Gateway"
          tone={status?.gateway_running ? 'good' : 'neutral'}
          value={status ? (status.gateway_running ? 'Running' : 'Stopped') : 'Checking…'}
        />
        <OverviewCard detail="Configured Hafiye route policy" label="Privacy mode" tone="neutral" value={privacyMode} />
        <OverviewCard detail="Host action policy" label="Execution policy" tone="neutral" value={executionPolicy} />
        <OverviewCard
          detail={computer?.backend ?? 'Managed computer-use-linux'}
          label="Computer control"
          tone={computer?.ready ? 'good' : 'neutral'}
          value={computer?.ready ? 'Ready' : computer ? 'Not ready' : 'Checking…'}
        />
      </div>

      <section className="mt-6">
        <h2 className="mb-2 text-sm font-medium">Quick access</h2>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {(['models', 'providers', 'routing', 'voice', 'computer', 'tasks'] as const).map(page => (
            <Button
              className="justify-start"
              key={page}
              onClick={() => onNavigate(page)}
              size="sm"
              variant="outline"
            >
              {PAGE_DEFINITIONS.find(definition => definition.id === page)?.label}
            </Button>
          ))}
        </div>
      </section>
    </div>
  )
}

function OverviewCard({ detail, label, tone, value }: { detail: string; label: string; tone: 'good' | 'neutral'; value: string }) {
  return (
    <div className="rounded-xl border border-(--ui-stroke-secondary) bg-background/45 p-4">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <span className={tone === 'good' ? 'size-2 rounded-full bg-emerald-500' : 'size-2 rounded-full bg-foreground/25'} />
        {label}
      </div>
      <div className="mt-2 text-base font-medium">{value}</div>
      <div className="mt-1 truncate text-xs text-muted-foreground">{detail}</div>
    </div>
  )
}

function configValue(config: Record<string, unknown> | null, path: string): string {
  if (!config) {
    return ''
  }

  let value: unknown = config

  for (const segment of path.split('.')) {
    if (!value || typeof value !== 'object') {
      return ''
    }

    value = (value as Record<string, unknown>)[segment]
  }

  return value === null || value === undefined ? '' : String(value)
}

function AutomationPage({ onOpenScheduler }: { onOpenScheduler: () => void }) {
  const [jobs, setJobs] = useState<CronJob[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState('')

  const refresh = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      setJobs(await getCronJobs())
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const runJobAction = async (job: CronJob, action: 'pause' | 'resume' | 'trigger') => {
    setBusy(`${action}:${job.id}`)
    setError('')

    try {
      if (action === 'pause') {
        await pauseCronJob(job.id)
      } else if (action === 'resume') {
        await resumeCronJob(job.id)
      } else {
        await triggerCronJob(job.id)
      }

      await refresh()
      notify({ kind: 'success', title: `${job.name || job.id}: ${action}`, message: '' })
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
      notifyError(cause, `Could not ${action} automation`)
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="h-full min-h-0 overflow-y-auto pr-1">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-muted-foreground">These controls operate the persistent Hermes scheduler.</p>
        <div className="flex gap-2">
          <Button disabled={loading} onClick={() => void refresh()} size="sm" variant="text">
            <RefreshCw className={loading ? 'size-3.5 animate-spin' : 'size-3.5'} />
            Refresh
          </Button>
          <Button onClick={onOpenScheduler} size="sm">
            Open scheduler
          </Button>
        </div>
      </div>

      {error && <p className="mb-3 text-sm text-destructive">{error}</p>}
      {loading && jobs.length === 0 ? (
        <p className="text-sm text-muted-foreground">Loading scheduled jobs…</p>
      ) : jobs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-(--ui-stroke-secondary) p-5 text-sm text-muted-foreground">
          No scheduled jobs. Open the scheduler to create one.
        </div>
      ) : (
        <div className="grid gap-2">
          {jobs.map(job => {
            const action = job.enabled ? 'pause' : 'resume'
            const actionKey = `${action}:${job.id}`

            return (
              <div className="rounded-xl border border-(--ui-stroke-secondary) bg-background/45 p-3" key={job.id}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={job.enabled ? 'size-2 rounded-full bg-emerald-500' : 'size-2 rounded-full bg-foreground/25'} />
                      <span className="truncate text-sm font-medium">{job.name || job.id}</span>
                    </div>
                    <p className="mt-1 truncate text-xs text-muted-foreground">
                      {job.schedule_display || job.schedule?.display || job.schedule?.expr || 'No schedule'}
                      {job.model ? ` · ${job.model}` : ''}
                    </p>
                    {job.last_error && <p className="mt-1 truncate text-xs text-destructive">{job.last_error}</p>}
                  </div>
                  <div className="flex shrink-0 gap-1">
                    <Button
                      disabled={busy !== null}
                      onClick={() => void runJobAction(job, action)}
                      size="xs"
                      variant="text"
                    >
                      {busy === actionKey ? <RefreshCw className="size-3 animate-spin" /> : null}
                      {action === 'pause' ? 'Pause' : 'Resume'}
                    </Button>
                    <Button
                      disabled={busy !== null}
                      onClick={() => void runJobAction(job, 'trigger')}
                      size="xs"
                      variant="textStrong"
                    >
                      Run now
                    </Button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

const LOG_FILES = ['agent', 'errors', 'gateway', 'desktop'] as const
const LOG_LEVELS = ['ALL', 'INFO', 'WARNING', 'ERROR'] as const

function LogsPage() {
  const [file, setFile] = useState<(typeof LOG_FILES)[number]>('gateway')
  const [level, setLevel] = useState<(typeof LOG_LEVELS)[number]>('ALL')
  const [query, setQuery] = useState('')
  const [lines, setLines] = useState<string[] | null>(null)
  const [error, setError] = useState('')

  const refresh = useCallback(async () => {
    setError('')

    try {
      const response = await getLogs({ file, level, lines: 300 })
      setLines(response.lines)
    } catch (cause) {
      setLines([])
      setError(cause instanceof Error ? cause.message : String(cause))
    }
  }, [file, level])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const visibleLines = useMemo(() => {
    const needle = query.trim().toLowerCase()

    return needle ? (lines ?? []).filter(line => line.toLowerCase().includes(needle)) : lines
  }, [lines, query])

  return (
    <div className="flex h-full min-h-0 flex-col gap-3 pr-1">
      <div className="flex flex-wrap items-center gap-2">
        <ResponsiveTabs
          onChange={value => setFile(value as (typeof LOG_FILES)[number])}
          tabs={LOG_FILES.map(value => ({ id: value, label: value }))}
          value={file}
        />
        <ResponsiveTabs
          onChange={value => setLevel(value as (typeof LOG_LEVELS)[number])}
          tabs={LOG_LEVELS.map(value => ({ id: value, label: value.toLowerCase() }))}
          value={level}
        />
        <SearchField onChange={setQuery} placeholder="Filter logs…" value={query} />
        <Button className="ml-auto" onClick={() => void refresh()} size="sm" variant="text">
          <RefreshCw className="size-3.5" />
          Refresh
        </Button>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <LogTail
        className="min-h-0 flex-1 rounded-lg border border-(--ui-stroke-tertiary) bg-(--ui-bg-quinary)"
        emptyLabel="No log lines."
        lines={visibleLines}
      />
    </div>
  )
}

export { PAGE_IDS as CONTROL_CENTER_PAGE_IDS }
