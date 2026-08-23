import { TRANSLATIONS } from './catalog'
import { DEFAULT_LOCALE } from './languages'
import type { Locale } from './types'

let runtimeLocale: Locale = DEFAULT_LOCALE

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

/** Walk a dot-path (`a.b.c`) into a nested message tree. */
function resolvePath(source: unknown, key: string): unknown {
  return key.split('.').reduce<unknown>((current, part) => (isRecord(current) ? current[part] : undefined), source)
}

/** A string is returned as-is, a function is called with `args`, else `null`. */
function render(value: unknown, args: unknown[]): null | string {
  if (typeof value === 'string') {
    return value
  }

  if (typeof value === 'function') {
    return (value as (...args: unknown[]) => string)(...args)
  }

  return null
}

/**
 * Keep the upstream translation catalog and its keys intact while ensuring
 * normal Hafiye UI never exposes the inherited product name.  Delimiters
 * used by package names, protocol headers, storage keys, and URLs are kept
 * intact; standalone CLI examples and prose are intentionally rebranded.
 */
export function rebrandUserFacingMessage(value: string): string {
  return value
    .replace(/(?<![A-Za-z0-9_@./-])Hermes(?![A-Za-z0-9_.-]|:\/\/)/g, 'Hafiye')
    .replace(/(?<![A-Za-z0-9_@./-])hermes(?![A-Za-z0-9_.-]|:\/\/)/g, 'hafiye')
}

const rebrandedTrees = new WeakMap<object, object>()

/**
 * Rebrand the catalog shape used by React's `useI18n().t` without copying the
 * large locale objects or changing their keys. Functions are wrapped too, so
 * interpolated messages receive the same product-name treatment as literals.
 */
export function rebrandTranslationTree<T>(value: T): T {
  if (typeof value === 'string') {
    return rebrandUserFacingMessage(value) as T
  }

  if (typeof value === 'function') {
    return ((...args: unknown[]) => rebrandUserFacingMessage(String(value(...args)))) as T
  }

  if (!isRecord(value)) {
    return value
  }

  const cached = rebrandedTrees.get(value)
  if (cached) {
    return cached as T
  }

  const proxy = new Proxy(value, {
    get(target, property, receiver) {
      return rebrandTranslationTree(Reflect.get(target, property, receiver))
    }
  })
  rebrandedTrees.set(value, proxy)
  return proxy as T
}

/** The active → DEFAULT → key resolution every translator shares. `source`
 *  yields a message tree per locale — the app catalog, or a plugin's bundles. */
export function translateFrom(
  source: (locale: Locale) => unknown,
  locale: Locale,
  key: string,
  args: unknown[]
): string {
  const active = render(resolvePath(source(locale), key), args)

  if (active !== null) {
    return rebrandUserFacingMessage(active)
  }

  if (locale !== DEFAULT_LOCALE) {
    const fallback = render(resolvePath(source(DEFAULT_LOCALE), key), args)

    if (fallback !== null) {
      return rebrandUserFacingMessage(fallback)
    }
  }

  return key
}

export function setRuntimeI18nLocale(locale: Locale) {
  runtimeLocale = locale
}

/** The locale module-level translators resolve against (the app's active
 *  `display.language`). Plugin `ctx.i18n.t` reads this too. */
export function getRuntimeI18nLocale(): Locale {
  return runtimeLocale
}

export function translateNow(key: string, ...args: unknown[]): string {
  return translateFrom(locale => TRANSLATIONS[locale], runtimeLocale, key, args)
}
