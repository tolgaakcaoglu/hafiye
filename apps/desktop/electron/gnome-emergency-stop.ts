/**
 * GNOME's user-level fallback for global accelerators on Wayland.
 *
 * Electron's globalShortcut API is not available for native Wayland global
 * accelerators on every Linux session. GNOME already owns the compositor-level
 * keybinding service, so use one private custom keybinding only when Electron
 * cannot register the mandated accelerator. The command still enters through
 * the normal Hafiye CLI -> persistent gateway -> cancellation controller path.
 */

import { execFileSync } from 'node:child_process'

import type { EmergencyStopShortcutFallback } from './emergency-stop-shortcut'

export const GNOME_EMERGENCY_STOP_BINDING = '<Control><Super>Escape'
export const GNOME_EMERGENCY_STOP_PATH =
  '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/hafiye-emergency-stop/'

const GNOME_MEDIA_KEYS_SCHEMA = 'org.gnome.settings-daemon.plugins.media-keys'
const GNOME_CUSTOM_SCHEMA = `org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:${GNOME_EMERGENCY_STOP_PATH}`
const GNOME_EMERGENCY_STOP_NAME = 'Hafiye Emergency Stop'

export interface GSettingsLike {
  get(schema: string, key: string): string
  reset(schema: string, key: string): void
  set(schema: string, key: string, value: string): void
}

const systemGSettings: GSettingsLike = {
  get(schema, key) {
    return execFileSync('gsettings', ['get', schema, key], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      timeout: 2_000
    })
  },
  set(schema, key, value) {
    execFileSync('gsettings', ['set', schema, key, value], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      timeout: 2_000
    })
  },
  reset(schema, key) {
    execFileSync('gsettings', ['reset', schema, key], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      timeout: 2_000
    })
  }
}

function parseStringList(raw: string): string[] {
  const values: string[] = []
  const pattern = /'((?:\\.|[^'])*)'/g
  let match: RegExpExecArray | null

  while ((match = pattern.exec(raw)) !== null) {
    values.push(match[1].replace(/\\'/g, "'"))
  }

  return values
}

function quoteGVariantString(value: string): string {
  return `'${value.replaceAll('\\', '\\\\').replaceAll("'", "\\'")}'`
}

function serializeStringList(values: string[]): string {
  return `[${values.map(quoteGVariantString).join(', ')}]`
}

function shellQuote(value: string): string {
  const escaped = value.split("'").join("'" + '\\' + "''")

  return `'${escaped}'`
}

function readCustomValue(gsettings: GSettingsLike, key: string): string {
  const raw = gsettings.get(GNOME_CUSTOM_SCHEMA, key).trim()

  if (raw.length >= 2 && raw.startsWith("'") && raw.endsWith("'")) {
    return raw.slice(1, -1).replace(/\\'/g, "'").replace(/\\\\/g, '\\')
  }

  // gsettings switches to a double-quoted GVariant representation when the
  // value itself contains single quotes, which is the normal form for our
  // shell-quoted CLI command.
  if (raw.length >= 2 && raw.startsWith('"') && raw.endsWith('"')) {
    try {
      return JSON.parse(raw) as string
    } catch {
      return ''
    }
  }

  return ''
}

function commandForCli(cliPath: string, hermesHome?: string): string {
  const prefix = hermesHome
    ? `/usr/bin/env ${shellQuote(`HERMES_HOME=${hermesHome}`)} `
    : ''

  return `${prefix}${shellQuote(cliPath)} emergency-stop --reason=global-hotkey`
}

export function createGnomeEmergencyStopFallback(
  cliPath: string,
  hermesHome?: string,
  gsettings: GSettingsLike = systemGSettings
): EmergencyStopShortcutFallback {
  const command = commandForCli(cliPath, hermesHome)
  let active = false
  let ownsListEntry = false

  return {
    register() {
      if (active) {
        return true
      }

      try {
        const configuredPaths = parseStringList(gsettings.get(GNOME_MEDIA_KEYS_SCHEMA, 'custom-keybindings'))

        if (configuredPaths.includes(GNOME_EMERGENCY_STOP_PATH)) {
          const existingName = readCustomValue(gsettings, 'name')
          const existingCommand = readCustomValue(gsettings, 'command')
          const existingBinding = readCustomValue(gsettings, 'binding')

          // Never overwrite an unrelated user keybinding if a future GNOME
          // version or another tool happens to claim the reserved object path.
          if (
            (existingName && existingName !== GNOME_EMERGENCY_STOP_NAME) ||
            (existingCommand && existingCommand !== command) ||
            (existingBinding && existingBinding !== GNOME_EMERGENCY_STOP_BINDING)
          ) {
            return false
          }
        } else {
          ownsListEntry = true
        }

        gsettings.set(GNOME_CUSTOM_SCHEMA, 'name', quoteGVariantString(GNOME_EMERGENCY_STOP_NAME))
        gsettings.set(GNOME_CUSTOM_SCHEMA, 'command', quoteGVariantString(command))
        gsettings.set(GNOME_CUSTOM_SCHEMA, 'binding', quoteGVariantString(GNOME_EMERGENCY_STOP_BINDING))

        if (!configuredPaths.includes(GNOME_EMERGENCY_STOP_PATH)) {
          gsettings.set(
            GNOME_MEDIA_KEYS_SCHEMA,
            'custom-keybindings',
            serializeStringList([...configuredPaths, GNOME_EMERGENCY_STOP_PATH])
          )
        }

        active = true
        return true
      } catch {
        active = false
        ownsListEntry = false
        return false
      }
    },
    dispose() {
      if (!active) {
        return
      }

      try {
        if (ownsListEntry) {
          const configuredPaths = parseStringList(gsettings.get(GNOME_MEDIA_KEYS_SCHEMA, 'custom-keybindings'))
          gsettings.set(
            GNOME_MEDIA_KEYS_SCHEMA,
            'custom-keybindings',
            serializeStringList(configuredPaths.filter(value => value !== GNOME_EMERGENCY_STOP_PATH))
          )
          gsettings.reset(GNOME_CUSTOM_SCHEMA, 'name')
          gsettings.reset(GNOME_CUSTOM_SCHEMA, 'command')
          gsettings.reset(GNOME_CUSTOM_SCHEMA, 'binding')
        }
      } catch {
        // Best effort. A stale Hafiye-owned entry is harmless and is repaired
        // on the next launch; unrelated custom keybindings are never removed.
      }

      active = false
      ownsListEntry = false
    }
  }
}

export function gnomeSessionSupportsFallback(env: NodeJS.ProcessEnv = process.env): boolean {
  if (process.platform !== 'linux') {
    return false
  }

  const desktop = `${env.XDG_CURRENT_DESKTOP ?? ''}:${env.DESKTOP_SESSION ?? ''}`.toLowerCase()
  return desktop.split(/[:;,]/).some(value => value.trim() === 'gnome' || value.trim() === 'ubuntu')
}
