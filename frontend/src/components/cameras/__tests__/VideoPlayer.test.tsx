import { render, screen, waitFor } from '@testing-library/react'
import { VideoPlayer } from '../VideoPlayer'
import { vi } from 'vitest'

vi.mock('hls.js', () => ({
  default: class MockHls {
    static isSupported = () => true
    static Events = {
      MANIFEST_PARSED: 'hlsManifestParsed',
      ERROR: 'hlsError',
    }
    static ErrorTypes = {
      NETWORK_ERROR: 'networkError',
      MEDIA_ERROR: 'mediaError',
    }
    static ErrorDetails = {
      MANIFEST_LOAD_ERROR: 'manifestLoadError',
    }
    loadSource = vi.fn()
    attachMedia = vi.fn()
    on = vi.fn()
    destroy = vi.fn()
  },
}))

describe('VideoPlayer - Protocol Failover', () => {
  it('should show HLS indicator', async () => {
    render(<VideoPlayer src="http://test.com/stream.m3u8" />)
    
    await waitFor(() => {
      expect(screen.getByText(/Modo Compatível/)).toBeInTheDocument()
    })
  })

  it('should show RTMP indicator', async () => {
    render(<VideoPlayer src="rtmp://test.com/stream" />)
    
    await waitFor(() => {
      expect(screen.getByText(/RTMP/)).toBeInTheDocument()
    })
  })

  it('should call onProtocolSwitch', async () => {
    const onProtocolSwitch = vi.fn()
    
    render(
      <VideoPlayer 
        src="http://test.com/webrtc/stream" 
        onProtocolSwitch={onProtocolSwitch}
      />
    )
    
    await waitFor(() => {
      expect(onProtocolSwitch).toHaveBeenCalledWith('webrtc', 'hls')
    }, { timeout: 6000 })
  })
})
