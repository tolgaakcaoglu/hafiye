import { useEffect, useRef } from 'react'

import { $jarvisInteraction, type JarvisInteractionState } from '@/store/jarvis-interaction'
import {
  initQuickEntryBridge,
  QUICK_TARGET_CURRENT,
  QUICK_TARGET_NEW,
  type QuickEntrySessionOption,
  setQuickEntrySubmitHandler
} from '@/store/quick-entry'
import { $gatewayState, $sessions } from '@/store/session'
import { $activeSessionId, $awaitingResponse, $busy } from '@/store/session'
import { $sessionStates, sessionTileDelegate } from '@/store/session-states'
import { isAuxiliaryWindow } from '@/store/windows'

interface QuickEntryBridgeParams {
  cancelRun: () => Promise<void> | void
  openSettings: () => void
  startFreshSessionDraft: () => void
  startVoice: () => void
  submitText: (text: string) => Promise<unknown> | unknown
  toggleVoice: () => void
}

// The picker is a capture aid, not a session browser — a handful of recent
// rows is the whole point.
const QUICK_ENTRY_SESSION_OPTIONS = 5

const VOICE_ACTIVE_STATES = [
  'LISTENING',
  'TRANSCRIBING',
  'ACKNOWLEDGING',
  'THINKING',
  'WORKING',
  'SPEAKING',
  'COMPLETED',
  'REARMING'
] as const

/** True when a wake-triggered voice turn has returned to a non-active state. */
export function shouldCollapseQuickEntryAfterVoice(
  previous: JarvisInteractionState,
  current: JarvisInteractionState
): boolean {
  return (
    Boolean(current.voiceTurnId) &&
    current.voiceTurnId === previous.voiceTurnId &&
    (current.state === 'IDLE_ARMED' || current.state === 'PAUSED') &&
    VOICE_ACTIVE_STATES.includes(previous.state as (typeof VOICE_ACTIVE_STATES)[number])
  )
}

function sessionOptions(): QuickEntrySessionOption[] {
  return $sessions
    .get()
    .filter(session => !session.archived)
    .slice(0, QUICK_ENTRY_SESSION_OPTIONS)
    .map(session => ({
      id: session.id,
      title: session.title?.trim() || session.preview?.trim() || session.id
    }))
}

/**
 * Wires the global-hotkey Quick Entry window back into the app, both ways:
 *
 * - **Inbound:** text captured there is routed by target and submitted through
 *   THIS window's normal prompt machinery — current chat rides `submitText`, a
 *   picked stored session rides the session-tile delegate (resume + submit,
 *   background, without touching the primary view — the same path tiled
 *   sessions use), and "new session" is a fresh draft + submit, exactly what
 *   clicking New Chat and typing does. One submit pipeline, no bespoke RPC.
 * - **Outbound:** gateway connection state + the recent-session list are pushed
 *   to the quick window (via main, which caches the latest push), so its input
 *   disables with a reconnect hint whenever the backend is unreachable.
 *
 * Handlers register ONCE through refs tracking the latest callbacks —
 * re-registering on identity churn leaves a nulled-handler window that can drop
 * a submit (the same bug shape use-pet-bridge guards). Primary window only: a
 * secondary session window must not also claim the global capture channel, or
 * one keystroke would send N prompts.
 */
