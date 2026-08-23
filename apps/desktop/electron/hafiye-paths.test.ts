import assert from 'node:assert/strict'
import path from 'node:path'

import { test } from 'vitest'

import {
  resolveHafiyeDataHome,
  resolveHafiyePaths,
  resolveHafiyeStateHome,
  resolvePersistentGatewayPaths
} from './hafiye-paths'

test('POSIX Desktop roots follow the XDG Hafiye layout', () => {
  const env = {
    XDG_CONFIG_HOME: '/tmp/hafiye-config',
    XDG_DATA_HOME: '/tmp/hafiye-data',
    XDG_STATE_HOME: '/tmp/hafiye-state',
    XDG_CACHE_HOME: '/tmp/hafiye-cache'
  }

  assert.deepEqual(resolveHafiyePaths({ env, home: '/home/test', platform: 'linux' }), {
    config: '/tmp/hafiye-config/hafiye',
    data: '/tmp/hafiye-data/hafiye',
    state: '/tmp/hafiye-state/hafiye',
    cache: '/tmp/hafiye-cache/hafiye'
  })
})

test('POSIX Desktop roots use the Hafiye defaults when XDG overrides are absent', () => {
  const options = { env: {}, home: '/home/test', platform: 'linux' as const }

  assert.equal(resolveHafiyeDataHome(options), '/home/test/.local/share/hafiye')
  assert.equal(resolveHafiyeStateHome(options), '/home/test/.local/state/hafiye')
})

test('Windows Desktop roots match the Python Hafiye path policy', () => {
  assert.deepEqual(
    resolveHafiyePaths({
      env: {
        APPDATA: 'C:/Users/test/AppData/Roaming',
        LOCALAPPDATA: 'C:/Users/test/AppData/Local'
      },
      home: 'C:/Users/test',
      platform: 'win32'
    }),
    {
      config: path.win32.join('C:/Users/test/AppData/Roaming', 'hafiye'),
      data: path.win32.join('C:/Users/test/AppData/Local', 'hafiye'),
      state: path.win32.join('C:/Users/test/AppData/Local', 'hafiye', 'state'),
      cache: path.win32.join('C:/Users/test/AppData/Local', 'hafiye', 'cache')
    }
  )
})

test('relative XDG overrides are ignored', () => {
  assert.equal(
    resolveHafiyeDataHome({
      env: { XDG_DATA_HOME: 'relative-data' },
      home: '/home/test',
      platform: 'linux'
    }),
    '/home/test/.local/share/hafiye'
  )
})

test('persistent gateway paths use the Hafiye state root and owner service unit', () => {
  assert.deepEqual(
    resolvePersistentGatewayPaths({
      env: { XDG_STATE_HOME: '/tmp/hafiye-state' },
      home: '/home/test',
      platform: 'linux'
    }),
    {
      stateDir: '/tmp/hafiye-state/hafiye/gateway',
      tokenFile: '/tmp/hafiye-state/hafiye/gateway/session-token',
      descriptorFile: '/tmp/hafiye-state/hafiye/gateway/connection.json',
      serviceUnit: '/home/test/.config/systemd/user/hafiye-gateway.service'
    }
  )
})
