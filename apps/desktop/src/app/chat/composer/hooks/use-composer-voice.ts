import { useStore } from '@nanostores/react'
import { useCallback, useEffect, useRef, useState } from 'react'

import { useI18n } from '@/i18n'
import { chatMessageText, collectUnspokenTurnSpeech } from '@/lib/chat-messages'
import { triggerHaptic } from '@/lib/haptics'
import { buildVoiceAcknowledgement } from '@/lib/speech-text'
import { markAssistantIdSpoken, resolveSpokenReply } from '@/lib/spoken-reply'
import { playSpeechText, stopVoicePlayback } from '@/lib/voice-playback'
import { clearWakeIndicator, syncWakeIndicatorWithVoice } from '@/lib/wake-indicator'
import { $voiceConversationStartRequest, takeVoiceConversationStartMode } from '@/store/composer'
import { resetBrowseState } from '@/store/composer-input-history'
import { $gateway } from '@/store/gateway'
import { $jarvisInteraction, transitionJarvisInteraction } from '@/store/jarvis-interaction'
import { notify, notifyError } from '@/store/notifications'
import { $autoSpeakReplies, $voiceStopPhrase, setAutoSpeakReplies } from '@/store/voice-prefs'
import { resumeWakeAfterVoice } from '@/store/wake-word'

import type { ComposerTarget } from '../focus'
import { onComposerVoiceToggleRequest } from '../focus'
import { useComposerScope } from '../scope'
import type { ChatBarProps } from '../types'

import { useAutoSpeakReplies } from './use-auto-speak-replies'
import { type ConversationStatus, useVoiceConversation } from './use-voice-conversation'
import { useVoiceRecorder } from './use-voice-recorder'

interface UseComposerVoiceArgs {
  busy: boolean
  clearDraft: () => void
  disabled: boolean
  focusInput: () => void
  insertText: (text: string) => void
  maxRecordingSeconds: number
  /** Interrupt the in-flight agent turn (Stop-button seam) — fired when the
   *  user speaks over the model while it is still generating. */
  onInterrupt?: () => Promise<void> | void
  onSubmit: ChatBarProps['onSubmit']
  onTranscribeAudio: ChatBarProps['onTranscribeAudio']
  sessionId: string | null | undefined
  /** This composer's focus-bus key — voice toggles targeting another
   *  composer (or the active one, when not us) are ignored. */
  target: ComposerTarget
}

/**
 * The composer's voice engine: push-to-talk dictation (transcript → draft), the
 * full voice-conversation loop, and auto-speak of replies. Self-contained — it
 * consumes the draft/submit primitives passed in but nothing depends back on it,
 * so it lifts cleanly out of ChatBar.
 */
