import { LiveDetections } from '@/components/detections/LiveDetections'

export function DetectionsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Detecções LPR</h1>
        <p className="text-muted-foreground">Placas detectadas em tempo real</p>
      </div>

      <LiveDetections />
    </div>
  )
}
