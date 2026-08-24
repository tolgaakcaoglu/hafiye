import { useStore } from '@nanostores/react'

import { $wakeWord, toggleWakeWord } from '@/store/wake-word'

import { ToggleRow } from './primitives'

/**
 * The wake toggle is an RPC-backed control rather than a plain config field.
 * Starting it acquires the shared microphone lease and, when requested from
 * Desktop, attaches the client PCM feeder. The phrase/tuning fields below are
 * ordinary config fields and are persisted by the settings draft.
 */
export function WakeWordSetting() {
  const wake = useStore($wakeWord)
  const phrase = wake.phrase || 'Hafiye'
  const description = wake.notice
    ? wake.notice
    : wake.listening
      ? `Listening locally for “${phrase}”.`
      : `Enable local wake detection for “${phrase}”.`

  return (
    <ToggleRow
      checked={wake.listening}
      description={description}
      disabled={wake.pending}
      label="Wake word enabled"
      onChange={() => void toggleWakeWord()}
    />
  )
}
