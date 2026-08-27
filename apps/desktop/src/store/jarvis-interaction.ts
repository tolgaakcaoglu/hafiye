import { atom } from 'nanostores'

/**
 * The installed Hafiye experience has one interaction state, not a collection
 * of loosely related "busy" flags.  Every surface (wake listener, Composer,
 * task progress and the compact Composer) consumes this state.
 */
export const JARVIS_INTERACTION_STATES = [
  'BOOTING',
  'IDLE_ARMED',
  'WAKE_DETECTED',
  'LISTENING',
  'TRANSCRIBING',
  'ACKNOWLEDGING',
  'THINKING',
  'WORKING',
  'SPEAKING',
  'COMPLETED',
  'ERROR',
  'PAUSED',
  'REARMING'
] as const

export type JarvisInteractionStateName = (typeof JARVIS_INTERACTION_STATES)[number]
export type JarvisLocality = 'CLOUD' | 'LOCAL' | 'REMOTE' | 'UNKNOWN'
export type JarvisCancellation = 'NONE' | 'REQUESTED'

export interface JarvisInteractionState {
  cancellation: JarvisCancellation
  currentTool: string | null
  emergency: boolean
  error: string | null
  locality: JarvisLocality | null
  model: string | null
  progress: string | null
  provider: string | null
  sessionId: string | null
  state: JarvisInteractionStateName
  taskId: string | null
  transcript: string | null
  updatedAt: number
  voiceTurnId: string | null
  wakeArmed: boolean
  wakeOwner: string | null
}

export type JarvisInteractionEvent =
  | { at?: number; type: 'boot' }
  | { at?: number; model?: string | null; provider?: string | null; type: 'context'; locality?: JarvisLocality | null }
  | { at?: number; type: 'gateway_ready' }
  | { at?: number; message?: string; type: 'error' }
  | { at?: number; active: boolean; type: 'emergency' }
  | { at?: number; type: 'completed' }
  | { at?: number; type: 'paused'; reason?: string }
  | { at?: number; type: 'rearming' }
  | { at?: number; type: 'reset' }
  | { at?: number; text: string; type: 'transcript' }
  | { at?: number; type: 'acknowledging' }
  | { at?: number; sessionId?: string | null; taskId?: string | null; type: 'thinking' }
  | { at?: number; progress?: string | null; taskId?: string | null; tool?: string | null; type: 'working' }
  | { at?: number; responseId?: string | null; type: 'speaking' }
  | { at?: number; sessionId?: string | null; type: 'wake_detected'; voiceTurnId?: string | null }
  | { at?: number; armed: boolean; owner?: string | null; phrase?: string; type: 'wake_status' }
  | { at?: number; type: 'cancel_requested' }
  | { at?: number; status: 'idle' | 'listening' | 'speaking' | 'thinking' | 'transcribing'; type: 'voice_status' }

export const initialJarvisInteractionState: JarvisInteractionState = {
  cancellation: 'NONE',
  currentTool: null,
  emergency: false,
  error: null,
  locality: null,
  model: null,
  progress: null,
  provider: null,
  sessionId: null,
  state: 'BOOTING',
  taskId: null,
  transcript: null,
  updatedAt: 0,
  voiceTurnId: null,
  wakeArmed: false,
  wakeOwner: null
}

function updated(state: JarvisInteractionState, event: JarvisInteractionEvent, nextState?: JarvisInteractionStateName) {
  return {
    ...state,
    ...(nextState ? { state: nextState } : {}),
    updatedAt: event.at ?? state.updatedAt
  }
}

function activeTurn(state: JarvisInteractionState, event: JarvisInteractionEvent): JarvisInteractionState {
  return updated(
    {
      ...state,
      cancellation: 'NONE',
      emergency: false,
      error: null
    },
    event
  )
}