export function useComposerVoice({
  busy,
  clearDraft,
  disabled,
  focusInput,
  insertText,
  maxRecordingSeconds,
  onInterrupt,
  onSubmit,
  onTranscribeAudio,
  sessionId,
  target
}: UseComposerVoiceArgs) {
  const { t } = useI18n()
  // A tile's composer speaks ITS transcript, not the primary chat's.
  const { $messages } = useComposerScope()
  const [voiceConversationActive, setVoiceConversationActive] = useState(false)
  const ownsWakeIndicatorRef = useRef(false)
  const wakeTurnRef = useRef(false)
  const endConversationRef = useRef<() => void>(() => {})
  const voiceStartRequest = useStore($voiceConversationStartRequest)

  const { dictate, voiceActivityState, voiceStatus } = useVoiceRecorder({
    focusInput,
    maxRecordingSeconds,
    onTranscript: insertText,
    onTranscribeAudio
  })

  /** Auto-speak selector: the latest unspoken reply only — a backlog collapses to the newest. */
  const pendingResponse = () => {
    const messages = $messages.get()
    const last = messages.findLast(m => m.role === 'assistant' && !m.hidden)
    const spoken = resolveSpokenReply(sessionId, messages)

    if (!last || last.id === spoken?.id) {
      return null
    }

    const text = chatMessageText(last).trim()

    if (!text) {
      return null
    }

    return {
      id: last.id,
      pending: Boolean(last.pending),
      text
    }
  }

  /**
   * Voice-conversation selector: every unspoken assistant bubble of the turn,
   * in order — narration interims AND the final answer, not just whichever
   * bubble happens to be last. See `collectUnspokenTurnSpeech`.
   */
  const pendingTurnResponse = () => {
    const messages = $messages.get()

    return collectUnspokenTurnSpeech(messages, resolveSpokenReply(sessionId, messages)?.id ?? null)
  }

  const consumePendingResponse = () => {
    const messages = $messages.get()
    const last = messages.findLast(m => m.role === 'assistant' && !m.hidden)

    if (last) {
      markAssistantIdSpoken(sessionId, messages, last.id)
    }
  }

  const publishQuickEntryTranscript = useCallback(async (text: string) => {
    const transcript = text.trim()

    if (!transcript) {
      return
    }

    transitionJarvisInteraction({ text: transcript, type: 'transcript' })

    // The compact Composer is a secondary renderer. A missing/old shell must
    // never prevent the actual voice request from reaching the agent.
    try {
      await window.hermesDesktop?.quickEntry?.publishTranscript?.(transcript)
    } catch {
      // The primary Composer remains the source of truth for submission.
    }
  }, [])

  const submitVoiceTurn = async (text: string) => {
    if (busy) {
      return
    }

    triggerHaptic('submit')
    resetBrowseState(sessionId)
    clearDraft()

    transitionJarvisInteraction({ type: 'acknowledging' })

    // Start the real agent turn immediately. Piper's short acknowledgement is
    // presentation, not a gate in front of tool execution; running both in
    // parallel keeps Jarvis responsive while the backend begins work.
    const submission = Promise.resolve().then(() => onSubmit(text))

    // Speak a short assistant-style acknowledgement before the real agent
    // turn. The detailed result remains visual; this prevents voice mode from
    // reading an entire coding/tool transcript aloud.
    try {
      await playSpeechText(buildVoiceAcknowledgement(text), { source: 'voice-ack' })
    } catch (error) {
      notifyError(error, 'Sesli onay oynatılamadı')
    }

    try {
      await submission
      // The gateway normally supplies message.complete. If a provider returns
      // before the event is observed, settle only an still-active local state;
      // never overwrite a completed/error transition received from the real
      // stream.
      const current = $jarvisInteraction.get()

      if (current.state === 'ACKNOWLEDGING' || current.state === 'THINKING' || current.state === 'WORKING') {
        transitionJarvisInteraction({ type: 'completed' })
      }
    } catch (error) {
      transitionJarvisInteraction({ message: error instanceof Error ? error.message : String(error), type: 'error' })
      throw error
    }
  }

  const handleVoiceStatusChange = useCallback((status: ConversationStatus) => {
    transitionJarvisInteraction({ status, type: 'voice_status' })

    // A wake-triggered request is one assistant turn, not an always-on voice
    // conversation. End it after the spoken result/turn settles so the compact
    // Composer can collapse and the wake listener can own the microphone again.
    if (status === 'idle' && wakeTurnRef.current) {
      wakeTurnRef.current = false
      endConversationRef.current()
    }
  }, [])

  const wakePausedRef = useRef(false)
  // Resolves once the in-flight wake.pause round-trip completes (mic released by
  // the wake listener). The conversation awaits this before opening its own mic
  // so the two never contend for the device — on Windows especially, opening the
  // capture device while the wake listener still holds it makes getUserMedia
  // fail and the conversation never starts listening.
  const wakePauseBarrierRef = useRef<Promise<void> | null>(null)

  const emergencyStop = useCallback(() => {
    stopVoicePlayback()
    transitionJarvisInteraction({ active: true, type: 'emergency' })
    const gateway = $gateway.get()

    if (!gateway) {
      return
    }

    return gateway
      .request('emergency.stop', { reason: 'voice-stop' })
      .catch(error => notifyError(error, 'Emergency stop failed'))
  }, [])

  const conversation = useVoiceConversation({
    busy,
    consumePendingResponse,
    enabled: voiceConversationActive,
    onFatalError: () => setVoiceConversationActive(false),
    // Speaking over the model mid-generation interrupts the in-flight turn —
    // the same seam as the Stop button — so the interjection becomes the next
    // turn instead of waiting behind a reply the user already rejected.
    onInterrupt,
    onStatusChange: handleVoiceStatusChange,
    // A spoken stop command ("stop", "never mind", "goodbye", …) ends the
    // hands-free conversation. Flipping the flag is the authoritative off
    // switch — the enabled=false prop + effect below drive conversation.end()
    // teardown (mic close, wake re-arm).
    onStopWord: () => {
      setVoiceConversationActive(false)
      void emergencyStop()
    },
    onSubmit: submitVoiceTurn,
    onTranscript: publishQuickEntryTranscript,
    onTranscribeAudio,
    pendingResponse: pendingTurnResponse,
    // Before the conversation opens the mic, wait for any in-flight wake.pause
    // to finish releasing the capture device (see wakePauseBarrierRef).
    beforeMicOpen: () => wakePauseBarrierRef.current ?? undefined
  })

  // The ref is assigned during render, before useVoiceConversation's status
  // effects run, so the one-shot wake callback can safely tear down the same
  // conversation instance that owns the recorder.
  endConversationRef.current = () => {
    setVoiceConversationActive(false)
    void conversation.end()
  }

  // eslint-disable-next-line no-restricted-syntax -- ownership token used only by unmount cleanup
  useEffect(() => {
    if (target !== 'main') {
      return
    }

    if (syncWakeIndicatorWithVoice(voiceConversationActive, conversation.status)) {
      ownsWakeIndicatorRef.current = voiceConversationActive
    }
  }, [conversation.status, target, voiceConversationActive])

  useEffect(
    () => () => {
      if (ownsWakeIndicatorRef.current) {
        clearWakeIndicator()
      }
    },
    []
  )

  // The `composer.voice` hotkey (Ctrl+B) toggles the conversation. Starting
  // with STT unconfigured lets the conversation surface its own "configure
  // speech-to-text" notice rather than silently no-opping.
  const toggleVoiceConversation = useCallback(() => {
    if (disabled) {
      return
    }

    if (voiceConversationActive) {
      wakeTurnRef.current = false
      setVoiceConversationActive(false)
      void conversation.end()
    } else {
      wakeTurnRef.current = false
      setVoiceConversationActive(true)
    }
  }, [conversation, disabled, voiceConversationActive])

  useEffect(
    () => onComposerVoiceToggleRequest(toggled => toggled === target && toggleVoiceConversation()),
    [target, toggleVoiceConversation]
  )

  useEffect(() => {
    if (target === 'main' && !disabled && !voiceConversationActive) {
      const mode = takeVoiceConversationStartMode(voiceStartRequest)

      if (mode) {
        wakeTurnRef.current = mode === 'wake'
        setVoiceConversationActive(true)
      }
    }
  }, [disabled, target, voiceConversationActive, voiceStartRequest])

  const resumeWakeIfPaused = useCallback(() => {
    if (!wakePausedRef.current) {
      return
    }

    wakePausedRef.current = false
    wakePauseBarrierRef.current = null
    // Reconcile, don't just resume: the wake word is a persistent setting, so
    // ending a voice chat must re-arm the listener whenever config says
    // enabled — including when the raw resume loses the mic-release race.
    void resumeWakeAfterVoice()
  }, [])

  // The ref is a request token (did WE issue wake.pause?), not an atom mirror —
  // it guards resumeWakeIfPaused from resuming a detector another surface owns.
  const pauseWakeForVoice = useCallback(() => {
    wakePausedRef.current = true

    const barrier = (async () => {
      try {
        await $gateway.get()?.request('wake.pause', {})
      } catch {
        // No wake listener / older backend — nothing held the mic.
      }
    })()

    wakePauseBarrierRef.current = barrier

    return barrier
  }, [])

  useEffect(() => {
    if (voiceConversationActive) {
      pauseWakeForVoice()
    } else {
      resumeWakeIfPaused()
    }
  }, [pauseWakeForVoice, resumeWakeIfPaused, voiceConversationActive])

  // 'Say "stop" to end the voice chat.' notice when the conversation starts.
  // Phrase comes from voice.stop_phrases (first entry) so a custom phrase
  // renders correctly; a null phrase (stop_phrases: []) shows no notice.
  useEffect(() => {
    if (!voiceConversationActive) {
      return
    }

    const phrase = $voiceStopPhrase.get()

    if (phrase) {
      notify({
        id: 'voice-stop-hint',
        kind: 'info',
        icon: 'mic',
        message: t.notifications.voice.sayStopToEnd(phrase)
      })
    }
  }, [t, voiceConversationActive])

  useEffect(() => resumeWakeIfPaused, [resumeWakeIfPaused])

  // Explicit start/end for the on-screen conversation controls (the hotkey uses
  // the gated toggle above).
  const startConversation = useCallback(() => {
    wakeTurnRef.current = false
    setVoiceConversationActive(true)
  }, [])

  const endConversation = useCallback(() => {
    wakeTurnRef.current = false
    setVoiceConversationActive(false)
    void conversation.end()
  }, [conversation])

  const handleToggleAutoSpeak = useCallback(() => {
    void setAutoSpeakReplies(!$autoSpeakReplies.get()).catch(error =>
      notifyError(error, t.settings.config.autosaveFailed)
    )
  }, [t])

  useAutoSpeakReplies({
    conversationActive: voiceConversationActive,
    failureLabel: t.assistant.thread.readAloudFailed,
    markSpoken: consumePendingResponse,
    pendingReply: pendingResponse,
    sessionId
  })

  return {
    conversation,
    dictate,
    endConversation,
    handleToggleAutoSpeak,
    startConversation,
    voiceActivityState,
    voiceConversationActive,
    voiceStatus
  }
}
