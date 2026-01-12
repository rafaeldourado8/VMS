import { render, screen, waitFor } from '@testing-library/react'
import { CameraGrid } from '../CameraGrid'
import { cameraService } from '@/services/api'
import { vi } from 'vitest'

vi.mock('@/services/api', () => ({
  cameraService: {
    getStream: vi.fn(),
  },
}))

vi.mock('@/store/cameraStore', () => ({
  useCameraStore: () => ({
    gridLayout: 4,
    setGridLayout: vi.fn(),
  }),
}))

const mockCameras = [
  { id: 1, name: 'Camera 1', status: 'online' },
  { id: 2, name: 'Camera 2', status: 'online' },
]

describe('CameraGrid - Graceful Degradation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should show MediaMTX down message', async () => {
    vi.mocked(cameraService.getStream).mockRejectedValue({
      response: { status: 503 },
    })

    render(<CameraGrid cameras={mockCameras} />)

    await waitFor(() => {
      expect(screen.getByText(/Servidor de streaming indisponível/)).toBeInTheDocument()
    })
  })

  it('should show maintenance message when all cameras offline', async () => {
    vi.mocked(cameraService.getStream).mockRejectedValue({
      response: { status: 500 },
    })

    render(<CameraGrid cameras={mockCameras} />)

    await waitFor(() => {
      expect(screen.getByText(/Sistema em manutenção/)).toBeInTheDocument()
    })
  })

  it('should show reconnecting overlay for offline camera', async () => {
    vi.mocked(cameraService.getStream)
      .mockResolvedValueOnce({ stream_url: 'http://test' })
      .mockRejectedValueOnce({ response: { status: 500 } })

    render(<CameraGrid cameras={mockCameras} />)

    await waitFor(() => {
      expect(screen.getByText(/Reconectando.../)).toBeInTheDocument()
    })
  })

  it('should show retry button for offline camera', async () => {
    vi.mocked(cameraService.getStream).mockRejectedValue({
      response: { status: 500 },
    })

    render(<CameraGrid cameras={mockCameras} />)

    await waitFor(() => {
      expect(screen.getByText(/Tentar novamente/)).toBeInTheDocument()
    })
  })
})