/** Pure state reducer used by both renderer integration and unit tests. */
export function jarvisInteractionReducer(
  state: JarvisInteractionState,
  event: JarvisInteractionEvent
): JarvisInteractionState {
  switch (event.type) {
    case 'boot':
      return updated({ ...initialJarvisInteractionState, updatedAt: state.updatedAt }, event, 'BOOTING')

    case 'gateway_ready':
      return updated(state, event, state.wakeArmed ? 'IDLE_ARMED' : 'PAUSED')

    case 'wake_status':
      // The detector is deliberately paused while the voice conversation owns
      // the microphone. That transport detail must not paint an active voice
      // turn as PAUSED; the next voice-status/re-arm event will settle it.
      if (
        !event.armed &&
        ['WAKE_DETECTED', 'LISTENING', 'TRANSCRIBING', 'ACKNOWLEDGING', 'THINKING', 'WORKING', 'SPEAKING'].includes(
          state.state
        )
      ) {
        return updated({ ...state, wakeArmed: false, wakeOwner: event.owner ?? null }, event)
      }

      return updated(
        {
          ...state,
          wakeArmed: event.armed,
          wakeOwner: event.owner ?? null,
          ...(event.armed ? { error: null } : {})
        },
        event,
        event.armed ? 'IDLE_ARMED' : 'PAUSED'
      )

    case 'wake_detected':
      return updated(
        {
          ...state,
          error: null,
          sessionId: event.sessionId ?? state.sessionId,
          taskId: null,
          transcript: null,
          voiceTurnId: event.voiceTurnId ?? state.voiceTurnId
        },
        event,
        'WAKE_DETECTED'
      )
    case 'voice_status': {
      const next =
        event.status === 'listening'
          ? 'LISTENING'
          : event.status === 'transcribing'
            ? 'TRANSCRIBING'
            : event.status === 'thinking'
              ? 'THINKING'
              : event.status === 'speaking'
                ? 'SPEAKING'
                : state.wakeArmed
                  ? 'IDLE_ARMED'
                  : 'PAUSED'

      return updated(activeTurn(state, event), event, next)
    }

    case 'transcript':
      return updated({ ...state, transcript: event.text }, event, 'TRANSCRIBING')

    case 'acknowledging':
      return updated(activeTurn(state, event), event, 'ACKNOWLEDGING')

    case 'thinking':
      return updated({ ...activeTurn(state, event), sessionId: event.sessionId ?? state.sessionId }, event, 'THINKING')

    case 'working':
      return updated(
        {
          ...activeTurn(state, event),
          currentTool: event.tool ?? state.currentTool,
          progress: event.progress ?? state.progress,
          taskId: event.taskId ?? state.taskId
        },
        event,
        'WORKING'
      )

    case 'speaking':
      return updated({ ...activeTurn(state, event), taskId: state.taskId }, event, 'SPEAKING')

    case 'completed':
      return updated(
        {
          ...state,
          cancellation: 'NONE',
          currentTool: null,
          error: null,
          progress: null,
          taskId: null
        },
        event,
        'COMPLETED'
      )

    case 'error':
      return updated(
        {
          ...state,
          cancellation: 'NONE',
          currentTool: null,
          error: event.message?.trim() || 'Hafiye işlemi başarısız oldu.',
          progress: null,
          taskId: null
        },
        event,
        'ERROR'
      )

    case 'paused':
      return updated(
        {
          ...state,
          cancellation: 'NONE',
          error: event.reason?.trim() || state.error,
          progress: event.reason?.trim() || state.progress
        },
        event,
        'PAUSED'
      )

    case 'cancel_requested':
      return updated({ ...state, cancellation: 'REQUESTED' }, event, 'PAUSED')

    case 'emergency':
      return updated(
        {
          ...state,
          cancellation: event.active ? 'REQUESTED' : 'NONE',
          emergency: event.active,
          progress: event.active ? 'Acil durdurma etkin.' : state.progress
        },
        event,
        event.active ? 'PAUSED' : state.state
      )

    case 'rearming':
      return updated({ ...state, cancellation: 'NONE', currentTool: null, progress: null }, event, 'REARMING')

    case 'context':
      return updated(
        {
          ...state,
          locality: event.locality === undefined ? state.locality : event.locality,
          model: event.model === undefined ? state.model : event.model,
          provider: event.provider === undefined ? state.provider : event.provider
        },
        event
      )

    case 'reset':
      return { ...initialJarvisInteractionState, updatedAt: event.at ?? state.updatedAt }
  }
}

