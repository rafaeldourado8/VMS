import { useEffect } from 'react'
import { clearOldSnapshots } from '@/lib/snapshotCache'

export function useSnapshotCleanup() {
  useEffect(() => {
    // Limpa snapshots antigos ao montar
    clearOldSnapshots()
    
    // Limpa a cada 1 hora
    const interval = setInterval(clearOldSnapshots, 60 * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [])
}
