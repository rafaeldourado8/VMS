# VMS — RTSP Flow: From Camera to MediaMTX

## Complete RTSP to HLS Pipeline

```mermaid
graph TB
    subgraph "IP Camera"
        CamSensor[Image Sensor]
        CamEncoder[H.264 Encoder]
        CamRTSP[RTSP Server]
    end

    subgraph "Network"
        TCP[TCP Connection]
        RTP[RTP/RTCP Packets]
    end

    subgraph "MediaMTX Server"
        RTSPClient[RTSP Client]
        Demuxer[Stream Demuxer]
        Buffer[Frame Buffer]
        HLSMuxer[HLS Muxer]
        Segmenter[Segment Writer]
        Storage[Segment Storage]
    end

    subgraph "Output"
        Manifest[index.m3u8]
        Segments[seg_N.mp4]
    end

    CamSensor -->|Raw Frames| CamEncoder
    CamEncoder -->|H.264 NAL Units| CamRTSP
    CamRTSP -->|RTSP Protocol| TCP
    TCP -->|DESCRIBE/SETUP/PLAY| RTSPClient
    RTSPClient -->|RTP Stream| RTP
    RTP -->|Video Packets| Demuxer
    Demuxer -->|Decoded Frames| Buffer
    Buffer -->|Buffered Stream| HLSMuxer
    HLSMuxer -->|4s Segments| Segmenter
    Segmenter -->|Write fMP4| Storage
    Storage -->|Update| Manifest
    Storage -->|Serve| Segments

    style CamSensor fill:#fff9c4
    style CamEncoder fill:#fff9c4
    style CamRTSP fill:#fff9c4
    style RTSPClient fill:#f3e5f5
    style HLSMuxer fill:#f3e5f5
    style Manifest fill:#e1f5ff
    style Segments fill:#e1f5ff
```

## RTSP Protocol Flow

### 1. Connection Establishment

```mermaid
sequenceDiagram
    participant MediaMTX as MediaMTX RTSP Client
    participant Camera as IP Camera RTSP Server

    Note over MediaMTX,Camera: PHASE 1: DESCRIBE (Get Stream Info)
    MediaMTX->>Camera: DESCRIBE rtsp://192.168.1.100:554/stream1
    Note right of MediaMTX: Request: What streams are available?
    Camera->>MediaMTX: 200 OK + SDP
    Note left of Camera: Response: H.264 video, AAC audio<br/>Resolution: 1920x1080<br/>Framerate: 25 fps

    Note over MediaMTX,Camera: PHASE 2: SETUP (Configure Transport)
    MediaMTX->>Camera: SETUP rtsp://.../stream1/trackID=0<br/>Transport: RTP/AVP/TCP;interleaved=0-1
    Note right of MediaMTX: Request: Use TCP for video track
    Camera->>MediaMTX: 200 OK<br/>Session: 12345678<br/>Transport: RTP/AVP/TCP;interleaved=0-1
    Note left of Camera: Response: Session created<br/>TCP interleaved mode

    MediaMTX->>Camera: SETUP rtsp://.../stream1/trackID=1<br/>Transport: RTP/AVP/TCP;interleaved=2-3
    Note right of MediaMTX: Request: Use TCP for audio track
    Camera->>MediaMTX: 200 OK<br/>Session: 12345678<br/>Transport: RTP/AVP/TCP;interleaved=2-3

    Note over MediaMTX,Camera: PHASE 3: PLAY (Start Streaming)
    MediaMTX->>Camera: PLAY rtsp://.../stream1<br/>Session: 12345678<br/>Range: npt=0.000-
    Note right of MediaMTX: Request: Start sending media
    Camera->>MediaMTX: 200 OK<br/>RTP-Info: url=.../trackID=0;seq=1234;rtptime=5678
    Note left of Camera: Response: Streaming started

    Note over MediaMTX,Camera: PHASE 4: STREAMING (Continuous)
    loop Every frame
        Camera->>MediaMTX: RTP Packet (Video H.264)
        Camera->>MediaMTX: RTP Packet (Audio AAC)
    end

    Note over MediaMTX,Camera: PHASE 5: KEEPALIVE (Every 30s)
    loop Every 30 seconds
        MediaMTX->>Camera: GET_PARAMETER rtsp://.../stream1<br/>Session: 12345678
        Camera->>MediaMTX: 200 OK
    end

    Note over MediaMTX,Camera: PHASE 6: TEARDOWN (Stop Streaming)
    MediaMTX->>Camera: TEARDOWN rtsp://.../stream1<br/>Session: 12345678
    Note right of MediaMTX: Request: Stop and close session
    Camera->>MediaMTX: 200 OK
    Note left of Camera: Response: Session closed
```

