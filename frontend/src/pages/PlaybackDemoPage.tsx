import { CameraViewer } from '@/components/cameras/CameraViewer'

export function PlaybackDemoPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Playback com Timeline</h1>
      
      <div className="grid gap-6">
        <CameraViewer
          cameraId={1}
          cameraName="Câmera 1"
          liveUrl="/streaming/cameras/1/index.m3u8"
        />
        
        <CameraViewer
          cameraId={2}
          cameraName="Câmera 2"
          liveUrl="/streaming/cameras/2/index.m3u8"
        />
      </div>

      <div className="mt-8 p-4 bg-muted rounded-lg">
        <h2 className="font-semibold mb-2">Como usar:</h2>
        <ul className="list-disc list-inside space-y-1 text-sm">
          <li>Clique na timeline para navegar no tempo</li>
          <li>Use os botões 24h/1h/5min para ajustar o zoom</li>
          <li>Setas para navegar pela timeline</li>
          <li>Botão "Ao Vivo" para voltar ao stream em tempo real</li>
          <li>Barras azuis indicam gravações disponíveis</li>
          <li>Linha vermelha mostra o momento atual</li>
        </ul>
      </div>
    </div>
  )
}
