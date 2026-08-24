import { describe, expect, it, vi } from 'vitest'

import { createEmergencyStopShortcut, DEFAULT_EMERGENCY_STOP_SHORTCUT } from './emergency-stop-shortcut'
import type { GlobalShortcutLike } from './quick-entry'

function fakeGlobalShortcut(options: { register?: boolean; taken?: string[] } = {}) {
  const held = new Set(options.taken ?? [])
  const globalShortcut: GlobalShortcutLike = {
    isRegistered: vi.fn((accelerator: string) => held.has(accelerator)),
    register: vi.fn((accelerator: string, _callback: () => void) => {
      if (options.register === false || held.has(accelerator)) {
        return false
      }

      held.add(accelerator)

      return true
    }),
    unregister: vi.fn((accelerator: string) => void held.delete(accelerator))
  }

  return { globalShortcut, held }
}

describe('createEmergencyStopShortcut', () => {
  it('registers the mandated Control+Super+Escape accelerator', () => {
    const { globalShortcut } = fakeGlobalShortcut()
    const controller = createEmergencyStopShortcut(globalShortcut, vi.fn())

    expect(controller.register()).toBe(true)
    expect(globalShortcut.isRegistered(DEFAULT_EMERGENCY_STOP_SHORTCUT)).toBe(true)
  })

  it('is idempotent and releases the accelerator on dispose', () => {
    const { globalShortcut } = fakeGlobalShortcut()
    const controller = createEmergencyStopShortcut(globalShortcut, vi.fn())

    expect(controller.register()).toBe(true)
    expect(controller.register()).toBe(true)
    expect(globalShortcut.register).toHaveBeenCalledTimes(1)

    controller.dispose()

    expect(globalShortcut.unregister).toHaveBeenCalledWith(DEFAULT_EMERGENCY_STOP_SHORTCUT)
    expect(globalShortcut.isRegistered(DEFAULT_EMERGENCY_STOP_SHORTCUT)).toBe(false)
  })

  it('reports a conflict without claiming the accelerator', () => {
    const { globalShortcut } = fakeGlobalShortcut({ taken: [DEFAULT_EMERGENCY_STOP_SHORTCUT] })
    const controller = createEmergencyStopShortcut(globalShortcut, vi.fn())

    expect(controller.register()).toBe(false)
    expect(globalShortcut.register).not.toHaveBeenCalled()
  })

  it('uses the fallback when Electron cannot register on the current desktop', () => {
    const { globalShortcut } = fakeGlobalShortcut({ register: false })
    const fallback = {
      dispose: vi.fn(),
      register: vi.fn(() => true)
    }
    const controller = createEmergencyStopShortcut(globalShortcut, vi.fn(), fallback)

    expect(controller.register()).toBe(true)
    expect(fallback.register).toHaveBeenCalledOnce()

    controller.dispose()

    expect(fallback.dispose).toHaveBeenCalledOnce()
  })
})
