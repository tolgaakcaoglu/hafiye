import os from 'node:os'
import path from 'node:path'

/** The three user-visible Composer launch modes mandated by the roadmap. */
export const COMPOSER_MODES = ['HOTKEY_ONLY', 'SHOW_ON_LOGIN', 'PINNED'] as const

export type ComposerMode = (typeof COMPOSER_MODES)[number]

export const DEFAULT_COMPOSER_MODE: ComposerMode = 'SHOW_ON_LOGIN'

export const DEFAULT_COMPOSER_SETTINGS: ComposerSettings = {
  launchMinimized: true,
  mode: DEFAULT_COMPOSER_MODE,
  showOnLogin: true,
  startAtLogin: true,
  startGatewayAtLogin: true
}

export interface ComposerSettings {
  /** Start the Desktop shell hidden/minimized from the XDG login item. */
  launchMinimized: boolean
  mode: ComposerMode
  /** Whether login should show the Composer (mode still controls its shape). */
  showOnLogin: boolean
  /** Whether Hafiye Desktop owns an XDG autostart entry. */
  startAtLogin: boolean
  /** Whether the persistent user gateway should be enabled at login. */
  startGatewayAtLogin: boolean
}

export interface AutostartEntryOptions {
  appName?: string
  appPath?: string
  execPath: string
  hidden?: boolean
}

export interface XdgPathOptions {
  env?: NodeJS.ProcessEnv
  home?: string
  platform?: NodeJS.Platform
}

function booleanOrDefault(value: unknown, fallback: boolean): boolean {
  return typeof value === 'boolean' ? value : fallback
}

function isComposerMode(value: unknown): value is ComposerMode {
  return typeof value === 'string' && (COMPOSER_MODES as readonly string[]).includes(value)
}

/** Normalize the main-process-owned Composer settings from disk/IPC input. */
export function sanitizeComposerSettings(raw: unknown): ComposerSettings {
  const record = raw && typeof raw === 'object' ? (raw as Record<string, unknown>) : {}

  return {
    launchMinimized: booleanOrDefault(record.launchMinimized, DEFAULT_COMPOSER_SETTINGS.launchMinimized),
    mode: isComposerMode(record.mode) ? record.mode : DEFAULT_COMPOSER_SETTINGS.mode,
    showOnLogin: booleanOrDefault(record.showOnLogin, DEFAULT_COMPOSER_SETTINGS.showOnLogin),
    startAtLogin: booleanOrDefault(record.startAtLogin, DEFAULT_COMPOSER_SETTINGS.startAtLogin),
    startGatewayAtLogin: booleanOrDefault(record.startGatewayAtLogin, DEFAULT_COMPOSER_SETTINGS.startGatewayAtLogin)
  }
}

/** Whether login should reveal the Composer at all. */
export function shouldShowComposerOnLogin(settings: Pick<ComposerSettings, 'mode' | 'showOnLogin'>): boolean {
  if (!settings.showOnLogin || settings.mode === 'HOTKEY_ONLY') {
    return false
  }

  return settings.mode === 'SHOW_ON_LOGIN' || settings.mode === 'PINNED'
}

/** PINNED means the Composer stays available after the login reveal. */
export function composerStaysVisible(settings: Pick<ComposerSettings, 'mode' | 'showOnLogin'>): boolean {
  return settings.showOnLogin && settings.mode === 'PINNED'
}

function xdgConfigHome({ env = process.env, home = os.homedir(), platform = process.platform }: XdgPathOptions = {}) {
  if (platform === 'win32') {
    return path.join(env.APPDATA || path.join(home, 'AppData', 'Roaming'))
  }

  const configured = String(env.XDG_CONFIG_HOME || '').trim()

  return path.posix.isAbsolute(configured) ? configured : path.posix.join(home, '.config')
}

/** Resolve the exact XDG autostart target without touching the filesystem. */
export function resolveAutostartPath(options: XdgPathOptions = {}): string {
  return path.join(xdgConfigHome(options), 'autostart', 'hafiye.desktop')
}

function desktopExecArg(value: string): string {
  // Desktop-entry Exec fields use backslash escapes rather than shell quoting.
  // Keep this deliberately small: the generated arguments are executable paths
  // and the app's own --hidden switch, not arbitrary shell input.
  return `"${String(value).replace(/([\\"%])/g, '\\$1')}"`
}

/** Build a valid user autostart file for both packaged and dev Electron runs. */
export function buildAutostartDesktopEntry({
  appName = 'Hafiye',
  appPath,
  execPath,
  hidden = true
}: AutostartEntryOptions): string {
  const command = [desktopExecArg(execPath)]

  if (appPath) {
    command.push(desktopExecArg(appPath))
  }

  if (hidden) {
    command.push('--hidden')
  }

  return [
    '[Desktop Entry]',
    'Type=Application',
    `Name=${appName}`,
    `Comment=Start ${appName} Desktop and connect to the persistent gateway`,
    `Exec=${command.join(' ')}`,
    'Terminal=false',
    'X-GNOME-Autostart-enabled=true',
    'X-KDE-autostart-after=panel',
    ''
  ].join('\n')
}

export { xdgConfigHome }
