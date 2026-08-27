import { describe, expect, it } from 'vitest'

import {
  createGnomeEmergencyStopFallback,
  GNOME_EMERGENCY_STOP_BINDING,
  GNOME_EMERGENCY_STOP_PATH,
  type GSettingsLike
} from './gnome-emergency-stop'

function fakeGSettings(initialPaths: string[] = []) {
  const values = new Map<string, string>([
    ['org.gnome.settings-daemon.plugins.media-keys/custom-keybindings', `[${initialPaths.map(path => `'${path}'`).join(', ')}]`]
  ])
  const calls: Array<{ key: string; schema: string; value?: string }> = []
  const keyFor = (schema: string, key: string) => `${schema}/${key}`
  const gsettings: GSettingsLike = {
    get(schema, key) {
      return values.get(keyFor(schema, key)) ?? "''"
    },
    set(schema, key, value) {
      calls.push({ key, schema, value })
      values.set(keyFor(schema, key), value)
    },
    reset(schema, key) {
      calls.push({ key, schema })
      values.set(keyFor(schema, key), "''")
    }
  }

  return { calls, gsettings, values }
}

describe('createGnomeEmergencyStopFallback', () => {
  it('adds the Hafiye keybinding without replacing existing custom bindings', () => {
    const existing = '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/'
    const fake = fakeGSettings([existing])
    const fallback = createGnomeEmergencyStopFallback('/home/tolga/.venv/bin/hafiye', undefined, fake.gsettings)

    expect(fallback.register()).toBe(true)
    expect(fake.values.get('org.gnome.settings-daemon.plugins.media-keys/custom-keybindings')).toContain(existing)
    expect(fake.values.get('org.gnome.settings-daemon.plugins.media-keys/custom-keybindings')).toContain(
      GNOME_EMERGENCY_STOP_PATH
    )
    expect(fake.values.get(
      'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:' + GNOME_EMERGENCY_STOP_PATH + '/command'
    )).toContain('emergency-stop')
    expect(fake.values.get(
      'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:' + GNOME_EMERGENCY_STOP_PATH + '/binding'
    )).toBe(`'${GNOME_EMERGENCY_STOP_BINDING}'`)

    fallback.dispose()

    expect(fake.values.get('org.gnome.settings-daemon.plugins.media-keys/custom-keybindings')).toBe(`['${existing}']`)
  })

  it('fails closed when the reserved path belongs to another binding', () => {
    const fake = fakeGSettings([GNOME_EMERGENCY_STOP_PATH])
    fake.values.set(
      'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:' + GNOME_EMERGENCY_STOP_PATH + '/name',
      "'Other shortcut'"
    )
    const fallback = createGnomeEmergencyStopFallback('/home/tolga/.venv/bin/hafiye', undefined, fake.gsettings)

    expect(fallback.register()).toBe(false)
    expect(fake.calls).toHaveLength(0)
  })

  it('repairs a legacy Hafiye binding that still targets the Hermes launcher', () => {
    const fake = fakeGSettings([GNOME_EMERGENCY_STOP_PATH])
    const prefix = 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:' + GNOME_EMERGENCY_STOP_PATH
    fake.values.set(`${prefix}/name`, "'Hafiye Emergency Stop'")
    fake.values.set(`${prefix}/command`, "'/home/tolga/.local/bin/hermes' emergency-stop --reason=global-hotkey")
    fake.values.set(`${prefix}/binding`, `'${GNOME_EMERGENCY_STOP_BINDING}'`)

    const fallback = createGnomeEmergencyStopFallback('/usr/bin/hafiye', undefined, fake.gsettings)

    expect(fallback.register()).toBe(true)
    const updatedCommand = fake.values.get(`${prefix}/command`) ?? ''
    expect(updatedCommand).toContain('/usr/bin/hafiye')
    expect(updatedCommand).not.toContain('/home/tolga/.local/bin/hermes')
    expect(updatedCommand).toContain('emergency-stop --reason=global-hotkey')
  })
})
