import { renderHook, waitFor } from '@testing-library/react'
import { act } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const getHermesConfigRecord = vi.hoisted(() => vi.fn())
const saveHermesConfig = vi.hoisted(() => vi.fn())
const setAutoSpeakReplies = vi.hoisted(() => vi.fn())
const setWakeWordEnabled = vi.hoisted(() => vi.fn())
const stopVoicePlayback = vi.hoisted(() => vi.fn())

vi.mock('@/hermes', () => ({
  getHermesConfigRecord,
  HERMES_CONFIG_SAVED_EVENT: 'hermes:config-saved',
  saveHermesConfig
}))
vi.mock('@/lib/voice-playback', () => ({ stopVoicePlayback }))
vi.mock('@/store/notifications', () => ({ notifyError: vi.fn() }))
vi.mock('@/store/windows', () => ({ isAuxiliaryWindow: () => false }))
vi.mock('@/store/session', async () => {
  const { atom } = await import('nanostores')

  return { $gatewayState: atom('open') }
})
vi.mock('@/store/jarvis-interaction', async () => {
  const { atom } = await import('nanostores')

  return { $jarvisInteraction: atom({ emergency: false }) }
})
vi.mock('@/store/voice-prefs', async () => {
  const { atom } = await import('nanostores')

  return { $autoSpeakReplies: atom(true), setAutoSpeakReplies }
})
vi.mock('@/store/wake-word', async () => {
  const { atom } = await import('nanostores')

  return { $wakeWord: atom({ enabled: true }), setWakeWordEnabled }
})

const { useHafiyeTrayBridge } = await import('./use-hafiye-tray-bridge')

describe('useHafiyeTrayBridge', () => {
  const callbacks = new Map<string, (...args: never[]) => void>()
  const updateState = vi.fn()

  beforeEach(() => {
    callbacks.clear()
    updateState.mockReset()
    stopVoicePlayback.mockReset()
    setAutoSpeakReplies.mockReset().mockResolvedValue(undefined)
    setWakeWordEnabled.mockReset().mockResolvedValue(undefined)
    getHermesConfigRecord.mockReset().mockResolvedValue({ hafiye: { privacy_mode: 'NORMAL' } })
    saveHermesConfig.mockReset().mockResolvedValue({ ok: true })

    const subscribe = (name: string) => (callback: (...args: never[]) => void) => {
      callbacks.set(name, callback)

      return () => callbacks.delete(name)
    }

    ;(window as unknown as { hermesDesktop: unknown }).hermesDesktop = {
      tray: {
        onNewTask: subscribe('new-task'),
        onOpenSession: subscribe('open-session'),
        onOpenSettings: subscribe('settings'),
        onSetPrivacyMode: subscribe('privacy'),
        onToggleMicrophone: subscribe('microphone'),
        onToggleVoice: subscribe('voice'),
        updateState
      }
    }
  })

  it('routes every stateful tray action through its canonical renderer boundary', async () => {
    const openSession = vi.fn()
    const openSettings = vi.fn()
    const startFreshSessionDraft = vi.fn()
    const hook = renderHook(() => useHafiyeTrayBridge({ openSession, openSettings, startFreshSessionDraft }))

    await waitFor(() =>
      expect(updateState).toHaveBeenCalledWith({
        computerControlPaused: false,
        gatewayRunning: true,
        microphoneEnabled: true,
        privacyMode: 'NORMAL',
        voiceEnabled: true
      })
    )

    act(() => {
      callbacks.get('new-task')?.()
      callbacks.get('settings')?.()
      callbacks.get('open-session')?.('session-1' as never)
      callbacks.get('microphone')?.(false as never)
      callbacks.get('voice')?.(false as never)
      callbacks.get('privacy')?.('OFFLINE' as never)
    })

    expect(startFreshSessionDraft).toHaveBeenCalledTimes(1)
    expect(openSettings).toHaveBeenCalledTimes(1)
    expect(openSession).toHaveBeenCalledWith('session-1')
    expect(setWakeWordEnabled).toHaveBeenCalledWith(false)
    expect(stopVoicePlayback).toHaveBeenCalledTimes(1)
    expect(setAutoSpeakReplies).toHaveBeenCalledWith(false)
    await waitFor(() => expect(saveHermesConfig).toHaveBeenCalledWith({ hafiye: { privacy_mode: 'OFFLINE' } }))

    hook.unmount()
    expect(callbacks).toHaveProperty('size', 0)
  })
})
