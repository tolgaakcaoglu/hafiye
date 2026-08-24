import { useCallback, useEffect, useMemo, useState } from 'react'

import { useGatewayRequest } from '@/app/gateway/hooks/use-gateway-request'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { onGatewayEvent } from '@/contrib/events'
import { AlertCircle, CheckCircle2, Clock, Loader2, StopFilled, Terminal } from '@/lib/icons'
import { notifyError } from '@/store/notifications'

export interface CodingTaskRecord {
  commands?: string[]
  completed_at?: number | null
  created_at?: number
  current_step_summary?: string
  error?: string
  file_changes?: string[]
  goal?: string
  model?: string
  privacy_mode?: string
  process_id?: string
  progress_events?: number
  provider?: string
  result_summary?: string
  route?: string
  started_at?: number | null
  state?: string
  task_id: string
  tool_history?: Array<{ at?: number; event?: string; source?: string; tool?: string }>
  updated_at?: number
}

interface TaskListResponse {
  tasks?: CodingTaskRecord[]
}

const ACTIVE_STATES = new Set(['QUEUED', 'PLANNING', 'RUNNING', 'WAITING', 'PAUSED', 'CANCELLING'])

function isTaskRecord(value: unknown): value is CodingTaskRecord {
  return typeof value === 'object' && value !== null && typeof (value as { task_id?: unknown }).task_id === 'string'
}

function formatElapsed(task: CodingTaskRecord): string {
  const start = task.started_at ?? task.created_at

  if (!start) {
    return '—'
  }

  const end = task.completed_at ?? Date.now() / 1000
  const seconds = Math.max(0, Math.round(end - start))

  if (seconds < 60) {
    return `${seconds}s`
  }

  const minutes = Math.floor(seconds / 60)

  return `${minutes}m ${seconds % 60}s`
}

function statusVariant(state: string): 'default' | 'destructive' | 'muted' | 'outline' | 'warn' {
  if (state === 'COMPLETED') {
    return 'default'
  }

  if (state === 'FAILED') {
    return 'destructive'
  }

  if (state === 'CANCELLING' || state === 'CANCELLED') {
    return 'warn'
  }

  return 'muted'
}

function statusIcon(state: string) {
  if (state === 'COMPLETED') {
    return CheckCircle2
  }

  if (state === 'FAILED') {
    return AlertCircle
  }

  if (ACTIVE_STATES.has(state)) {
    return Loader2
  }

  return Clock
}

