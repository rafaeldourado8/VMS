import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MosaicosPage } from '../MosaicosPage'
import { cameraService } from '@/services/api'
import { vi } from 'vitest'

vi.mock('@/services/api', () => ({
  mosaicoService: {
    list: vi.fn(),
    delete: vi.fn(),
  },
  cameraService: {
    list: vi.fn(),
    getStream: vi.fn(),
  },
  streamingService: {
    getHlsUrl: vi.fn((id) => `http://localhost:8889/camera${id}/index.m3u8`),
  },
}))

vi.mock('@/components/cameras/VideoPlayer', () => ({
  VideoPlayer: ({ src }: { src: string }) => <div data-testid="video-player">{src}</div>,
}))

const createQueryClient = () => new QueryClient({
  defaultOptions: { queries: { retry: false } },
})

describe('MosaicosPage - Stream Limits', () => {
  it('should show error when API returns 429', async () => {
    const queryClient = createQueryClient()

    vi.mocked(cameraService.getStream).mockRejectedValue({
      response: {
        status: 429,
        data: { max_streams: 2 },
      },
    })

    render(
      <QueryClientProvider client={queryClient}>
        <MosaicosPage />
      </QueryClientProvider>
    )

    const startButton = screen.getByText('Iniciar')
    fireEvent.click(startButton)

    await waitFor(() => {
      expect(screen.getByText('Limite de 2 streams atingido')).toBeInTheDocument()
    })
  })

  it('should prevent opening more streams after limit', async () => {
    const queryClient = createQueryClient()
    
    vi.mocked(cameraService.getStream)
      .mockResolvedValueOnce({ stream_url: 'rtsp://test1' })
      .mockResolvedValueOnce({ stream_url: 'rtsp://test2' })

    render(
      <QueryClientProvider client={queryClient}>
        <MosaicosPage />
      </QueryClientProvider>
    )

    const startButtons = screen.getAllByText('Iniciar')
    
    fireEvent.click(startButtons[0])
    fireEvent.click(startButtons[1])

    await waitFor(() => {
      expect(cameraService.getStream).toHaveBeenCalledTimes(2)
    })

    fireEvent.click(startButtons[2])

    await waitFor(() => {
      expect(screen.getByText(/Limite de \d+ streams atingido/)).toBeInTheDocument()
    })
  })
})
