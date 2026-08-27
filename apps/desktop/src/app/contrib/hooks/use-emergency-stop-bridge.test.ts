import { renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const gatewayEventCallbacks = vi.hoisted(() => new Map<string, () => void>())
const stopVoicePlayback = vi.hoisted(() => vi.fn())
const transitionJarvisInteraction = vi.hoisted(() => vi.fn())

vi.mock('@/contrib/events', () => ({
  onGatewayEvent: (name: string, callback: () => void) => {
    gatewayEventCallbacks.set(name, callback)

    return () => gatewayEventCallbacks.delete(name)
  }
}))
vi.mock('@/lib/voice-playback', () => ({ stopVoicePlayback }))
vi.mock('@/store/jarvis-interaction', () => ({ transitionJarvisInteraction }))
vi.mock('@/store/notifications', () => ({ notifyError: vi.fn() }))
vi.mock('@/store/windows', () => ({ isAuxiliaryWindow: () => false }))

const { useEmergencyStopBridge } = await import('./use-emergency-stop-bridge')

describe('useEmergencyStopBridge tray computer-control gate', () => {
  let onComputerControl: ((paused: boolean) => void) | undefined
  let onEmergencyStop: (() => void) | undefined
  const disposeComputer = vi.fn()
  const disposeEmergency = vi.fn()

  beforeEach(() => {
    gatewayEventCallbacks.clear()
    stopVoicePlayback.mockReset()
    transitionJarvisInteraction.mockReset()
    disposeComputer.mockReset()
    disposeEmergency.mockReset()
    ;(window as unknown as { hermesDesktop: unknown }).hermesDesktop = {
      tray: {
        onEmergencyStop: (callback: () => void) => {
          onEmergencyStop = callback

          return disposeEmergency
        },
        onToggleComputerControl: (callback: (paused: boolean) => void) => {
          onComputerControl = callback

          return disposeComputer
        }
      }
    }
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('pauses through emergency.stop and resumes through emergency.resume', async () => {
    const requestGatewayMock = vi.fn(
      async (_method: string, _params?: Record<string, unknown>, _timeoutMs?: number, _signal?: AbortSignal) => ({})
    )
    const requestGateway = async <T>(
      method: string,
      params?: Record<string, unknown>,
      timeoutMs?: number,
      signal?: AbortSignal
    ): Promise<T> => requestGatewayMock(method, params, timeoutMs, signal) as Promise<T>
    const hook = renderHook(() => useEmergencyStopBridge({ requestGateway }))

    onComputerControl?.(true)
    expect(stopVoicePlayback).toHaveBeenCalledTimes(1)
    expect(transitionJarvisInteraction).toHaveBeenCalledWith({ active: true, type: 'emergency' })
    expect(requestGatewayMock).toHaveBeenCalledWith(
      'emergency.stop',
      { reason: 'tray-computer-control' },
      10_000,
      undefined
    )

    onComputerControl?.(false)
    await waitFor(() =>
      expect(requestGatewayMock).toHaveBeenCalledWith(
        'emergency.resume',
        { reason: 'tray-computer-control' },
        10_000,
        undefined
      )
    )
    expect(transitionJarvisInteraction).toHaveBeenCalledWith({ active: false, type: 'emergency' })

    onEmergencyStop?.()
    expect(requestGatewayMock).toHaveBeenCalledWith('emergency.stop', { reason: 'tray' }, 10_000, undefined)

    hook.unmount()
    expect(disposeComputer).toHaveBeenCalledTimes(1)
    expect(disposeEmergency).toHaveBeenCalledTimes(1)
  })
})