## SDP (Session Description Protocol) Example

When MediaMTX sends `DESCRIBE`, the camera responds with SDP:

```
v=0
o=- 1234567890 1234567890 IN IP4 192.168.1.100
s=RTSP Session
c=IN IP4 0.0.0.0
t=0 0
a=control:*
a=range:npt=0-

m=video 0 RTP/AVP 96
a=rtpmap:96 H264/90000
a=fmtp:96 packetization-mode=1;profile-level-id=64001f;sprop-parameter-sets=Z2QAH6zZQPAR,aO48gA==
a=control:trackID=0

m=audio 0 RTP/AVP 97
a=rtpmap:97 MPEG4-GENERIC/16000/1
a=fmtp:97 streamtype=5;profile-level-id=1;mode=AAC-hbr;sizelength=13;indexlength=3;indexdeltalength=3;config=1408
a=control:trackID=1
```

**Key Information Extracted**:
- **Video Codec**: H.264 (payload type 96)
- **Video Profile**: High Profile Level 3.1
- **Clock Rate**: 90000 Hz
- **Audio Codec**: AAC (payload type 97)
- **Sample Rate**: 16000 Hz
- **Tracks**: trackID=0 (video), trackID=1 (audio)

## RTP Packet Structure

### RTP Header (12 bytes)
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|V=2|P|X|  CC   |M|     PT      |       Sequence Number         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Timestamp                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Synchronization Source (SSRC) identifier            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**Fields**:
- **V**: Version (2)
- **P**: Padding
- **X**: Extension
- **CC**: CSRC count
- **M**: Marker (end of frame)
- **PT**: Payload Type (96 for H.264)
- **Sequence Number**: Incremental packet counter
- **Timestamp**: RTP timestamp (90kHz for video)
- **SSRC**: Stream identifier

### H.264 RTP Payload

```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| RTP Header (12 bytes)                                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| NAL Unit Type | H.264 Payload Data...                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**NAL Unit Types**:
- **1**: Non-IDR slice (P-frame)
- **5**: IDR slice (I-frame, keyframe)
- **7**: SPS (Sequence Parameter Set)
- **8**: PPS (Picture Parameter Set)

## MediaMTX Processing Pipeline

### 1. RTSP Client Module

```go
// Pseudo-code representation
type RTSPClient struct {
    url         string
    session     string
    tracks      []Track
    transport   Transport
}

func (c *RTSPClient) Connect() error {
    // Send DESCRIBE
    sdp := c.sendDescribe()
    c.tracks = parseSDP(sdp)
    
    // Setup each track
    for track := range c.tracks {
        c.sendSetup(track)
    }
    
    // Start streaming
    c.sendPlay()
    
    // Start keepalive goroutine
    go c.keepalive()
    
    return nil
}

func (c *RTSPClient) ReadPacket() (RTPPacket, error) {
    // Read from TCP socket
    packet := c.conn.Read()
    return parseRTP(packet)
}
```

### 2. Stream Demuxer

```go
type Demuxer struct {
    videoTrack *Track
    audioTrack *Track
    buffer     *Buffer
}

func (d *Demuxer) ProcessPacket(pkt RTPPacket) {
    if pkt.PayloadType == 96 { // H.264
        nalUnit := extractNAL(pkt)
        d.videoTrack.AddNAL(nalUnit)
        
        if nalUnit.IsKeyframe() {
            d.buffer.Flush() // Complete GOP
        }
    } else if pkt.PayloadType == 97 { // AAC
        audioFrame := extractAAC(pkt)
        d.audioTrack.AddFrame(audioFrame)
    }
}
```

### 3. HLS Muxer

```go
type HLSMuxer struct {
    segmentDuration time.Duration  // 4s
    currentSegment  *Segment
    segmentCount    int
    playlist        *Playlist
}

func (m *HLSMuxer) WriteFrame(frame Frame) {
    m.currentSegment.AddFrame(frame)
    
    if m.currentSegment.Duration() >= m.segmentDuration {
        // Finalize segment
        m.finalizeSegment()
        
        // Create new segment
        m.currentSegment = NewSegment(m.segmentCount)
        m.segmentCount++
        
        // Update playlist
        m.updatePlaylist()
    }
}

