import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const requestGateway = vi.fn()
let taskListener: ((event: { payload?: unknown }) => void) | undefined

vi.mock('@/app/gateway/hooks/use-gateway-request', () => ({
  useGatewayRequest: () => ({ requestGateway })
}))

vi.mock('@/contrib/events', () => ({
  onGatewayEvent: vi.fn((_type: string, listener: (event: { payload?: unknown }) => void) => {
    taskListener = listener
    return () => {
      taskListener = undefined
    }
  })
}))

vi.mock('@/store/notifications', () => ({
  notifyError: vi.fn()
}))

const task = {
  created_at: 1,
  current_step_summary: 'OpenHands worker running',
  goal: 'Fix the failing test',
  model: 'gemini-flash-lite-latest',
  privacy_mode: 'NORMAL',
  progress_events: 2,
  provider: 'gemini',
  repository_path: '/tmp/fixture',
  route: 'coding',
  state: 'RUNNING',
  subagent_state: 'RUNNING',
  task_id: 'coding-1',
  tool_history: [{ event: 'ToolCallEvent', tool: 'terminal' }]
}

beforeEach(() => {
  requestGateway.mockImplementation(async (method: string) => {
    if (method === 'tasks.list') {
      return { tasks: [task] }
    }
    return { task: { ...task, state: 'CANCELLING' } }
  })
})

afterEach(() => {
  cleanup()
  taskListener = undefined
  vi.clearAllMocks()
})

describe('TaskCenterPanel', () => {
  it('renders live task progress and sends a real cancellation RPC', async () => {
    const { TaskCenterPanel } = await import('./task-center')

    render(<TaskCenterPanel />)

    expect(await screen.findByText('Fix the failing test')).toBeTruthy()
    expect(screen.getByText('Task Center')).toBeTruthy()
    expect(screen.getByTestId('task-state-active').textContent).toContain('Active 1')
    expect(screen.getByText('OpenHands worker running')).toBeTruthy()
    expect(screen.getByText('gemini / gemini-flash-lite-latest')).toBeTruthy()
    expect(screen.getByText('subagent RUNNING')).toBeTruthy()

    taskListener?.({
      payload: {
        ...task,
        current_step_summary: 'OpenHands: MessageEvent',
        state: 'RUNNING',
        task_id: task.task_id
      }
    })
    expect(await screen.findByText('OpenHands: MessageEvent')).toBeTruthy()

    fireEvent.click(screen.getByRole('button', { name: 'Cancel task' }))
    await waitFor(() => expect(requestGateway).toHaveBeenCalledWith('tasks.cancel', { task_id: 'coding-1' }))
  })
})
