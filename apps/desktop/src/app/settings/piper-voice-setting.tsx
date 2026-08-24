import { useCallback, useEffect, useState } from 'react'

import { Button } from '@/components/ui/button'
import { getPiperVoicePreview, getPiperVoices } from '@/hermes'
import type { PiperVoice } from '@/types/hermes'

import { ListRow } from './primitives'

interface PiperVoiceSettingProps {
  onChange: (voice: string) => void
  profile?: null | string
  value: unknown
}

export function PiperVoiceSetting({ onChange, profile, value }: PiperVoiceSettingProps) {
  const selected = String(value ?? '')
  const [voices, setVoices] = useState<PiperVoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [previewing, setPreviewing] = useState(false)
  const [previewUrl, setPreviewUrl] = useState('')

  const refresh = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const result = await getPiperVoices(profile)
      setVoices(result.voices)

      if (!result.ready) {
        setError('Managed Piper is not installed yet. Run `hafiye voice install-piper`.')
      }
    } catch {
      setError('Installed Piper voices could not be loaded.')
    } finally {
      setLoading(false)
    }
  }, [profile])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const preview = async () => {
    if (!selected) {
      return
    }

    setPreviewing(true)
    setError('')

    try {
      const result = await getPiperVoicePreview('Merhaba, ben Hafiye. Türkçe ses testi.', selected, profile)
      setPreviewUrl(result.data_url)
    } catch {
      setError('Piper voice preview failed.')
    } finally {
      setPreviewing(false)
    }
  }

  const hasSelectedOption = voices.some(voice => voice.name === selected)

  return (
    <ListRow
      action={
        <div className="flex min-w-0 gap-1.5">
          <select
            aria-label="Piper Turkish voice"
            className="h-8 min-w-0 flex-1 rounded-md border border-input bg-background px-2 text-xs"
            disabled={loading || (!voices.length && !selected)}
            onChange={event => {
              setPreviewUrl('')
              onChange(event.target.value)
            }}
            value={selected}
          >
            {!selected && <option value="">Select an installed voice</option>}
            {selected && !hasSelectedOption && <option value={selected}>{selected} (not installed)</option>}
            {voices.map(voice => (
              <option key={voice.name} value={voice.name}>
                {voice.name}
                {voice.language ? ` — ${voice.language}` : ''}
              </option>
            ))}
          </select>
          <Button
            disabled={!selected || previewing || !hasSelectedOption}
            onClick={() => void preview()}
            size="sm"
            type="button"
            variant="outline"
          >
            {previewing ? 'Previewing…' : 'Preview'}
          </Button>
        </div>
      }
      description={error || 'Managed local Turkish Piper voice. Preview uses the installed voice process.'}
      below={previewUrl ? <audio className="mt-2 h-8 max-w-full" controls src={previewUrl} /> : undefined}
      id="setting-field-tts.piper.voice"
      title="Piper voice"
    />
  )
}
