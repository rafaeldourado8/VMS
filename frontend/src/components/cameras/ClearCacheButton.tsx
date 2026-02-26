import { Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useCameraStore } from '@/store/cameraStore'
import { toast } from 'sonner'

export function ClearCacheButton() {
  const clearAllCameraCache = useCameraStore(state => state.clearAllCameraCache)

  const handleClearCache = async () => {
    try {
      // Limpar cache do frontend (IndexedDB)
      clearAllCameraCache()
      
      // Limpar cache do backend
      await fetch('/api/thumbnails/clear/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      toast.success('Cache de thumbnails limpo com sucesso')
      window.location.reload()
    } catch (error) {
      toast.error('Erro ao limpar cache')
    }
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleClearCache}
      className="gap-2"
    >
      <Trash2 className="w-4 h-4" />
      Limpar Cache
    </Button>
  )
}
