import { expect, test } from './test'

import { setupMockBackend, type MockBackendFixture } from './fixtures'

let fixture: MockBackendFixture | null = null

test.beforeAll(async () => {
  fixture = await setupMockBackend({
    extraEnv: {
      // The real backend owns this gate. It makes the packaged-only wizard
      // visible in the isolated Electron acceptance sandbox without replacing
      // any onboarding REST or host-probe implementation.
      HAFIYE_ONBOARDING_FORCE: '1'
    }
  })
})

test.afterAll(async () => {
  await fixture?.cleanup()
  fixture = null
})

test('real Electron onboarding advances through environment and computer checks', async () => {
  const page = fixture!.page

  await expect(page.getByRole('heading', { name: 'Hafiye’ye hoş geldiniz' })).toBeVisible({ timeout: 90_000 })
  await page.getByRole('button', { name: 'Kuruluma başla' }).click()

  await expect(page.getByRole('heading', { name: 'Linux ortamını doğrula' })).toBeVisible()
  await expect(page.getByText('Kernel')).toBeVisible()
  await page.getByRole('button', { name: 'Ortamı doğrula ve devam et' }).click()

  await expect(page.getByRole('heading', { name: 'Masaüstü kontrolünü doğrula' })).toBeVisible({ timeout: 30_000 })
  await page.getByRole('button', { name: 'Doctor sonucunu doğrula' }).click()

  await expect(page.getByRole('heading', { name: 'Hesaplama backend’ini seç' })).toBeVisible({ timeout: 30_000 })
})
