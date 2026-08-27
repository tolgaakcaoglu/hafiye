import { describe, expect, it } from 'vitest'

import {
  buildHafiyeTrayTemplate,
  DEFAULT_HAFIYE_TRAY_CONTROL_STATE,
  type HafiyeTrayActions,
  normalizeHafiyeTrayControlState
} from './hafiye-tray-menu'

function actions(calls: string[]): HafiyeTrayActions {
  return {
    emergencyStop: () => calls.push('emergency'),
    newTask: () => calls.push('new-task'),
    openComposer: () => calls.push('composer'),
    openDesktop: () => calls.push('desktop'),
    openLogs: () => calls.push('logs'),
    openRecentTask: id => calls.push(`recent:${id}`),
    openSettings: () => calls.push('settings'),
    quitDesktop: () => calls.push('quit'),
    restartCore: () => calls.push('restart'),
    setPrivacyMode: mode => calls.push(`privacy:${mode}`),
    stopCore: () => calls.push('stop'),
    toggleComputerControl: paused => calls.push(`computer:${paused}`),
    toggleMicrophone: enabled => calls.push(`microphone:${enabled}`),
    toggleVoice: enabled => calls.push(`voice:${enabled}`)
  }
}

function click(item: { click?: unknown }) {
  expect(typeof item.click).toBe('function')
  ;(item.click as () => void)()
}

describe('Hafiye tray menu', () => {
  it('normalizes renderer state and rejects an invalid privacy mode', () => {
    expect(
      normalizeHafiyeTrayControlState({
        computerControlPaused: true,
        gatewayRunning: true,
        microphoneEnabled: true,
        privacyMode: 'INVALID',
        voiceEnabled: true
      })
    ).toEqual({
      computerControlPaused: true,
      gatewayRunning: true,
      microphoneEnabled: true,
      privacyMode: 'NORMAL',
      voiceEnabled: true
    })
    expect(normalizeHafiyeTrayControlState(null)).toEqual(DEFAULT_HAFIYE_TRAY_CONTROL_STATE)
  })

  it('builds stateful controls that invoke the requested next state', () => {
    const calls: string[] = []

    const template = buildHafiyeTrayTemplate({
      actions: actions(calls),
      appName: 'Hafiye',
      recentTasks: [{ id: 'session-1', title: 'Task one' }],
      state: {
        computerControlPaused: true,
        gatewayRunning: true,
        microphoneEnabled: true,
        privacyMode: 'LOCAL_ONLY',
        voiceEnabled: false
      }
    })

    expect(template[1].label).toBe('● Running')
    expect(template[7].label).toBe('Mute Microphone')
    expect(template[8].label).toBe('Resume Voice')
    expect(template[10].label).toBe('Resume Computer Control')
    click(template[7])
    click(template[8])
    click(template[10])

    const privacy = template[11].submenu
    expect(Array.isArray(privacy)).toBe(true)
    expect(privacy[1].checked).toBe(true)
    click(privacy[2])

    const recent = template[12].submenu
    expect(Array.isArray(recent)).toBe(true)
    click(recent[0])
    expect(calls).toEqual(['microphone:false', 'voice:true', 'computer:false', 'privacy:OFFLINE', 'recent:session-1'])
  })
})