export function TaskCenterPanel() {
  const { requestGateway } = useGatewayRequest()
  const [tasks, setTasks] = useState<CodingTaskRecord[]>([])
  const [error, setError] = useState('')

  const refresh = useCallback(async () => {
    try {
      const response = await requestGateway<TaskListResponse>('tasks.list')
      setTasks(Array.isArray(response.tasks) ? response.tasks.filter(isTaskRecord) : [])
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }, [requestGateway])

  useEffect(() => {
    void refresh()
    const timer = window.setInterval(() => void refresh(), 4000)

    return () => window.clearInterval(timer)
  }, [refresh])

  useEffect(() => {
    return onGatewayEvent('task.update', event => {
      const payload = event.payload

      if (!isTaskRecord(payload)) {
        return
      }

      setTasks(current => {
        const next = current.filter(task => task.task_id !== payload.task_id)
        const merged: CodingTaskRecord[] = [payload, ...next]

        return merged.sort(
          (left, right) => (right.created_at ?? 0) - (left.created_at ?? 0)
        )
      })
    })
  }, [])

  const activeCount = useMemo(
    () => tasks.filter(task => ACTIVE_STATES.has(task.state ?? '')).length,
    [tasks]
  )

  const cancel = useCallback(
    async (task: CodingTaskRecord) => {
      try {
        const response = await requestGateway<{ task?: CodingTaskRecord }>('tasks.cancel', {
          task_id: task.task_id
        })

        if (response.task && isTaskRecord(response.task)) {
          setTasks(current => [response.task!, ...current.filter(item => item.task_id !== task.task_id)])
        }
      } catch (err) {
        notifyError(err, 'Could not cancel coding task')
      }
    },
    [requestGateway]
  )

  return (
    <section className="border-b border-(--ui-stroke-tertiary) pb-4" data-testid="task-center">
      <div className="mb-2 flex items-center justify-between gap-2">
        <div>
          <div className="text-[0.625rem] font-medium uppercase tracking-[0.08em] text-(--ui-text-tertiary)">
            Coding tasks
          </div>
          <div className="mt-1 text-[length:var(--conversation-caption-font-size)] text-(--ui-text-tertiary)">
            {activeCount > 0 ? `${activeCount} active · live OpenHands progress` : 'OpenHands task history'}
          </div>
        </div>
        <Button onClick={() => void refresh()} size="xs" variant="text">
          Refresh
        </Button>
      </div>

      {error && (
        <div className="mb-2 flex items-center gap-1 text-[length:var(--conversation-caption-font-size)] text-destructive">
          <AlertCircle className="size-3.5" />
          {error}
        </div>
      )}

      {tasks.length === 0 ? (
        <div className="rounded-lg border border-dashed border-(--ui-stroke-tertiary) p-3 text-[length:var(--conversation-caption-font-size)] text-(--ui-text-tertiary)">
          No delegated coding tasks yet.
        </div>
      ) : (
        <div className="space-y-2">
          {tasks.map(task => (
            <TaskRow key={task.task_id} onCancel={() => void cancel(task)} task={task} />
          ))}
        </div>
      )}
    </section>
  )
}

function TaskRow({ onCancel, task }: { onCancel: () => void; task: CodingTaskRecord }) {
  const state = task.state ?? 'UNKNOWN'
  const Icon = statusIcon(state)
  const active = ACTIVE_STATES.has(state)
  const history = (task.tool_history ?? []).slice(-4)

  return (
    <article
      className="rounded-lg border border-(--ui-stroke-tertiary) bg-(--ui-bg-quinary) p-3"
      data-testid={`task-row-${task.task_id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Icon className={active && state !== 'CANCELLING' ? 'size-3.5 animate-spin' : 'size-3.5'} />
            <Badge size="xs" variant={statusVariant(state)}>
              {state}
            </Badge>
            <span className="text-[0.68rem] text-(--ui-text-tertiary)">{formatElapsed(task)}</span>
          </div>
          <div className="mt-2 whitespace-pre-wrap wrap-break-word text-[length:var(--conversation-text-font-size)] font-medium">
            {task.goal || task.task_id}
          </div>
        </div>
        {active && (
          <Button aria-label="Cancel coding task" onClick={onCancel} size="xs" variant="text">
            <StopFilled className="size-3" />
            Cancel
          </Button>
        )}
      </div>

      <div className="mt-2 text-[length:var(--conversation-caption-font-size)] text-(--ui-text-tertiary)">
        {task.current_step_summary || 'Waiting for worker status'}
      </div>

      <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[0.65rem] text-(--ui-text-tertiary)">
        <span>
          {task.provider || 'provider'} / {task.model || 'model'}
        </span>
        <span>{task.route || 'coding'}</span>
        <span>{task.privacy_mode || 'NORMAL'}</span>
        <span>{task.progress_events ?? 0} progress events</span>
      </div>

      {task.process_id && (
        <div className="mt-1 flex items-center gap-1 font-mono text-[0.62rem] text-(--ui-text-tertiary)">
          <Terminal className="size-3" />
          {task.process_id}
        </div>
      )}

      {task.commands && task.commands.length > 0 && (
        <div className="mt-2 border-t border-(--ui-stroke-tertiary) pt-2 text-[0.62rem] text-(--ui-text-tertiary)">
          <div className="mb-1 font-medium">Worker command</div>
          <div className="truncate font-mono">{task.commands[task.commands.length - 1]}</div>
        </div>
      )}

      {history.length > 0 && (
        <div className="mt-2 border-t border-(--ui-stroke-tertiary) pt-2 text-[0.62rem] text-(--ui-text-tertiary)">
          {history.map((event, index) => (
            <div key={`${event.at ?? index}-${index}`}>
              {event.event || 'OpenHands event'}{event.tool ? ` · ${event.tool}` : ''}
            </div>
          ))}
        </div>
      )}

      {task.file_changes && task.file_changes.length > 0 && (
        <div className="mt-2 border-t border-(--ui-stroke-tertiary) pt-2 text-[0.62rem] text-(--ui-text-tertiary)">
          <div className="mb-1 font-medium">Modified files</div>
          {task.file_changes.slice(0, 12).map(file => (
            <div className="truncate font-mono" key={file}>
              {file}
            </div>
          ))}
        </div>
      )}

      {task.result_summary && (
        <div className="mt-2 whitespace-pre-wrap wrap-break-word text-[0.68rem] text-(--ui-text-secondary)">
          {task.result_summary}
        </div>
      )}
      {task.error && <div className="mt-2 text-[0.68rem] text-destructive">{task.error}</div>}
    </article>
  )
}
