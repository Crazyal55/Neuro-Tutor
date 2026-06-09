import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { sendMessage } from './chatService'

describe('chatService', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('sends chat requests to the configured API endpoint', async () => {
    const mockResponse = {
      session_id: 'session-1',
      reply_message: {
        id: 'reply-1',
        role: 'assistant',
        content: 'What do you already know about photosynthesis?',
      },
    }

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    } as Response)

    const result = await sendMessage({
      messages: [
        {
          id: 'msg-1',
          role: 'user',
          content: 'Help me with photosynthesis',
        },
      ],
      preferences: {
        verbosity_level: 3,
        explanation_style: 'step_by_step',
        reading_mode: 'comfortable',
        visual_aids: true,
      },
    })

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/chat/'),
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    expect(result).toEqual(mockResponse)
  })

  it('maps network failures to a friendly message', async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError('Failed to fetch'))

    await expect(
      sendMessage({
        messages: [{ id: 'msg-1', role: 'user', content: 'Hello' }],
      }),
    ).rejects.toThrow(
      "I'm having trouble connecting to my brain right now. Please check your internet connection and try again.",
    )
  })

  it('maps server errors to a friendly message', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ detail: 'Internal server error' }),
    } as Response)

    await expect(
      sendMessage({
        messages: [{ id: 'msg-1', role: 'user', content: 'Hello' }],
      }),
    ).rejects.toThrow(
      "I seem to have hit a mental roadblock. Let's try that question again in a different way.",
    )
  })

  it('maps rate limit errors to a friendly message', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 429,
      json: async () => ({ detail: 'Rate limit exceeded' }),
    } as Response)

    await expect(
      sendMessage({
        messages: [{ id: 'msg-1', role: 'user', content: 'Hello' }],
      }),
    ).rejects.toThrow(
      "Whoa, slow down there! My brain needs a moment to catch up. Let's try again in a few seconds.",
    )
  })
})
