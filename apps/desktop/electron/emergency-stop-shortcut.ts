/**
 * Global emergency-stop accelerator.
 *
 * Electron owns the OS registration; the renderer receives only a signal and
 * sends the authenticated gateway RPC through its normal connection.  Keeping
 * registration in this small controller makes conflict and teardown behavior
 * unit-testable without booting the whole Desktop.
 */

import type { GlobalShortcutLike } from './quick-entry'

export const DEFAULT_EMERGENCY_STOP_SHORTCUT = 'Control+Super+Escape'

export interface EmergencyStopShortcutFallback {
  register(): boolean
  dispose(): void
}

export interface EmergencyStopShortcutController {
  register(): boolean
  dispose(): void
}

export function createEmergencyStopShortcut(
  globalShortcut: GlobalShortcutLike,
  onTrigger: () => void,
  fallback?: EmergencyStopShortcutFallback
): EmergencyStopShortcutController {
  let active: 'electron' | 'fallback' | null = null

  return {
    register() {
      if (active !== null) {
        return true
      }

      const accelerator = DEFAULT_EMERGENCY_STOP_SHORTCUT
      let registered = false

      try {
        registered = globalShortcut.isRegistered(accelerator)
          ? false
          : globalShortcut.register(accelerator, onTrigger)
      } catch {
        registered = false
      }

      if (registered) {
        active = 'electron'

        return true
      }

      try {
        if (fallback?.register()) {
          active = 'fallback'

          return true
        }
      } catch {
        // The fallback is best-effort; the caller logs the unavailable state.
      }

      return false
    },
    dispose() {
      if (active === null) {
        return
      }

      if (active === 'electron') {
        try {
          globalShortcut.unregister(DEFAULT_EMERGENCY_STOP_SHORTCUT)
        } catch {
          // Best effort during app teardown.
        }
      } else {
        try {
          fallback?.dispose()
        } catch {
          // Best effort during app teardown.
        }
      }

      active = null
    }
  }
}
