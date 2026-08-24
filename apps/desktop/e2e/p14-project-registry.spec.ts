import { execFileSync } from 'node:child_process'
import * as fs from 'node:fs'
import * as path from 'node:path'

import {
  buildAppEnv,
  createSandbox,
  launchDesktop,
  type MockBackendFixture,
  waitForAppReady,
  writeEnvFile,
  writeMockProviderConfig
} from './fixtures'
import { startMockServer } from './mock-server'
import { expect, test } from './test'

const DESKTOP_ROOT = path.resolve(import.meta.dirname, '..')
const REPO_ROOT = path.resolve(DESKTOP_ROOT, '..', '..')
const PYTHON = path.join(REPO_ROOT, '.venv', 'bin', 'python')

function createGitRepo(root: string, name: string): string {
  const repo = path.join(root, name)

  fs.mkdirSync(repo, { recursive: true })
  execFileSync('git', ['init', '--initial-branch=main'], { cwd: repo, stdio: 'ignore' })
  execFileSync('git', ['config', 'user.email', 'p14-e2e@example.com'], { cwd: repo, stdio: 'ignore' })
  execFileSync('git', ['config', 'user.name', 'Hafiye P14 E2E'], { cwd: repo, stdio: 'ignore' })
  fs.writeFileSync(path.join(repo, 'README.md'), `# ${name}\n`, 'utf8')
  execFileSync('git', ['add', 'README.md'], { cwd: repo, stdio: 'ignore' })
  execFileSync('git', ['commit', '-m', 'initial'], { cwd: repo, stdio: 'ignore' })

  return repo
}

function seedProjects(hermesHome: string, pocketWorldRepo: string, otherRepo: string): void {
  const script = `
import os

from hermes_cli import projects_db as pdb

with pdb.connect_closing() as conn:
    pdb.create_project(conn, name="Pocket World", folders=[os.environ["P14_POCKET_REPO"]])
    pdb.create_project(conn, name="Other Project", folders=[os.environ["P14_OTHER_REPO"]])
`

  execFileSync(PYTHON, ['-c', script], {
    cwd: REPO_ROOT,
    env: {
      ...process.env,
      HERMES_HOME: hermesHome,
      P14_OTHER_REPO: otherRepo,
      P14_POCKET_REPO: pocketWorldRepo,
      PYTHONPATH: REPO_ROOT
    },
    stdio: 'pipe'
  })
}

function assertProjectDatabaseAfterDelete(hermesHome: string): void {
  const script = `
from hermes_cli import projects_db as pdb

with pdb.connect_closing() as conn:
    names = [project.name for project in pdb.list_projects(conn)]
    assert names == ["Other Project"], names
print("P14_GUI_PROJECT_DB_OK")
`

  const output = execFileSync(PYTHON, ['-c', script], {
    cwd: REPO_ROOT,
    env: { ...process.env, HERMES_HOME: hermesHome, PYTHONPATH: REPO_ROOT },
    encoding: 'utf8'
  })

  if (!output.includes('P14_GUI_PROJECT_DB_OK')) {
    throw new Error(`Unexpected project database verification output: ${output}`)
  }
}

let fixture: MockBackendFixture | null = null

