import assert from 'node:assert/strict'

import { test } from 'vitest'

import {
  buildAutostartDesktopEntry,
  composerStaysVisible,
  DEFAULT_COMPOSER_MODE,
  DEFAULT_COMPOSER_SETTINGS,
  resolveAutostartPath,
  sanitizeComposerSettings,
  shouldShowComposerOnLogin
} from './composer-lifecycle'

test('Composer defaults follow the Hafiye roadmap', () => {
  assert.equal(DEFAULT_COMPOSER_MODE, 'SHOW_ON_LOGIN')
  assert.deepEqual(DEFAULT_COMPOSER_SETTINGS, {
    launchMinimized: true,
    mode: 'SHOW_ON_LOGIN',
    showOnLogin: true,
    startAtLogin: true,
    startGatewayAtLogin: true
  })
})

test('Composer settings sanitize malformed and unsupported values', () => {
  assert.deepEqual(sanitizeComposerSettings({ mode: 'PINNED', showOnLogin: false }), {
    launchMinimized: true,
    mode: 'PINNED',
    showOnLogin: false,
    startAtLogin: true,
    startGatewayAtLogin: true
  })
  assert.deepEqual(sanitizeComposerSettings({ mode: 'not-a-mode', startAtLogin: 'yes' }), DEFAULT_COMPOSER_SETTINGS)
})

test('Composer login mode semantics are explicit', () => {
  assert.equal(shouldShowComposerOnLogin({ mode: 'HOTKEY_ONLY', showOnLogin: true }), false)
  assert.equal(shouldShowComposerOnLogin({ mode: 'SHOW_ON_LOGIN', showOnLogin: true }), true)
  assert.equal(shouldShowComposerOnLogin({ mode: 'PINNED', showOnLogin: true }), true)
  assert.equal(shouldShowComposerOnLogin({ mode: 'PINNED', showOnLogin: false }), false)
  assert.equal(composerStaysVisible({ mode: 'PINNED', showOnLogin: true }), true)
  assert.equal(composerStaysVisible({ mode: 'SHOW_ON_LOGIN', showOnLogin: true }), false)
})

test('autostart path follows XDG_CONFIG_HOME and uses the Hafiye filename', () => {
  assert.equal(
    resolveAutostartPath({ env: { XDG_CONFIG_HOME: '/tmp/config' }, home: '/home/test', platform: 'linux' }),
    '/tmp/config/autostart/hafiye.desktop'
  )
  assert.equal(
    resolveAutostartPath({ env: {}, home: '/home/test', platform: 'linux' }),
    '/home/test/.config/autostart/hafiye.desktop'
  )
})

test('autostart entry launches the packaged app hidden', () => {
  const entry = buildAutostartDesktopEntry({ execPath: '/opt/Hafiye/hafiye-desktop', hidden: true })

  assert.match(entry, /Name=Hafiye/)
  assert.match(entry, /Exec="\/opt\/Hafiye\/hafiye-desktop" --hidden/)
  assert.match(entry, /X-GNOME-Autostart-enabled=true/)
})

test('dev autostart entry retains the Electron app path', () => {
  const entry = buildAutostartDesktopEntry({
    appPath: '/home/test/hafiye/apps/desktop',
    execPath: '/home/test/.local/node/electron'
  })

  assert.match(entry, /Exec="\/home\/test\/\.local\/node\/electron" "\/home\/test\/hafiye\/apps\/desktop" --hidden/)
})
