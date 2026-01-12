// frontend/src/lib/metrics.ts
class MetricsClient {
  private endpoint = '/api/metrics'

  async recordProtocolFallback(cameraId: number, from: string, to: string) {
    try {
      await fetch(this.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metric: 'vms_protocol_fallback_total',
          labels: { camera_id: cameraId.toString(), from, to },
          value: 1,
        }),
      })
    } catch (error) {
      console.error('Failed to record metric:', error)
    }
  }
}

export const metricsClient = new MetricsClient()