test.describe('P14 project registry — real Desktop and gateway', () => {
  test.beforeAll(async () => {
    const sandbox = createSandbox('p14-project-registry')
    const pocketWorldRepo = createGitRepo(sandbox.root, 'pocket-world')
    const otherRepo = createGitRepo(sandbox.root, 'other-project')
    const mock = await startMockServer()

    writeMockProviderConfig(sandbox.hermesHome, mock.url)
    fs.appendFileSync(path.join(sandbox.hermesHome, 'config.yaml'), `\nterminal:\n  cwd: ${pocketWorldRepo}\n`, 'utf8')
    writeEnvFile(sandbox.hermesHome)
    seedProjects(sandbox.hermesHome, pocketWorldRepo, otherRepo)

    const { app, page } = await launchDesktop(buildAppEnv(sandbox))
    fixture = {
      app,
      page,
      mock,
      mockUrl: mock.url,
      sandbox,
      cleanup: async () => {
        await app.close().catch(() => undefined)
        await mock.close()
        sandbox.cleanup()
      }
    }

    await waitForAppReady(fixture, 120_000)

    // Give the real gateway one repo-backed session so the coding/worktree
    // surface is mounted for the project-search part of this acceptance flow.
    const prompt = 'P14_GUI_PROJECT_BOOT'
    const composer = page.locator('[contenteditable="true"]').first()
    await composer.click()
    await composer.type(prompt, { delay: 2 })
    await page.keyboard.press('Enter')
    await page.waitForFunction(text => (document.body.textContent ?? '').includes(text), prompt, { timeout: 30_000 })
  })

  test.afterAll(async () => {
    await fixture?.cleanup()
    fixture = null
  })

  test('browses, searches, renames, and deletes a persistent project', async () => {
    const page = fixture!.page

    // Select the real Project grouping in the sidebar filter. The project rows
    // below are rendered from the gateway's projects.tree response.
    await page.getByRole('button', { name: 'Filters' }).click()
    await page.getByRole('menuitem', { name: 'Grouping' }).hover()
    await page.getByRole('menuitemradio', { name: 'Project' }).click()

    const projectRows = page.locator('[data-sessions-project]')
    const pocketRow = projectRows.filter({ hasText: 'Pocket World' }).first()
    await expect(pocketRow).toBeVisible({ timeout: 30_000 })
    await expect(projectRows.filter({ hasText: 'Other Project' }).first()).toBeVisible()

    // The worktree dialog exposes the deterministic project registry through a
    // real searchable project picker, backed by the same project tree.
    await page.keyboard.press('Control+Shift+B')
    const worktreeDialog = page.locator('[data-slot="dialog-content"]')
    await expect(worktreeDialog).toBeVisible()
    await worktreeDialog.getByRole('button').filter({ hasText: 'Pocket World' }).click()

    const projectSearch = page.getByPlaceholder('Search projects…')
    await expect(projectSearch).toBeVisible()
    await projectSearch.fill('Other Project')
    await expect(page.getByRole('option', { name: /Other Project/ })).toBeVisible()
    await expect(page.getByRole('option', { name: /Pocket World/ })).toHaveCount(0)
    // Command's root owns pointer hit-testing for its portalled option list;
    // Enter is the deterministic selection path used by the existing worktree
    // E2E coverage as well.
    await page.keyboard.press('Enter')
    await expect(worktreeDialog.getByRole('button').filter({ hasText: 'Other Project' })).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(worktreeDialog).toHaveCount(0)

    // Rename through the actual row action and the real projects.update RPC.
    await pocketRow.locator('button[aria-label="Open Pocket World"]').click({ button: 'right', force: true })
    await page.getByRole('menuitem', { name: 'Rename', exact: true }).click()
    const renameDialog = page.locator('[data-slot="dialog-content"]')
    await expect(renameDialog).toContainText('Rename project')
    await renameDialog.getByPlaceholder('e.g. Skunkworks').fill('Pocket World Renamed')
    await renameDialog.getByRole('button', { name: 'Save', exact: true }).click()

    const renamedRow = projectRows.filter({ hasText: 'Pocket World Renamed' }).first()
    await expect(renamedRow).toBeVisible({ timeout: 15_000 })
    await expect(page.locator('button[aria-label="Open Pocket World"]')).toHaveCount(0)

    // Delete through the destructive confirmation. The repository directory
    // must remain on disk; projects.db owns metadata, not user files.
    await renamedRow.locator('button[aria-label="Open Pocket World Renamed"]').click({ button: 'right', force: true })
    await page.getByRole('menuitem', { name: /^Delete/ }).click()
    const deleteDialog = page.locator('[data-slot="dialog-content"]').filter({ hasText: 'Pocket World Renamed' })
    await expect(deleteDialog).toContainText('Delete')
    await deleteDialog.getByRole('button', { name: 'Delete', exact: true }).click()
    await expect(projectRows.filter({ hasText: 'Pocket World Renamed' })).toHaveCount(0, { timeout: 15_000 })

    expect(fs.existsSync(path.join(fixture!.sandbox.root, 'pocket-world'))).toBe(true)
    assertProjectDatabaseAfterDelete(fixture!.sandbox.hermesHome)
  })
})
