import { useEffect, useRef } from 'react'

import { getHermesConfigRecord, HERMES_CONFIG_SAVED_EVENT, saveHermesConfig } from '@/hermes'
import { stopVoicePlayback } from '@/lib/voice-playback'
import { $jarvisInteraction } from '@/store/jarvis-interaction'
import { notifyError } from '@/store/notifications'
import { $gatewayState } from '@/store/session'
import { $autoSpeakReplies, setAutoSpeakReplies } from '@/store/voice-prefs'
import { $wakeWord, setWakeWordEnabled } from '@/store/wake-word'
import { isAuxiliaryWindow } from '@/store/windows'

type PrivacyMode = 'LOCAL_ONLY' | 'NORMAL' | 'OFFLINE'

interface HafiyeTrayBridgeParams {
  openSession: (sessionId: string) => void
  openSettings: () => void
  startFreshSessionDraft: () => void
}

function privacyModeFromConfig(config: Record<string, unknown>): PrivacyMode {
  const hafiye = config.hafiye

  const value =
    hafiye && typeof hafiye === 'object' ? String((hafiye as Record<string, unknown>).privacy_mode || '') : ''

  return value === 'LOCAL_ONLY' || value === 'OFFLINE' ? value : 'NORMAL'
}

/**
 * Owns the stateful system-tray controls. Electron renders only cached labels;
 * every mutation still travels through the same renderer stores/config/RPCs as
 * Settings, Composer, wake, and emergency-stop.
 */
export function useHafiyeTrayBridge({
  openSession,
  openSettings,
  startFreshSessionDraft
}: HafiyeTrayBridgeParams): void {
  const openSessionRef = useRef(openSession)
  openSessionRef.current = openSession
  const openSettingsRef = useRef(openSettings)
  openSettingsRef.current = openSettings
  const startFreshRef = useRef(startFreshSessionDraft)
  startFreshRef.current = startFreshSessionDraft

  useEffect(() => {
    if (isAuxiliaryWindow()) {
      return
    }

    const tray = window.hermesDesktop?.tray

    if (!tray) {
      return
    }

    let privacyMode: PrivacyMode = 'NORMAL'

    const pushState = () => {
      tray.updateState({
        computerControlPaused: $jarvisInteraction.get().emergency,
        gatewayRunning: $gatewayState.get() === 'open',
        microphoneEnabled: $wakeWord.get().enabled,
        privacyMode,
        voiceEnabled: $autoSpeakReplies.get()
      })
    }

    const applyConfig = (config: Record<string, unknown>) => {
      privacyMode = privacyModeFromConfig(config)
      pushState()
    }

    void getHermesConfigRecord()
      .then(config => applyConfig(config as Record<string, unknown>))
      .catch(error => notifyError(error, 'Tray privacy state could not be loaded'))

    const offNewTask = tray.onNewTask(() => startFreshRef.current())
    const offOpenSettings = tray.onOpenSettings(() => openSettingsRef.current())
    const offOpenSession = tray.onOpenSession(sessionId => openSessionRef.current(sessionId))

    const offToggleMicrophone = tray.onToggleMicrophone(enabled => {
      void setWakeWordEnabled(enabled).catch(error => notifyError(error, 'Microphone state could not be changed'))
    })

    const offToggleVoice = tray.onToggleVoice(enabled => {
      if (!enabled) {
        stopVoicePlayback()
      }

      void setAutoSpeakReplies(enabled).catch(error => notifyError(error, 'Voice state could not be changed'))
    })

    const offSetPrivacy = tray.onSetPrivacyMode(mode => {
      const previous = privacyMode
      privacyMode = mode
      pushState()
      void getHermesConfigRecord()
        .then(async record => {
          const hafiye = record.hafiye && typeof record.hafiye === 'object' ? record.hafiye : {}
          await saveHermesConfig({ ...record, hafiye: { ...hafiye, privacy_mode: mode } })
        })
        .catch(error => {
          privacyMode = previous
          pushState()
          notifyError(error, 'Privacy mode could not be changed')
        })
    })

    const onConfigSaved = (event: Event) => {
      const detail = (event as CustomEvent<{ config?: unknown; profile?: null | string }>).detail

      if (detail?.profile || !detail?.config || typeof detail.config !== 'object') {
        return
      }

      applyConfig(detail.config as Record<string, unknown>)
    }

    window.addEventListener(HERMES_CONFIG_SAVED_EVENT, onConfigSaved)
    pushState()
    const offGateway = $gatewayState.listen(pushState)
    const offWake = $wakeWord.listen(pushState)
    const offVoice = $autoSpeakReplies.listen(pushState)
    const offInteraction = $jarvisInteraction.listen(pushState)

    return () => {
      offNewTask()
      offOpenSettings()
      offOpenSession()
      offToggleMicrophone()
      offToggleVoice()
      offSetPrivacy()
      offGateway()
      offWake()
      offVoice()
      offInteraction()
      window.removeEventListener(HERMES_CONFIG_SAVED_EVENT, onConfigSaved)
    }
  }, [])
}
