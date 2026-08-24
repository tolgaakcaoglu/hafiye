import { useCallback, useEffect, useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  listVoiceInputDevices,
  getSelectedVoiceInputDeviceId,
  requestVoiceInputPermission,
  setSelectedVoiceInputDeviceId,
  clearSelectedVoiceInputDeviceId
} from '@/lib/voice-input-device'

import { ListRow } from './primitives'

export function MicrophoneDeviceSetting() {
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([])
  const [selected, setSelected] = useState(() => getSelectedVoiceInputDeviceId())
  const [message, setMessage] = useState('')

  const refresh = useCallback(async () => {
    if (!navigator.mediaDevices?.enumerateDevices) {
      setMessage('This desktop does not expose microphone device enumeration.')

      return
    }

    let permissionMessage = ''

    try {
      await requestVoiceInputPermission()
    } catch {
      permissionMessage = 'Allow microphone access to reveal device names.'
    }

    try {
      const inputs = await listVoiceInputDevices()
      const current = getSelectedVoiceInputDeviceId()

      if (current && !inputs.some(device => device.deviceId === current)) {
        clearSelectedVoiceInputDeviceId()
        setSelected('')
      } else {
        setSelected(current)
      }

      setDevices(inputs)
      setMessage(permissionMessage || (inputs.length ? '' : 'No microphone input devices were found.'))
    } catch {
      setMessage('Microphone devices could not be enumerated.')
    }
  }, [])

  useEffect(() => {
    void refresh()
    const mediaDevices = navigator.mediaDevices
    mediaDevices?.addEventListener?.('devicechange', refresh)

    return () => mediaDevices?.removeEventListener?.('devicechange', refresh)
  }, [refresh])

  return (
    <ListRow
      action={
        <div className="flex min-w-0 gap-1.5">
          <select
            aria-label="Microphone input device"
            className="h-8 min-w-0 flex-1 rounded-md border border-input bg-background px-2 text-xs"
            disabled={!devices.length}
            onChange={event => {
              const deviceId = event.target.value
              setSelectedVoiceInputDeviceId(deviceId)
              setSelected(deviceId)
            }}
            value={selected}
          >
            <option value="">System default</option>
            {devices.map((device, index) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `Microphone ${index + 1}`}
              </option>
            ))}
          </select>
          <Button
            aria-label="Refresh microphone devices"
            onClick={() => void refresh()}
            size="sm"
            type="button"
            variant="outline"
          >
            Refresh
          </Button>
        </div>
      }
      description={message || 'Used by push-to-talk, continuous voice, wake capture, and barge-in.'}
      title="Microphone input"
    />
  )
}
