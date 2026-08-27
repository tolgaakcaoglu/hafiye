import type { MenuItemConstructorOptions } from 'electron'

export const HAFIYE_TRAY_PRIVACY_MODES = ['NORMAL', 'LOCAL_ONLY', 'OFFLINE'] as const

export type HafiyeTrayPrivacyMode = (typeof HAFIYE_TRAY_PRIVACY_MODES)[number]

export interface HafiyeTrayControlState {
  computerControlPaused: boolean
  gatewayRunning: boolean
  microphoneEnabled: boolean
  privacyMode: HafiyeTrayPrivacyMode
  voiceEnabled: boolean
}

export interface HafiyeTrayRecentTask {
  id: string
  title: string
}

export interface HafiyeTrayActions {
  emergencyStop: () => void
  openComposer: () => void
  openDesktop: () => void
  openLogs: () => void
  openRecentTask: (sessionId: string) => void
  openSettings: () => void
  newTask: () => void
  quitDesktop: () => void
  restartCore: () => void
  setPrivacyMode: (mode: HafiyeTrayPrivacyMode) => void
  stopCore: () => void
  toggleComputerControl: (paused: boolean) => void
  toggleMicrophone: (enabled: boolean) => void
  toggleVoice: (enabled: boolean) => void
}

export const DEFAULT_HAFIYE_TRAY_CONTROL_STATE: HafiyeTrayControlState = {
  computerControlPaused: false,
  gatewayRunning: false,
  microphoneEnabled: false,
  privacyMode: 'NORMAL',
  voiceEnabled: false
}

export function normalizeHafiyeTrayControlState(value: unknown): HafiyeTrayControlState {
  const input = value && typeof value === 'object' ? (value as Record<string, unknown>) : {}

  const privacyMode = HAFIYE_TRAY_PRIVACY_MODES.includes(input.privacyMode as HafiyeTrayPrivacyMode)
    ? (input.privacyMode as HafiyeTrayPrivacyMode)
    : 'NORMAL'

  return {
    computerControlPaused: input.computerControlPaused === true,
    gatewayRunning: input.gatewayRunning === true,
    microphoneEnabled: input.microphoneEnabled === true,
    privacyMode,
    voiceEnabled: input.voiceEnabled === true
  }
}

export function buildHafiyeTrayTemplate({
  actions,
  appName,
  recentTasks,
  state
}: {
  actions: HafiyeTrayActions
  appName: string
  recentTasks: HafiyeTrayRecentTask[]
  state: HafiyeTrayControlState
}): MenuItemConstructorOptions[] {
  const recentTaskItems: MenuItemConstructorOptions[] = recentTasks.length
    ? recentTasks.map(task => ({ click: () => actions.openRecentTask(task.id), label: task.title || task.id }))
    : [{ enabled: false, label: 'No recent tasks' }]

  return [
    { enabled: false, label: appName },
    { enabled: false, label: state.gatewayRunning ? '● Running' : '○ Reconnecting' },
    { type: 'separator' },
    { click: actions.openComposer, label: 'Open Composer' },
    { click: actions.openDesktop, label: `Open ${appName}` },
    { click: actions.newTask, label: 'New Task' },
    { type: 'separator' },
    {
      click: () => actions.toggleMicrophone(!state.microphoneEnabled),
      label: state.microphoneEnabled ? 'Mute Microphone' : 'Unmute Microphone'
    },
    {
      click: () => actions.toggleVoice(!state.voiceEnabled),
      label: state.voiceEnabled ? 'Pause Voice' : 'Resume Voice'
    },
    { click: actions.emergencyStop, label: 'Emergency Stop' },
    {
      click: () => actions.toggleComputerControl(!state.computerControlPaused),
      label: state.computerControlPaused ? 'Resume Computer Control' : 'Pause Computer Control'
    },
    {
      label: 'Privacy Mode',
      submenu: HAFIYE_TRAY_PRIVACY_MODES.map(mode => ({
        checked: state.privacyMode === mode,
        click: () => actions.setPrivacyMode(mode),
        label: mode,
        type: 'radio' as const
      }))
    },
    { label: 'Recent Tasks', submenu: recentTaskItems },
    { type: 'separator' },
    { click: actions.openSettings, label: 'Settings' },
    { click: actions.openLogs, label: 'Logs' },
    { type: 'separator' },
    { click: actions.restartCore, label: 'Restart Hafiye' },
    { click: actions.quitDesktop, label: 'Quit Desktop' },
    { click: actions.stopCore, label: 'Stop Hafiye Core' }
  ]
}
