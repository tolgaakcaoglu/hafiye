import { useStore } from '@nanostores/react'
import { useEffect, useState } from 'react'

import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useI18n } from '@/i18n'
import {
  $quickEntry,
  canUseQuickEntry,
  loadQuickEntrySettings,
  QUICK_ENTRY_COMPOSER_MODES,
  QUICK_ENTRY_DEFAULT_SHORTCUT,
  saveQuickEntrySettings
} from '@/store/quick-entry'

import { ListRow, ToggleRow } from './primitives'

/**
 * Quick Entry — the global-hotkey mini composer's settings rows.
 *
 * The MAIN process is authoritative (it owns the OS accelerator), so this reads
 * the live registration state on mount and surfaces the failure the feature must
 * never swallow: a chord another app already owns comes back `registered: false`
 * with `error: 'taken'` and says so, right under the field.
 */
export function QuickEntrySettings() {
  const { t } = useI18n()
  const q = t.settings.quickEntry
  const state = useStore($quickEntry)
  // The field is a local draft: the accelerator is only committed on blur/Enter,
  // so a half-typed chord ("Alt+") never tears down the live registration.
  const [draft, setDraft] = useState<null | string>(null)

  useEffect(() => {
    void loadQuickEntrySettings()
  }, [])

  if (!canUseQuickEntry()) {
    return null
  }

  const commit = () => {
    const next = (draft ?? '').trim()
    setDraft(null)

    if (next && next !== state.shortcut) {
      void saveQuickEntrySettings({ shortcut: next })
    }
  }

  const status =
    state.registered === null
      ? null
      : state.error === 'taken'
        ? q.takenBy
        : state.error === 'invalid'
          ? q.invalidShortcut
          : state.enabled && state.registered
            ? q.active
            : null

  return (
    <>
      <ToggleRow
        checked={state.enabled}
        description={q.enabledDesc}
        label={q.enabledTitle}
        onChange={enabled => void saveQuickEntrySettings({ enabled })}
      />
      <ListRow
        action={
          <Input
            aria-label={q.shortcutTitle}
            disabled={!state.enabled}
            onBlur={commit}
            onChange={event => setDraft(event.target.value)}
            onKeyDown={event => {
              if (event.key === 'Enter') {
                event.preventDefault()
                commit()
              }
            }}
            placeholder={QUICK_ENTRY_DEFAULT_SHORTCUT}
            value={draft ?? state.shortcut}
          />
        }
        below={
          status && (
            <div
              className={
                state.error
                  ? 'mt-1 text-[length:var(--conversation-caption-font-size)] text-amber-500/90'
                  : 'mt-1 text-[length:var(--conversation-caption-font-size)] text-(--ui-text-tertiary)'
              }
            >
              {status}
            </div>
          )
        }
        description={q.shortcutDesc}
        title={q.shortcutTitle}
      />
      <ToggleRow
        checked={state.showOnLogin}
        description="Show the Composer briefly after the Desktop starts."
        label="Show Composer at login"
        onChange={showOnLogin => void saveQuickEntrySettings({ showOnLogin })}
      />
      <ListRow
        action={
          <Select
            onValueChange={mode =>
              void saveQuickEntrySettings({ mode: mode as (typeof QUICK_ENTRY_COMPOSER_MODES)[number] })
            }
            value={state.mode}
          >
            <SelectTrigger className="min-w-52 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {QUICK_ENTRY_COMPOSER_MODES.map(mode => (
                <SelectItem key={mode} value={mode}>
                  {mode}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        }
        description="HOTKEY_ONLY waits for the shortcut; SHOW_ON_LOGIN greets you briefly; PINNED stays visible."
        title="Composer mode"
      />
      <ToggleRow
        checked={state.startAtLogin}
        description="Start Hafiye Desktop from the XDG user autostart entry."
        label="Start Hafiye at login"
        onChange={startAtLogin => void saveQuickEntrySettings({ startAtLogin })}
      />
      <ToggleRow
        checked={state.startGatewayAtLogin}
        description="Enable the persistent hafiye-gateway.service user unit at login."
        label="Start gateway at login"
        onChange={startGatewayAtLogin => void saveQuickEntrySettings({ startGatewayAtLogin })}
      />
      <ToggleRow
        checked={state.launchMinimized}
        description="Launch the Desktop hidden when started by autostart."
        label="Launch minimized"
        onChange={launchMinimized => void saveQuickEntrySettings({ launchMinimized })}
      />
    </>
  )
}
