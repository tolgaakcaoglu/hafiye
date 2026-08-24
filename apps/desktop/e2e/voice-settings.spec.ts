/** Real Electron smoke test for the P11 Voice settings surface. */
import * as fs from 'node:fs'
import * as os from 'node:os'
import * as path from 'node:path'

import { expect, test } from './test'

import { setupMockBackend, waitForAppReady, type MockBackendFixture } from './fixtures'

let fixture: MockBackendFixture | null = null

test.beforeAll(async () => {
  fixture = await setupMockBackend({
    extraConfig: `tts:
  provider: piper
  piper:
    runtime: managed
    voice: tr_TR-dfki-medium`,
    extraEnv: { HAFIYE_DESKTOP_DISABLE_PERSISTENT_GATEWAY: '1' }
  })

  const managedPiper = path.join(os.homedir(), '.local', 'share', 'hafiye', 'runtimes', 'piper')
  const sandboxPiper = path.join(fixture.sandbox.hermesHome, 'runtimes', 'piper')
  fs.mkdirSync(path.dirname(sandboxPiper), { recursive: true })
  fs.symlinkSync(managedPiper, sandboxPiper, 'dir')

  await waitForAppReady(fixture, 120_000)
})

test.afterAll(async () => {
  await fixture?.cleanup()
  fixture = null
})

test('Voice settings expose microphone selection and managed Piper voice controls', async () => {
  const page = fixture!.page

  await page.getByRole('button', { name: 'Open settings' }).click()
  await page.getByRole('button', { name: 'Voice', exact: true }).click()

  await expect(page.getByText('Microphone input', { exact: true })).toBeVisible()
  await expect(page.getByText('Piper voice', { exact: true })).toBeVisible()
  await expect(page.getByRole('combobox', { name: 'Microphone input device' })).toBeVisible()
  const piperSelect = page.getByRole('combobox', { name: 'Piper Turkish voice' })
  await expect(piperSelect).toBeVisible()
  await piperSelect.selectOption('tr_TR-dfki-medium')
  await expect(piperSelect).toHaveValue('tr_TR-dfki-medium')
  await page.getByRole('button', { name: 'Preview', exact: true }).click()
  await expect(page.locator('audio')).toHaveAttribute('src', /^data:audio\/wav;base64,/)
})