export const $jarvisInteraction = atom<JarvisInteractionState>(initialJarvisInteractionState)

export function transitionJarvisInteraction(event: JarvisInteractionEvent): JarvisInteractionState {
  const next = jarvisInteractionReducer($jarvisInteraction.get(), event)
  $jarvisInteraction.set(next)

  return next
}

export function resetJarvisInteraction(): void {
  $jarvisInteraction.set(initialJarvisInteractionState)
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {}
}

function localityFromPayload(payload: Record<string, unknown>): JarvisLocality | null {
  const raw = String(payload.locality || payload.locality_policy || '')
    .trim()
    .toUpperCase()

  if (raw === 'LOCAL' || raw === 'LOCAL_ONLY' || raw === 'OFFLINE') {
    return 'LOCAL'
  }

  if (raw === 'REMOTE') {
    return 'REMOTE'
  }

  if (raw === 'CLOUD' || raw === 'GEMINI') {
    return 'CLOUD'
  }

  const provider = String(payload.provider || '').toLowerCase()

  if (provider === 'gemini' || provider === 'openai' || provider === 'anthropic') {
    return 'CLOUD'
  }

  return null
}

function eventSessionMatches(event: { session_id?: string }, activeSessionId?: string | null): boolean {
  const eventSessionId = event.session_id?.trim()

  return !eventSessionId || !activeSessionId || eventSessionId === activeSessionId
}

/**
 * Translate gateway stream events into the product state. Background sessions
 * must not overwrite the foreground Jarvis surface, hence the explicit active
 * session check at this seam.
 */
export function transitionJarvisFromGatewayEvent(
  event: { payload?: unknown; session_id?: string; type: string },
  activeSessionId?: string | null
): JarvisInteractionState | null {
  if (!eventSessionMatches(event, activeSessionId)) {
    return null
  }

  const payload = asRecord(event.payload)
  const sessionId = event.session_id?.trim() || activeSessionId || null
  const taskId = typeof payload.task_id === 'string' ? payload.task_id : sessionId
  const tool = typeof payload.name === 'string' ? payload.name : typeof payload.tool === 'string' ? payload.tool : null

  const progress =
    typeof payload.progress === 'string' ? payload.progress : typeof payload.text === 'string' ? payload.text : null

  switch (event.type) {
    case 'gateway.ready':
      return transitionJarvisInteraction({ type: 'gateway_ready' })

    case 'session.info':
      return transitionJarvisInteraction({
        locality: localityFromPayload(payload),
        model: typeof payload.model === 'string' ? payload.model : null,
        provider: typeof payload.provider === 'string' ? payload.provider : null,
        type: 'context'
      })

    case 'message.start':
      return transitionJarvisInteraction({ sessionId, taskId, type: 'thinking' })

    case 'tool.generating':

    case 'tool.start':

    case 'tool.progress':
      return transitionJarvisInteraction({ progress, taskId, tool, type: 'working' })

    case 'tool.complete':
      return transitionJarvisInteraction({
        progress: progress || 'Araç tamamlandı; sonuç doğrulanıyor.',
        taskId,
        tool,
        type: 'working'
      })

    case 'message.complete':
      return transitionJarvisInteraction({ type: 'completed' })

    case 'approval.request':

    case 'clarify.request':

    case 'secret.request':

    case 'sudo.request':
      return transitionJarvisInteraction({ reason: 'Kullanıcı girdisi bekleniyor.', type: 'paused' })

    case 'error':
      return transitionJarvisInteraction({
        message: typeof payload.message === 'string' ? payload.message : undefined,
        type: 'error'
      })

    case 'emergency.stop':
      return transitionJarvisInteraction({ active: true, type: 'emergency' })

    case 'emergency.resume':
      return transitionJarvisInteraction({ active: false, type: 'emergency' })

    default:
      return null
  }
}
