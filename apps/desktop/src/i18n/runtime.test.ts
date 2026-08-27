import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { fieldCopyForSchemaKey } from '@/app/settings/field-copy'

import { TRANSLATIONS } from './catalog'
import { rebrandTranslationTree, setRuntimeI18nLocale, translateFrom, translateNow } from './runtime'
import { zh } from './zh'

describe('desktop i18n runtime translator', () => {
  beforeEach(() => {
    setRuntimeI18nLocale('en')
  })

  afterEach(() => {
    setRuntimeI18nLocale('en')
  })

  it('translates string paths for the active runtime locale', () => {
    setRuntimeI18nLocale('zh')

    expect(translateNow('boot.ready')).toBe('Hafiye 桌面版已就绪')
    expect(translateNow('notifications.voice.noSpeechDetected')).toBe('没有检测到语音')
    expect(translateNow('composer.lookupNoMatches')).toBe('没有匹配项。')
    expect(translateNow('assistant.tool.statusRecovered')).toBe('已恢复')
  })

  it('passes arguments to function translations', () => {
    expect(translateNow('notifications.updateReadyMessage', 2)).toBe('2 new changes available.')
  })

  it('rebrands visible product copy without changing identifiers or URLs', () => {
    expect(
      translateFrom(
        () => ({
          probe: 'Hermes @hermes ~/.hermes https://hermes-agent.nousresearch.com hermes://legacy'
        }),
        'en',
        'probe',
        []
      )
    ).toBe('Hafiye @hermes ~/.hermes https://hermes-agent.nousresearch.com hermes://legacy')
  })

  it('rebrands the catalog shape consumed by React context', () => {
    const tree = rebrandTranslationTree({
      nested: {
        literal: 'Hermes is ready',
        interpolated: (count: number) => `${count} Hermes chats`
      }
    })

    expect(tree.nested.literal).toBe('Hafiye is ready')
    expect(tree.nested.interpolated(3)).toBe('3 Hafiye chats')
  })

  it('translates migrated overlap keys for newly supported locales', () => {
    setRuntimeI18nLocale('ja')
    expect(translateNow('common.save')).toBe('保存')

    setRuntimeI18nLocale('zh-hant')
    expect(translateNow('cron.promptPlaceholder')).toBe('代理每次執行時應做什麼？')
  })

  it('translates settings copy for newly supported locales', () => {
    setRuntimeI18nLocale('ja')
    expect(translateNow('settings.appearance.title')).toBe('外観')
    expect(translateNow('settings.nav.providers')).toBe('プロバイダー')

    setRuntimeI18nLocale('zh-hant')
    expect(translateNow('settings.appearance.title')).toBe('外觀')
    expect(translateNow('settings.nav.providerApiKeys')).toBe('API 金鑰')

    setRuntimeI18nLocale('ar')
    expect(translateNow('settings.appearance.reasoningCollapsedTitle')).toBe('طي التفكير افتراضيًا')
    expect(translateNow('settings.appearance.reasoningCollapsedDesc')).toBe(
      'أبقِ التفكير المتدفق متاحًا دون توسيعه حتى تفتحه.'
    )

    setRuntimeI18nLocale('tr')
    expect(translateNow('language.label')).toBe('Dil')
    expect(translateNow('settings.nav.controlCenter')).toBe('Hafiye Kontrol Merkezi')
    expect(translateNow('settings.nav.computer')).toBe('Bilgisayar')
    expect(translateNow('settings.localRuntime.title')).toBe('Yerel GGUF Çalışma Zamanı')
    expect(translateNow('settings.nav.providers')).toBe('Sağlayıcılar')
    expect(translateNow('settings.appearance.title')).toBe('Görünüm')
    expect(translateNow('settings.model.provider')).toBe('Sağlayıcı')
    expect(translateNow('composer.send')).toBe('Gönder')
    expect(translateNow('modelPicker.title')).toBe('Modeli değiştir')
  })

  it('keeps translated settings field copy addressable from schema keys', () => {
    const field = ['display', 'show_reasoning'].join('.')

    expect(fieldCopyForSchemaKey(zh.settings.fieldLabels, field)).toBe('推理过程块')
    expect(fieldCopyForSchemaKey(zh.settings.fieldDescriptions, field)).toBe('当后端提供推理内容时予以显示。')
  })

  it('falls back to English when the active locale cannot resolve a key', () => {
    const boot = TRANSLATIONS.ja.boot as { ready?: string }
    const originalReady = boot.ready

    try {
      boot.ready = undefined
      setRuntimeI18nLocale('ja')

      expect(translateNow('boot.ready')).toBe('Hafiye Desktop is ready')
    } finally {
      boot.ready = originalReady
    }
  })

  it('returns the key when no locale can resolve a path', () => {
    setRuntimeI18nLocale('zh')

    expect(translateNow('missing.path')).toBe('missing.path')
  })
})
