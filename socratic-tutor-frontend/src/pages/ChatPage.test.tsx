import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ChatPage } from './ChatPage'
import { ThemeProvider } from '../components/ThemeProvider'
import * as chatService from '../services/chatService'

vi.mock('../services/chatService', async () => {
  const actual = await vi.importActual<typeof chatService>('../services/chatService')
  return {
    ...actual,
    getSessions: vi.fn(),
    getSessionMessages: vi.fn(),
    sendMessage: vi.fn(),
    sendMessageStream: vi.fn(),
  }
})

vi.mock('../services/subjectService', () => ({
  getSubjects: vi.fn().mockResolvedValue([]),
  createSubject: vi.fn(),
  getMaterials: vi.fn(),
  uploadMaterial: vi.fn(),
  deleteMaterial: vi.fn(),
  deleteSubject: vi.fn(),
}))

function renderChatPage() {
  return render(
    <ThemeProvider>
      <ChatPage />
    </ThemeProvider>,
  )
}

describe('ChatPage', () => {
  beforeEach(() => {
    vi.mocked(chatService.getSessions).mockResolvedValue({
      sessions: [
        {
          id: 'session-1',
          title: 'Biology',
          created_at: '2026-01-01T00:00:00Z',
          last_updated_at: '2026-01-01T00:00:00Z',
          message_count: 0,
          last_message_preview: 'No messages',
        },
      ],
    })
    vi.mocked(chatService.getSessionMessages).mockResolvedValue({
      session_id: 'session-1',
      messages: [],
    })
    vi.mocked(chatService.sendMessageStream).mockImplementation(async (_request, handlers) => {
      handlers.onToken('What do you already know about photosynthesis?')
      handlers.onDone({
        session_id: 'session-1',
        reply_message: {
          id: 'reply-1',
          role: 'assistant',
          content: 'What do you already know about photosynthesis?',
        },
      })
    })
  })

  it('renders and shows an optimistic user message after sending', async () => {
    const user = userEvent.setup()
    renderChatPage()

    await waitFor(() => {
      expect(chatService.getSessions).toHaveBeenCalled()
    })

    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Help me with photosynthesis{enter}')

    const main = screen.getByRole('main')
    expect(within(main).getByText('Help me with photosynthesis')).toBeInTheDocument()

    await waitFor(() => {
      expect(chatService.sendMessageStream).toHaveBeenCalled()
      expect(
        within(main).getByText('What do you already know about photosynthesis?'),
      ).toBeInTheDocument()
    })
  })
})
