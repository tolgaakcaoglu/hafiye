import { useEffect, useRef } from 'react'

import { onGatewayEvent } from '@/contrib/events'
import { stopVoicePlayback } from '@/lib/voice-playback'
import { transitionJarvisInteraction } from '@/store/jarvis-interaction'
import { notifyError } from '@/store/notifications'
import { isAuxiliaryWindow } from '@/store/windows'

type GatewayRequest = <T>(
  method: string,
  params?: Record<string, unknown>,
  timeoutMs?: number,
  signal?: AbortSignal
) => Promise<T>

interface EmergencyStopBridgeParams {
  requestGateway: GatewayRequest
}

/**
 * Routes the native global shortcut and tray Stop into one gateway RPC.
 * Auxiliary session windows deliberately do not subscribe, so a single native
 * event cannot fan out into duplicate emergency requests.
 */
export function useEmergencyStopBridge({ requestGateway }: EmergencyStopBridgeParams): void {
  const requestGatewayRef = useRef(requestGateway)
  requestGatewayRef.current = requestGateway

  useEffect(() => {
    if (isAuxiliaryWindow()) {
      return
    }

    const trigger = (reason: string) => {
      // Cut renderer-owned audio synchronously; the backend then interrupts
      // the active turn, all delegations, and registered host processes.
      stopVoicePlayback()
      transitionJarvisInteraction({ active: true, type: 'emergency' })
      void requestGatewayRef
        .current('emergency.stop', { reason }, 10_000)
        .catch(error => notifyError(error, 'Emergency stop failed'))
    }

    const offShortcut = window.hermesDesktop?.onEmergencyStop?.(() => trigger('global-hotkey'))
    const offTray = window.hermesDesktop?.tray?.onEmergencyStop?.(() => trigger('tray'))

    const offComputerControl = window.hermesDesktop?.tray?.onToggleComputerControl?.(paused => {
      if (paused) {
        trigger('tray-computer-control')

        return
      }

      void requestGatewayRef
        .current('emergency.resume', { reason: 'tray-computer-control' }, 10_000)
        .then(() => transitionJarvisInteraction({ active: false, type: 'emergency' }))
        .catch(error => notifyError(error, 'Computer control could not be resumed'))
    })

    const offGateway = onGatewayEvent('emergency.stop', () => {
      // A GNOME Wayland keybinding invokes the CLI directly, so the renderer
      // learns about that same cancellation through the gateway event rather
      // than relying on an Electron globalShortcut callback.
      stopVoicePlayback()
      transitionJarvisInteraction({ active: true, type: 'emergency' })
    })

    const offGatewayResume = onGatewayEvent('emergency.resume', () => {
      transitionJarvisInteraction({ active: false, type: 'emergency' })
    })

    return () => {
      offShortcut?.()
      offTray?.()
      offComputerControl?.()
      offGateway()
      offGatewayResume()
    }
  }, [])
}