func (m *HLSMuxer) finalizeSegment() {
    // Write fMP4 file
    filename := fmt.Sprintf("seg_%d.mp4", m.segmentCount)
    m.currentSegment.WriteToFile(filename)
    
    // Add to playlist
    m.playlist.AddSegment(filename, m.currentSegment.Duration())
    
    // Remove old segments (keep only 6)
    if len(m.playlist.Segments) > 6 {
        oldSegment := m.playlist.Segments[0]
        os.Remove(oldSegment.Filename)
        m.playlist.Segments = m.playlist.Segments[1:]
    }
}
```

## MediaMTX Configuration Deep Dive

### Path Configuration

```yaml
paths:
  cam_2:
    source: rtsp://admin:password@192.168.1.100:554/stream1
    sourceOnDemand: yes
    sourceOnDemandStartTimeout: 10s
    sourceOnDemandCloseAfter: 15s
    maxReaders: 8
    rtspTransport: tcp
```

**Parameter Explanation**:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `source` | RTSP URL | Camera stream source |
| `sourceOnDemand` | yes | Only connect when viewers present |
| `sourceOnDemandStartTimeout` | 10s | Max time to establish RTSP connection |
| `sourceOnDemandCloseAfter` | 15s | Close RTSP after last viewer leaves |
| `maxReaders` | 8 | Max concurrent HLS viewers |
| `rtspTransport` | tcp | Use TCP (reliable) instead of UDP |

### HLS Configuration

```yaml
hls: yes
hlsAddress: :8888
hlsVariant: fmp4              # Fragmented MP4
hlsSegmentCount: 6            # Playlist size
hlsSegmentDuration: 4s        # Segment length
hlsSegmentMaxSize: 50M        # Max segment file size
hlsMuxerCloseAfter: 30s       # Close muxer after no viewers
hlsPartDuration: 1s           # Low-latency part duration
```

**Why fMP4 over TS?**
- ✅ Better browser support
- ✅ Smaller file sizes
- ✅ Faster seeking
- ✅ Modern standard

## Transport Modes

### TCP (Interleaved) - Current Configuration

```
MediaMTX ←→ Camera
    |
    TCP Connection (Port 554)
    |
    ├─ RTSP Commands (ASCII)
    └─ RTP Data (Binary, interleaved)
```

**Advantages**:
- ✅ Reliable delivery
- ✅ Works through firewalls
- ✅ No packet loss
- ✅ Ordered packets

**Disadvantages**:
- ❌ Higher latency
- ❌ TCP overhead
- ❌ Head-of-line blocking

### UDP (Alternative)

```
MediaMTX ←→ Camera
    |
    ├─ TCP Port 554 (RTSP commands)
    ├─ UDP Port 5000-5001 (RTP video)
    └─ UDP Port 5002-5003 (RTP audio)
```

**Advantages**:
- ✅ Lower latency
- ✅ Less overhead
- ✅ Better for real-time

**Disadvantages**:
- ❌ Packet loss possible
- ❌ Firewall issues
- ❌ NAT traversal problems

**MVP Choice**: TCP for reliability

## Bandwidth Calculation

### Camera Output

**1080p @ 25fps, H.264 High Profile**:
```
Bitrate: 3 Mbps (variable)
Packet Size: ~1400 bytes (MTU)
Packets per second: ~270 packets/s
Bandwidth: 3 Mbps + RTSP overhead (~3.2 Mbps)
```

### MediaMTX Processing

**Input**: 3 Mbps RTSP
**Processing**: Demux + Remux to HLS
**Output**: 3 Mbps HLS (same bitrate, different container)

**No Transcoding**: MediaMTX does NOT re-encode video, only repackages it.

### Network Flow

```
Camera (3 Mbps) 
    → RTSP/TCP → 
MediaMTX (3 Mbps buffered)
    → HLS/HTTP → 
Browser (3 Mbps per viewer)
```

**4 Viewers**: 3 Mbps input, 12 Mbps output

## Error Scenarios

### 1. Camera Unreachable

```mermaid
sequenceDiagram
    participant MediaMTX
    participant Camera

    MediaMTX->>Camera: DESCRIBE rtsp://...
    Note right of MediaMTX: Timeout after 10s
    Camera--xMediaMTX: No response
    MediaMTX->>MediaMTX: Retry 3 times
    MediaMTX->>MediaMTX: Mark path as failed
    MediaMTX->>Viewer: 404 Not Found
```

### 2. Connection Lost During Streaming

```mermaid
sequenceDiagram
    participant MediaMTX
    participant Camera
    participant Viewer

    Camera->>MediaMTX: RTP packets (streaming)
    Note over Camera: Network interruption
    Camera--xMediaMTX: Connection lost
    MediaMTX->>MediaMTX: Detect timeout (no packets)
    MediaMTX->>MediaMTX: Attempt reconnect
    
    alt Reconnect Success
        MediaMTX->>Camera: DESCRIBE + SETUP + PLAY
        Camera->>MediaMTX: Resume streaming
        MediaMTX->>Viewer: Continue HLS
    else Reconnect Failed
        MediaMTX->>MediaMTX: Close path
        MediaMTX->>Viewer: Stop serving segments
        Viewer->>Viewer: HLS.js error event
    end
