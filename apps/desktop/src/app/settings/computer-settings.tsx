import { useCallback, useEffect, useState } from 'react'

import { Button } from '@/components/ui/button'
import { getComputerUseStatus } from '@/hermes'
import { AlertTriangle, Check, Loader2, RefreshCw } from '@/lib/icons'
import { notifyError } from '@/store/notifications'
import type { ComputerUseStatus } from '@/types/hermes'

import { Pill } from './primitives'

const REQUIRED_READINESS = [
  'can_register_mcp_tools',
  'can_build_accessibility_tree',
  'can_send_development_input',
  'can_query_windows'
] as const

export function ComputerSettings() {
  const [status, setStatus] = useState<ComputerUseStatus | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    setLoading(true)

    try {
      setStatus(await getComputerUseStatus())
    } catch (err) {
      notifyError(err, 'Could not read Computer status')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">Computer</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Linux desktop control is provided by Hafiye&apos;s managed computer-use-linux MCP server.
          </p>
        </div>
        <Button disabled={loading} onClick={() => void refresh()} size="sm" variant="text">
          {loading ? <Loader2 className="size-3.5 animate-spin" /> : <RefreshCw className="size-3.5" />}
          Recheck
        </Button>
      </div>

      {!status && loading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="size-4 animate-spin" />
          Checking Computer readiness…
        </div>
      ) : status ? (
        <div className="grid gap-4">
          <div className="rounded-xl border border-(--ui-stroke-secondary) bg-background/45 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm font-medium">{status.backend ?? 'Computer Use'}</p>
                <p className="mt-1 break-all text-xs text-muted-foreground">
                  {status.binary ?? 'Binary not found'}
                </p>
              </div>
              <Pill tone={status.ready === true ? 'primary' : 'muted'}>
                {status.ready === true ? <Check className="size-3" /> : <AlertTriangle className="size-3" />}
                {status.ready === true ? 'Ready' : 'Not ready'}
              </Pill>
            </div>
            <p className="mt-3 text-xs text-muted-foreground">
              MCP server: {status.mcp_server ?? 'not registered'}
              {status.source_commit ? ` · source ${status.source_commit.slice(0, 12)}` : ''}
            </p>
          </div>

          <div className="grid gap-2">
            {REQUIRED_READINESS.map(key => {
              const ready = status.readiness?.[key] === true

              return (
                <div className="flex items-center justify-between rounded-lg bg-background/55 p-3" key={key}>
                  <span className="text-sm">{key}</span>
                  <Pill tone={ready ? 'primary' : 'muted'}>
                    {ready ? <Check className="size-3" /> : <AlertTriangle className="size-3" />}
                    {ready ? 'true' : 'false'}
                  </Pill>
                </div>
              )
            })}
          </div>

          {status.blockers?.length ? (
            <div className="grid gap-1 text-xs text-muted-foreground">
              {status.blockers.map(blocker => (
                <p key={blocker}>
                  <AlertTriangle className="mr-1 inline size-3" />
                  {blocker}
                </p>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">
              Window enumeration, accessibility-tree access, and development input are available to the managed MCP provider.
            </p>
          )}

          {status.error && <p className="text-xs text-muted-foreground">{status.error}</p>}
        </div>
      ) : null}
    </div>
  )
}
