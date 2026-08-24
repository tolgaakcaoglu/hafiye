import { describe, expect, it } from 'vitest'

import { CONTROL_CENTER_PAGE_IDS } from './index'

describe('Hafiye Control Center navigation contract', () => {
  it('exposes every roadmap page exactly once', () => {
    expect(CONTROL_CENTER_PAGE_IDS).toEqual([
      'overview',
      'chat',
      'tasks',
      'models',
      'providers',
      'routing',
      'voice',
      'computer',
      'browser',
      'coding',
      'memory',
      'skills',
      'mcp',
      'automation',
      'permissions',
      'privacy',
      'logs',
      'developer',
      'about'
    ])
    expect(new Set(CONTROL_CENTER_PAGE_IDS).size).toBe(CONTROL_CENTER_PAGE_IDS.length)
  })
})