```

### 3. Authentication Failure

```mermaid
sequenceDiagram
    participant MediaMTX
    participant Camera

    MediaMTX->>Camera: DESCRIBE rtsp://user:pass@...
    Camera->>MediaMTX: 401 Unauthorized<br/>WWW-Authenticate: Basic realm="RTSP"
    MediaMTX->>Camera: DESCRIBE with Authorization header
    
    alt Correct Credentials
        Camera->>MediaMTX: 200 OK + SDP
    else Wrong Credentials
        Camera->>MediaMTX: 401 Unauthorized
        MediaMTX->>MediaMTX: Mark as auth failed
        MediaMTX->>Viewer: 404 Not Found
    end
```

## Performance Optimization

### 1. Buffer Management

```yaml
# MediaMTX buffer settings
rtspUDPReadBufferSize: 65536    # 64KB
writeQueueSize: 65536           # 64K packets
```

**Purpose**:
- Absorb network jitter
- Prevent packet loss
- Smooth output to HLS

### 2. Segment Duration Trade-off

| Duration | Latency | CPU | Requests/min |
|----------|---------|-----|--------------|
| 1s | Low (6s) | High | 60 |
| 2s | Medium (12s) | Medium | 30 |
| 4s | High (24s) | Low | 15 |
| 6s | Very High (36s) | Very Low | 10 |

**MVP Choice**: 4s (balanced for multiple streams)

### 3. On-Demand Connection

```
No Viewers:
  Camera: Idle
  MediaMTX: No RTSP connection
  Bandwidth: 0

First Viewer Arrives:
  MediaMTX → Camera: Connect (10s)
  Camera → MediaMTX: Start streaming
  Bandwidth: 3 Mbps

Last Viewer Leaves:
  MediaMTX: Wait 30s
  MediaMTX → Camera: TEARDOWN
  Bandwidth: 0
```

**Savings**: Only use bandwidth when needed

## Monitoring & Debugging

### Check RTSP Connection

```bash
# Test RTSP with ffmpeg
ffmpeg -rtsp_transport tcp -i rtsp://admin:pass@192.168.1.100:554/stream1 -t 10 test.mp4

# Test with VLC
vlc rtsp://admin:pass@192.168.1.100:554/stream1

# MediaMTX API - Check path status
curl http://localhost:9997/v3/paths/get/cam_2
```

### MediaMTX Logs

```
2026/01/08 10:00:00 INF [RTSP] [conn 192.168.1.100:554] opened
2026/01/08 10:00:01 INF [RTSP] [session 12345678] created by 192.168.1.100:554
2026/01/08 10:00:01 INF [RTSP] [session 12345678] is reading from path 'cam_2', 1 track with TCP
2026/01/08 10:00:05 INF [HLS] [muxer cam_2] is converting into HLS, 1 track (H264)
2026/01/08 10:00:09 INF [HLS] [muxer cam_2] is being read by 1 reader
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 on HLS | Path not provisioned | Check Streaming Service |
| Timeout on DESCRIBE | Camera offline | Check camera network |
| 401 Unauthorized | Wrong credentials | Update RTSP URL |
| Stuttering playback | Packet loss | Use TCP transport |
| High CPU | Too many streams | Limit concurrent cameras |

## Camera Compatibility

### Tested Cameras

| Brand | Model | RTSP URL Format | Notes |
|-------|-------|-----------------|-------|
| Hikvision | DS-2CD2xxx | `rtsp://admin:pass@ip:554/Streaming/Channels/101` | ✅ Works |
| Dahua | IPC-HDW | `rtsp://admin:pass@ip:554/cam/realmonitor?channel=1&subtype=0` | ✅ Works |
| Axis | M-Series | `rtsp://root:pass@ip:554/axis-media/media.amp` | ✅ Works |
| Generic ONVIF | Various | `rtsp://admin:pass@ip:554/stream1` | ✅ Usually works |

### Requirements

- **Protocol**: RTSP (not HTTP-FLV, not proprietary)
- **Codec**: H.264 (not H.265 for MVP)
- **Transport**: TCP support
- **Authentication**: Basic or Digest
- **Resolution**: Up to 1080p recommended

## Future Enhancements

1. **H.265 Support**: Better compression
2. **UDP Transport**: Lower latency option
3. **Multicast**: Efficient for multiple viewers
4. **ONVIF Discovery**: Auto-detect cameras
5. **PTZ Control**: Pan/Tilt/Zoom via ONVIF
6. **Audio Support**: Two-way audio
7. **Recording**: Save to disk
8. **Snapshot**: Extract still images
