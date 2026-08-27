import { describe, expect, it } from 'vitest'

import { jarvisInteractionReducer, initialJarvisInteractionState } from '@/store/jarvis-interaction'

import { shouldCollapseQuickEntryAfterVoice } from './use-quick-entry-bridge'

describe('shouldCollapseQuickEntryAfterVoice', () => {
  it('collapses a wake Composer after its spoken turn becomes idle', () => {
    const detected = jarvisInteractionReducer(initialJarvisInteractionState, {
      at: 1,
      type: 'wake_detected',
      voiceTurnId: 'voice-1'
    })
    const speaking = jarvisInteractionReducer(detected, { at: 2, status: 'speaking', type: 'voice_status' })
    const settled = jarvisInteractionReducer(speaking, { at: 3, status: 'idle', type: 'voice_status' })

    expect(shouldCollapseQuickEntryAfterVoice(speaking, settled)).toBe(true)
  })

  it('does not collapse active, manual, or unrelated turns', () => {
    const detected = jarvisInteractionReducer(initialJarvisInteractionState, {
      at: 1,
      type: 'wake_detected',
      voiceTurnId: 'voice-1'
    })
    const listening = jarvisInteractionReducer(detected, { at: 2, status: 'listening', type: 'voice_status' })
    const otherTurn = { ...listening, voiceTurnId: 'voice-2', state: 'PAUSED' as const }

    expect(shouldCollapseQuickEntryAfterVoice(listening, listening)).toBe(false)
    expect(shouldCollapseQuickEntryAfterVoice(listening, otherTurn)).toBe(false)
  })

  it('collapses after the re-arm transition completes a wake turn', () => {
    const detected = jarvisInteractionReducer(initialJarvisInteractionState, {
      at: 1,
      type: 'wake_detected',
      voiceTurnId: 'voice-1'
    })
    const rearming = jarvisInteractionReducer(detected, { at: 2, type: 'rearming' })
    const armed = jarvisInteractionReducer(rearming, { at: 3, armed: true, owner: 'gui', type: 'wake_status' })

    expect(shouldCollapseQuickEntryAfterVoice(rearming, armed)).toBe(true)
  })
})
