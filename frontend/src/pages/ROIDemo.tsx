import { useState } from 'react'
import { Button } from '@/components/ui'
import { ROIEditor } from '@/components/cameras/ROIEditor'
import { Edit } from 'lucide-react'

export function ROIDemo() {
  const [showEditor, setShowEditor] = useState(false)

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Demo - Editor de ROI</h1>
      
      <Button onClick={() => setShowEditor(true)}>
        <Edit className="w-4 h-4 mr-2" />
        Abrir Editor ROI
      </Button>

      {showEditor && (
        <ROIEditor
          videoSrc="/api/test-video.mp4" // URL de exemplo
          onSave={(config) => {
            console.log('Configuração salva:', config)
            setShowEditor(false)
          }}
          onClose={() => setShowEditor(false)}
        />
      )}
    </div>
  )
}