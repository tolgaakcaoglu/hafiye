import os from 'node:os'
import path from 'node:path'

interface HafiyePathOptions {
  env?: NodeJS.ProcessEnv
  home?: string
  platform?: NodeJS.Platform
}

function absoluteBase(value: string | undefined, fallback: string, pathModule: typeof path.posix) {
  const candidate = String(value || '').trim()

  return candidate && pathModule.isAbsolute(candidate) ? candidate : fallback
}

function posixBase(
  env: NodeJS.ProcessEnv,
  home: string,
  variable: string,
  fallback: string,
  pathModule: typeof path.posix
) {
  return absoluteBase(env[variable], pathModule.join(home, fallback), pathModule)
}

function windowsBase(
  env: NodeJS.ProcessEnv,
  home: string,
  variable: string,
  fallback: string,
  pathModule: typeof path.posix
) {
  return absoluteBase(env[variable], pathModule.join(home, 'AppData', fallback), pathModule)
}

/** Resolve the same user-facing roots as hermes_constants.py. */
function resolveHafiyePaths(options: HafiyePathOptions = {}) {
  const env = options.env || process.env
  const platform = options.platform || process.platform
  const home = options.home || os.homedir()
  const pathModule = platform === 'win32' ? path.win32 : path.posix

  if (platform === 'win32') {
    const config = windowsBase(env, home, 'APPDATA', 'Roaming', pathModule)
    const local = windowsBase(env, home, 'LOCALAPPDATA', 'Local', pathModule)
    const data = pathModule.join(local, 'hafiye')

    return {
      config: pathModule.join(config, 'hafiye'),
      data,
      state: pathModule.join(data, 'state'),
      cache: pathModule.join(data, 'cache')
    }
  }

  return {
    config: path.posix.join(posixBase(env, home, 'XDG_CONFIG_HOME', '.config', pathModule), 'hafiye'),
    data: path.posix.join(posixBase(env, home, 'XDG_DATA_HOME', '.local/share', pathModule), 'hafiye'),
    state: path.posix.join(posixBase(env, home, 'XDG_STATE_HOME', '.local/state', pathModule), 'hafiye'),
    cache: path.posix.join(posixBase(env, home, 'XDG_CACHE_HOME', '.cache', pathModule), 'hafiye')
  }
}

function resolveHafiyeDataHome(options: HafiyePathOptions = {}) {
  return resolveHafiyePaths(options).data
}

function resolveHafiyeStateHome(options: HafiyePathOptions = {}) {
  return resolveHafiyePaths(options).state
}

export { resolveHafiyeDataHome, resolveHafiyePaths, resolveHafiyeStateHome }
