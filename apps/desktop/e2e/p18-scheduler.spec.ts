import { type MockBackendFixture, setupMockBackend } from './fixtures'
import { expect, test } from './test'

let fixture: MockBackendFixture | null = null

test.describe('P18 Scheduler policy choices — real Desktop and gateway', () => {
  test.beforeAll(async () => {
    fixture = await setupMockBackend()
    await fixture.page.evaluate(() => {
      window.location.hash = '#/cron'
    })
    await expect(fixture.page.getByRole('heading', { name: 'Scheduled jobs' })).toBeVisible({ timeout: 30_000 })
  })

  test.afterAll(async () => {
    await fixture?.cleanup()
    fixture = null
  })

  test('creates a recurring job with route, privacy, and toolset choices that survive edit', async () => {
    const page = fixture!.page

    await page.getByRole('button', { name: 'New cron', exact: true }).click()
    await expect(page.getByRole('dialog')).toBeVisible()

    await page.locator('#cron-name').fill('P18 scheduler policy')
    await page.locator('#cron-prompt').fill('Run the recurring local scheduler acceptance probe.')

    await page.locator('#cron-route').click()
    await page.getByRole('option', { name: 'Coding', exact: true }).click()

    await page.locator('#cron-privacy-mode').click()
    await page.getByRole('option', { name: 'Local only', exact: true }).click()

    const defaults = page.getByRole('checkbox', { name: 'Use gateway defaults', exact: true })
    await expect(defaults).toBeChecked()
    await defaults.click()

    const customToolset = page.locator('[id^="cron-toolset-"]:not(#cron-toolsets-default)').first()
    await expect(customToolset).toBeVisible({ timeout: 30_000 })
    await customToolset.click()

    await page.getByRole('button', { name: 'Create cron', exact: true }).click()
    await expect(page.getByRole('dialog')).toBeHidden({ timeout: 30_000 })

    const row = page.locator('[data-panel-row]').filter({ hasText: 'P18 scheduler policy' })
    await expect(row).toBeVisible({ timeout: 30_000 })

    await row.getByRole('button', { name: 'Manage', exact: true }).click()
    await page.getByRole('menuitem', { name: 'Edit cron', exact: true }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.locator('#cron-route')).toContainText('Coding')
    await expect(page.locator('#cron-privacy-mode')).toContainText('Local only')
    await expect(page.getByRole('checkbox', { name: 'Use gateway defaults', exact: true })).not.toBeChecked()
    await expect(customToolset).toHaveAttribute('data-state', 'checked')
  })
})
