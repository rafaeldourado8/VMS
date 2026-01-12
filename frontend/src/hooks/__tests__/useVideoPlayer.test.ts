import { renderHook, act, waitFor } from '@testing-library/react'
import { useVideoPlayer } from '../useVideoPlayer'
import { vi } from 'vitest'

describe('useVideoPlayer', () => {
  let mockVideo: Partial<HTMLVideoElement>

  beforeEach(() => {
    mockVideo = {
      readyState: 4,
      paused: false,
      volume: 1,
      load: vi.fn(),
      play: vi.fn().mockResolvedValue(undefined),
    }
    
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('should detect stalled stream', async () => {
    const onStalled = vi.fn()
    const videoRef = { current: mockVideo as HTMLVideoElement }
    
    const { result } = renderHook(() => 
      useVideoPlayer(videoRef, { onStalled })
    )

    mockVideo.readyState = 2

    await waitFor(() => {
      expect(result.current.isStalled).toBe(true)
    }, { timeout: 6000 })
  })

  it('should limit retries to 3 per minute', async () => {
    const videoRef = { current: mockVideo as HTMLVideoElement }
    
    const { result } = renderHook(() => useVideoPlayer(videoRef))

    mockVideo.readyState = 2

    for (let i = 0; i < 4; i++) {
      act(() => {
        mockVideo.readyState = 2
      })
      await new Promise(resolve => setTimeout(resolve, 100))
    }

    await waitFor(() => {
      expect(result.current.showError).toBe(true)
    })
  })

  it('should persist volume', () => {
    const videoRef = { current: mockVideo as HTMLVideoElement }
    
    const { result } = renderHook(() => useVideoPlayer(videoRef))

    act(() => {
      result.current.setVolume(0.5)
    })

    const saved = JSON.parse(localStorage.getItem('vms_player_state') || '{}')
    expect(saved.volume).toBe(0.5)
  })

  it('should persist quality', () => {
    const videoRef = { current: mockVideo as HTMLVideoElement }
    
    const { result } = renderHook(() => useVideoPlayer(videoRef))

    act(() => {
      result.current.setQuality('720p')
    })

    const saved = JSON.parse(localStorage.getItem('vms_player_state') || '{}')
    expect(saved.quality).toBe('720p')
  })

  it('should allow manual retry', async () => {
    const videoRef = { current: mockVideo as HTMLVideoElement }
    
    const { result } = renderHook(() => useVideoPlayer(videoRef))

    mockVideo.readyState = 2
    for (let i = 0; i < 4; i++) {
      act(() => {
        mockVideo.readyState = 2
      })
      await new Promise(resolve => setTimeout(resolve, 100))
    }

    await waitFor(() => {
      expect(result.current.showError).toBe(true)
    })

    act(() => {
      result.current.manualRetry()
    })

    expect(result.current.showError).toBe(false)
  })
})