export function useQuickEntryBridge({
  cancelRun,
  openSettings,
  startFreshSessionDraft,
  startVoice,
  submitText,
  toggleVoice
}: QuickEntryBridgeParams): void {
  const previousInteractionRef = useRef($jarvisInteraction.get())
  const submitTextRef = useRef(submitText)
  submitTextRef.current = submitText
  const startFreshRef = useRef(startFreshSessionDraft)
  startFreshRef.current = startFreshSessionDraft
  const cancelRunRef = useRef(cancelRun)
  cancelRunRef.current = cancelRun
  const openSettingsRef = useRef(openSettings)
  openSettingsRef.current = openSettings
  const startVoiceRef = useRef(startVoice)
  startVoiceRef.current = startVoice
  const toggleVoiceRef = useRef(toggleVoice)
  toggleVoiceRef.current = toggleVoice

  useEffect(() => {
    if (isAuxiliaryWindow()) {
      return
    }

    setQuickEntrySubmitHandler(({ target, text }) => {
      if (target === QUICK_TARGET_NEW) {
        // Same as the user clicking New Chat and typing: fresh draft, then the
        // normal submit creates the backend session.
        startFreshRef.current()
        void submitTextRef.current(text)

        return
      }

      if (target !== QUICK_TARGET_CURRENT) {
        // A picked stored session: resume + submit in the background through
        // the session-tile delegate so the primary view stays where it is.
        const delegate = sessionTileDelegate()

        if (delegate) {
          void delegate
            .resumeTile(target)
            .then(runtimeId => delegate.submitToSession(runtimeId, text))
            // A dead/undeliverable target must not swallow the prompt.
            .catch(() => void submitTextRef.current(text))

          return
        }
      }

      void submitTextRef.current(text)
    })

    const dispose = initQuickEntryBridge()

    const tray = window.hermesDesktop?.tray
    const offNewTask = tray?.onNewTask(() => startFreshRef.current())
    const offOpenSettings = tray?.onOpenSettings(() => openSettingsRef.current())

    const offOpenSession = tray?.onOpenSession(sessionId => {
      const delegate = sessionTileDelegate()

      if (delegate) {
        void delegate.resumeTile(sessionId).catch(() => undefined)
      }
    })

    const offToggleVoice = tray?.onToggleVoice(() => toggleVoiceRef.current())
    const quickEntry = window.hermesDesktop?.quickEntry
    const offStartVoice = quickEntry?.onStartVoice?.(() => startVoiceRef.current())
    const offStop = quickEntry?.onStop?.(() => void cancelRunRef.current())

    return () => {
      setQuickEntrySubmitHandler(null)
      dispose()
      offNewTask?.()
      offOpenSettings?.()
      offOpenSession?.()
      offToggleVoice?.()
      offStartVoice?.()
      offStop?.()
    }
  }, [])

  // Push gateway truth into the quick window whenever it changes: connection
  // state gates its input; the recent-session list feeds its target picker.
  useEffect(() => {
    if (isAuxiliaryWindow()) {
      return
    }

    const api = window.hermesDesktop?.quickEntry

    if (!api?.pushState) {
      return
    }

    const push = () => {
      const activeRuntimeId = $activeSessionId.get()
      const activeState = activeRuntimeId ? $sessionStates.get()[activeRuntimeId] : undefined
      const interaction = $jarvisInteraction.get()
      const activity = interaction.state
      const previousInteraction = previousInteractionRef.current
      const voiceTurnSettled = shouldCollapseQuickEntryAfterVoice(previousInteraction, interaction)

      previousInteractionRef.current = interaction

      api.pushState({
        activity,
        connected: $gatewayState.get() === 'open',
        currentTask: interaction.taskId || activeState?.storedSessionId || undefined,
        currentTool: interaction.currentTool || undefined,
        error: interaction.error || undefined,
        locality: interaction.locality || undefined,
        model: interaction.model || activeState?.model || undefined,
        progress: interaction.progress || undefined,
        sessions: sessionOptions(),
        voiceTurnId: interaction.voiceTurnId || undefined,
        wakeArmed: interaction.wakeArmed
      })

      // A wake invocation is one turn. Once its final speech/agent state has
      // settled, collapse the compact Composer so the microphone can return
      // to the background wake listener without leaving a stale capture UI.
      if (voiceTurnSettled) {
        api.dismiss()
      }
    }

    push()

    const offGateway = $gatewayState.listen(push)
    const offSessions = $sessions.listen(push)
    const offBusy = $busy.listen(push)
    const offAwaiting = $awaitingResponse.listen(push)
    const offSessionStates = $sessionStates.listen(push)
    const offJarvisInteraction = $jarvisInteraction.listen(push)

    return () => {
      offGateway()
      offSessions()
      offBusy()
      offAwaiting()
      offSessionStates()
      offJarvisInteraction()
    }
  }, [])
}
