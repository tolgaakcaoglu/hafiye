import { beforeEach, describe, expect, it } from 'vitest'

import {
  $jarvisInteraction,
  initialJarvisInteractionState,
  jarvisInteractionReducer,
  resetJarvisInteraction,
  transitionJarvisFromGatewayEvent,
  transitionJarvisInteraction
} from './jarvis-interaction'

describe('jarvis interaction state', () => {
  beforeEach(() => resetJarvisInteraction())

  it('models the installed wake → voice → work → speech → re-arm lifecycle', () => {
    let state = jarvisInteractionReducer(initialJarvisInteractionState, { at: 1, type: 'gateway_ready' })
    state = jarvisInteractionReducer(state, { armed: true, at: 2, owner: 'gui', type: 'wake_status' })
    state = jarvisInteractionReducer(state, { at: 3, sessionId: 'runtime-1', type: 'wake_detected' })
    state = jarvisInteractionReducer(state, { at: 4, status: 'listening', type: 'voice_status' })
    state = jarvisInteractionReducer(state, { at: 5, status: 'transcribing', type: 'voice_status' })
    state = jarvisInteractionReducer(state, { at: 6, text: 'Terminali aç', type: 'transcript' })
    state = jarvisInteractionReducer(state, { at: 7, type: 'acknowledging' })
    state = jarvisInteractionReducer(state, { at: 8, taskId: 'task-1', type: 'thinking' })
    state = jarvisInteractionReducer(state, {
      at: 9,
      progress: 'Terminal açılıyor',
      taskId: 'task-1',
      tool: 'terminal',
      type: 'working'
    })
    state = jarvisInteractionReducer(state, { at: 10, responseId: 'answer-1', type: 'speaking' })
    state = jarvisInteractionReducer(state, { at: 11, type: 'completed' })
    state = jarvisInteractionReducer(state, { at: 12, type: 'rearming' })
    state = jarvisInteractionReducer(state, { armed: true, at: 13, owner: 'gui', type: 'wake_status' })

    expect(state.state).toBe('IDLE_ARMED')
    expect(state.sessionId).toBe('runtime-1')
    expect(state.transcript).toBe('Terminali aç')
    expect(state.currentTool).toBeNull()
    expect(state.taskId).toBeNull()
    expect(state.wakeArmed).toBe(true)
    expect(state.updatedAt).toBe(13)
  })

  it('keeps error, cancellation and emergency state explicit', () => {
    const working = jarvisInteractionReducer(initialJarvisInteractionState, {
      at: 1,
      progress: 'Çalışıyor',
      tool: 'terminal',
      type: 'working'
    })

    const cancelled = jarvisInteractionReducer(working, { at: 2, type: 'cancel_requested' })
    const emergency = jarvisInteractionReducer(cancelled, { active: true, at: 3, type: 'emergency' })
    const error = jarvisInteractionReducer(emergency, { at: 4, message: 'Gateway bağlantısı kesildi.', type: 'error' })

    expect(cancelled).toMatchObject({ cancellation: 'REQUESTED', state: 'PAUSED' })
    expect(emergency).toMatchObject({ emergency: true, state: 'PAUSED' })
    expect(error).toMatchObject({ emergency: true, error: 'Gateway bağlantısı kesildi.', state: 'ERROR' })
  })

  it('ignores background gateway events for the foreground Jarvis surface', () => {
    expect(
      transitionJarvisFromGatewayEvent(
        { payload: { name: 'terminal' }, session_id: 'background', type: 'tool.start' },
        'foreground'
      )
    ).toBeNull()
    expect($jarvisInteraction.get().state).toBe('BOOTING')
  })

  it('projects real gateway events into tool and provider state', () => {
    transitionJarvisFromGatewayEvent(
      { payload: { model: 'local.gguf', provider: 'custom' }, type: 'session.info' },
      's1'
    )
    transitionJarvisFromGatewayEvent(
      { payload: { name: 'computer_use', progress: 'Firefox doğrulanıyor' }, session_id: 's1', type: 'tool.progress' },
      's1'
    )

    expect($jarvisInteraction.get()).toMatchObject({
      currentTool: 'computer_use',
      model: 'local.gguf',
      progress: 'Firefox doğrulanıyor',
      provider: 'custom',
      state: 'WORKING'
    })
  })

  it('updates the atom through the public transition seam', () => {
    const next = transitionJarvisInteraction({ at: 99, type: 'rearming' })

    expect(next.state).toBe('REARMING')
    expect($jarvisInteraction.get()).toEqual(next)
  })
})
