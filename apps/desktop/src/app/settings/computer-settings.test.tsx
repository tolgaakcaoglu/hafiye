import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const getComputerUseStatus = vi.fn()

vi.mock('@/hermes', () => ({
  getComputerUseStatus: () => getComputerUseStatus()
}))

vi.mock('@/store/notifications', () => ({
  notifyError: vi.fn()
}))

beforeEach(() => {
  getComputerUseStatus.mockResolvedValue({
    backend: 'computer-use-linux',
    binary: '/home/tolga/.local/bin/computer-use-linux',
    blockers: [],
    checks: [],
    error: null,
    installed: true,
    mcp_configured: true,
    mcp_server: 'hafiye-computer-use-linux',
    platform: 'linux',
    platform_supported: true,
    readiness: {
      can_build_accessibility_tree: true,
      can_query_windows: true,
      can_register_mcp_tools: true,
      can_send_development_input: true
    },
    ready: true,
    screen_recording: null,
    screen_recording_capturable: null,
    source: null,
    source_commit: '94736dc3e0dca56acfc89752c26869fb9ed01202',
    accessibility: true,
    version: 'source 94736dc3e0dc'
  })
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('ComputerSettings', () => {
  it('renders the managed Linux readiness and MCP diagnostics', async () => {
    const { ComputerSettings } = await import('./computer-settings')

    render(<ComputerSettings />)

    expect(await screen.findByText('Ready')).toBeTruthy()
    expect(screen.getByText('computer-use-linux')).toBeTruthy()
    expect(screen.getByText(/MCP server:/).textContent).toContain('hafiye-computer-use-linux')
    expect(screen.getByText('can_register_mcp_tools')).toBeTruthy()
    expect(screen.getByText('can_build_accessibility_tree')).toBeTruthy()
    expect(screen.getByText('can_send_development_input')).toBeTruthy()
    expect(screen.getByText('can_query_windows')).toBeTruthy()
    expect(screen.getAllByText('true')).toHaveLength(4)
  })
})
