/** Device-local microphone preference shared by recording, wake capture, and
 * barge-in. The browser's deviceId is intentionally kept in the Desktop
 * profile, not sent to the backend config: it belongs to this physical input
 * device and may not exist on a remote backend. */

const STORAGE_KEY = 'hafiye.voice.input-device'

export function getSelectedVoiceInputDeviceId(): string {
  try {
    return window.localStorage.getItem(STORAGE_KEY) ?? ''
  } catch {
    return ''
  }
}

export function setSelectedVoiceInputDeviceId(deviceId: string): void {
  try {
    if (deviceId) {
      window.localStorage.setItem(STORAGE_KEY, deviceId)
    } else {
      window.localStorage.removeItem(STORAGE_KEY)
    }
  } catch {
    // Private browsing and locked-down Electron profiles may reject storage;
    // live capture still works with the browser default device.
  }
}

export function clearSelectedVoiceInputDeviceId(): void {
  setSelectedVoiceInputDeviceId('')
}

function isMissingSelectedDeviceError(error: unknown): boolean {
  const name = error instanceof DOMException ? error.name : error instanceof Error ? error.name : ''

  return name === 'OverconstrainedError' || name === 'NotFoundError' || name === 'DevicesNotFoundError'
}

/** Open a microphone stream, using the saved input device when it still exists.
 * A removed/unavailable device falls back to the browser default and clears
 * the stale preference so all voice modes recover without a restart. */
export async function getVoiceInputStream(constraints: MediaTrackConstraints = {}): Promise<MediaStream> {
  const selected = getSelectedVoiceInputDeviceId()
  const base = { ...constraints }

  if (!selected) {
    return navigator.mediaDevices.getUserMedia({ audio: base, video: false })
  }

  try {
    return await navigator.mediaDevices.getUserMedia({
      audio: { ...base, deviceId: { exact: selected } },
      video: false
    })
  } catch (error) {
    if (!isMissingSelectedDeviceError(error)) {
      throw error
    }

    clearSelectedVoiceInputDeviceId()

    return navigator.mediaDevices.getUserMedia({ audio: base, video: false })
  }
}

export async function listVoiceInputDevices(): Promise<MediaDeviceInfo[]> {
  if (!navigator.mediaDevices?.enumerateDevices) {
    return []
  }

  const devices = await navigator.mediaDevices.enumerateDevices()

  return devices.filter(device => device.kind === 'audioinput')
}

export async function requestVoiceInputPermission(): Promise<void> {
  const stream = await getVoiceInputStream()
  stream.getTracks().forEach(track => track.stop())
}
