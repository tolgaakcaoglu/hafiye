import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  clearSelectedVoiceInputDeviceId,
  getVoiceInputStream,
  getSelectedVoiceInputDeviceId,
  setSelectedVoiceInputDeviceId
} from './voice-input-device'

describe('voice input device selection', () => {
  const getUserMedia = vi.fn()

  beforeEach(() => {
    window.localStorage.clear()
    getUserMedia.mockReset()
    Object.defineProperty(navigator, 'mediaDevices', {
      configurable: true,
      value: { getUserMedia }
    })
  })

  it('persists and clears the selected device id', () => {
    setSelectedVoiceInputDeviceId('usb-mic')
    expect(getSelectedVoiceInputDeviceId()).toBe('usb-mic')

    clearSelectedVoiceInputDeviceId()
    expect(getSelectedVoiceInputDeviceId()).toBe('')
  })

  it('falls back to the system default when a selected device was removed', async () => {
    const fallbackStream = { getTracks: () => [] } as unknown as MediaStream
    setSelectedVoiceInputDeviceId('removed-mic')
    getUserMedia
      .mockRejectedValueOnce(new DOMException('missing', 'OverconstrainedError'))
      .mockResolvedValueOnce(fallbackStream)

    const stream = await getVoiceInputStream({ echoCancellation: true })

    expect(stream).toBe(fallbackStream)
    expect(getUserMedia).toHaveBeenNthCalledWith(1, {
      audio: { echoCancellation: true, deviceId: { exact: 'removed-mic' } },
      video: false
    })
    expect(getUserMedia).toHaveBeenNthCalledWith(2, {
      audio: { echoCancellation: true },
      video: false
    })
    expect(getSelectedVoiceInputDeviceId()).toBe('')
  })
})
