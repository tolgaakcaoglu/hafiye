import { type MockBackendFixture, setupMockBackend } from './fixtures'
import { expect, test } from './test'

let fixture: MockBackendFixture | null = null

const PAGES = [
  ['overview', 'Overview'],
  ['chat', 'Chat'],
  ['tasks', 'Tasks'],
  ['models', 'Models'],
  ['providers', 'Providers'],
  ['routing', 'Routing'],
  ['voice', 'Voice'],
  ['computer', 'Computer'],
  ['browser', 'Browser'],
  ['coding', 'Coding'],
  ['memory', 'Memory'],
  ['skills', 'Skills'],
  ['mcp', 'MCP'],
  ['automation', 'Automation'],
  ['permissions', 'Permissions'],
  ['privacy', 'Privacy'],
  ['logs', 'Logs'],
  ['developer', 'Developer'],
  ['about', 'About']
] as const

test.describe('P17 Control Center — real Desktop and gateway', () => {
  test.beforeAll(async () => {
    fixture = await setupMockBackend()
    await fixture.page.evaluate(() => {
      window.location.hash = '#/control-center?page=overview'
    })
    await expect(fixture.page.getByTestId('control-center-page-title')).toHaveText('Overview', { timeout: 30_000 })
  })

  test.afterAll(async () => {
    await fixture?.cleanup()
    fixture = null
  })

  test('exposes every roadmap page and keeps config changes real across reload', async () => {
    const page = fixture!.page
    const nav = page.locator('[data-tour="overlay-nav"]')

    await expect(nav).toBeVisible()

    for (const [id, label] of PAGES) {
      await expect(nav.locator(`[data-tour="nav-${id}"]`)).toBeVisible()
      await nav.getByRole('button', { name: label, exact: true }).click()
      await expect(page.getByTestId('control-center-page-title')).toHaveText(label, { timeout: 30_000 })

      if (id === 'models') {
        await expect(page.locator('[data-slot="local-runtime-settings"]')).toBeVisible({ timeout: 30_000 })
        await expect(page.getByRole('button', { name: 'Download GGUF', exact: true })).toBeVisible()
        await expect(page.getByRole('textbox', { name: 'Hugging Face repository' })).toBeVisible()
      }
    }

    await nav.getByRole('button', { name: 'Privacy', exact: true }).click()
    await expect(page.getByTestId('control-center-page-title')).toHaveText('Privacy')

    const privacyRow = page.locator('[data-tour="field-hafiye.privacy_mode"]')
    const privacySelect = privacyRow.getByRole('combobox')
    await expect(privacySelect).toBeVisible({ timeout: 30_000 })
    await privacySelect.click()
    await page.getByRole('option', { name: 'LOCAL ONLY', exact: true }).click()
    await expect(privacySelect).toContainText('LOCAL ONLY')

    // ConfigSettings autosaves to the real gateway config; reload the actual
    // Electron renderer and verify the value comes back from that backend.
    await page.waitForTimeout(900)
    await page.reload()
    await page.waitForSelector('[data-tour="overlay-nav"]', { timeout: 30_000 })
    await expect(page.getByTestId('control-center-page-title')).toHaveText('Privacy', { timeout: 30_000 })
    await expect(page.locator('[data-tour="field-hafiye.privacy_mode"]').getByRole('combobox')).toContainText('LOCAL ONLY')
  })
})
