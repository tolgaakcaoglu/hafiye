import { execFileSync } from 'node:child_process'
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

function seedTaskCenter(hermesHome: string): void {
  const script = `
from tools.task_center import TaskCenterRegistry

registry = TaskCenterRegistry()
registry.create(
    task_id="p16-completed",
    goal="Persisted completed task",
    provider="mock",
    model="mock-model",
    route="coding",
    repository_path="/tmp/p16-repository",
)
registry.update(
    "p16-completed",
    state="RUNNING",
    current_step_summary="Running verification",
    event_name="ToolCallEvent",
    tool_name="terminal",
    source="openhands",
    command="pytest -q",
)
registry.update(
    "p16-completed",
    state="COMPLETED",
    current_step_summary="Verification completed",
    result_summary="1 passed",
    changed_files=["bug.py"],
)
registry.create(
    task_id="p16-failed",
    goal="Persisted failed task",
    provider="mock",
    model="mock-model",
    route="coding",
)
registry.update(
    "p16-failed",
    state="FAILED",
    current_step_summary="Worker failed",
    error="fixture failure",
)
registry.create(
    task_id="p16-queued",
    goal="Queued task to cancel",
    provider="mock",
    model="mock-model",
    route="coding",
)
`

  execFileSync(PYTHON, ['-c', script], {
    cwd: REPO_ROOT,
    env: {
      ...process.env,
      HERMES_HOME: hermesHome,
      PYTHONPATH: REPO_ROOT
    },
    stdio: 'pipe'
  })
}

let fixture: MockBackendFixture | null = null

test.describe('P16 Task Center — real Desktop and gateway', () => {
  test.beforeAll(async () => {
    const sandbox = createSandbox('p16-task-center')
    const mock = await startMockServer()

    writeMockProviderConfig(sandbox.hermesHome, mock.url)
    writeEnvFile(sandbox.hermesHome)
    seedTaskCenter(sandbox.hermesHome)

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
  })

  test.afterAll(async () => {
    await fixture?.cleanup()
    fixture = null
  })

  test('renders persisted states and cancels a queued task through the gateway', async () => {
    const page = fixture!.page

    await page.evaluate(() => {
      window.location.hash = '#/command-center?section=maintenance'
    })

    const taskCenter = page.getByTestId('task-center')
    await expect(taskCenter).toBeVisible({ timeout: 30_000 })
    await expect(taskCenter.getByTestId('task-state-active')).toContainText('Active 1')
    await expect(taskCenter.getByTestId('task-state-queued')).toContainText('Queued 1')
    await expect(taskCenter.getByTestId('task-state-completed')).toContainText('Completed 1')
    await expect(taskCenter.getByTestId('task-state-failed')).toContainText('Failed 1')

    await expect(taskCenter.getByTestId('task-row-p16-completed')).toContainText('1 passed')
    await expect(taskCenter.getByTestId('task-row-p16-completed')).toContainText('bug.py')
    await expect(taskCenter.getByTestId('task-row-p16-completed')).toContainText('mock / mock-model')
    await expect(taskCenter.getByTestId('task-row-p16-failed')).toContainText('fixture failure')

    const queuedRow = taskCenter.getByTestId('task-row-p16-queued')
    await queuedRow.getByRole('button', { name: 'Cancel task' }).click()
    await expect(queuedRow).toContainText('CANCELLED')
    await expect(taskCenter.getByTestId('task-state-active')).toContainText('Active 0')
    await expect(taskCenter.getByTestId('task-state-queued')).toContainText('Queued 0')
  })
})
