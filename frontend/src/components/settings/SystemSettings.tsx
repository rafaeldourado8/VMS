import { useQuery } from '@tanstack/react-query'
import { Activity, RefreshCw } from 'lucide-react'
import { Button, Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui'
import { streamingService } from '@/services/api'
import { formatBytes, formatDuration } from '@/lib/utils'

export function SystemSettings() {
  const { data: stats, isLoading, refetch } = useQuery({
    queryKey: ['streaming-stats'],
    queryFn: streamingService.getStats,
    refetchInterval: 10000,
  })

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Estatísticas do Sistema
          </CardTitle>
          <CardDescription>Monitoramento de streaming em tempo real</CardDescription>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Atualizar
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-muted-foreground">Carregando...</p>
        ) : stats ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-secondary">
              <p className="text-2xl font-bold">{stats.active_streams ?? 0}</p>
              <p className="text-sm text-muted-foreground">Streams Ativos</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary">
              <p className="text-2xl font-bold">{stats.total_viewers ?? 0}</p>
              <p className="text-sm text-muted-foreground">Viewers</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary">
              <p className="text-2xl font-bold">{formatBytes(stats.total_bytes_sent ?? 0)}</p>
              <p className="text-sm text-muted-foreground">Dados Enviados</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary">
              <p className="text-2xl font-bold">{formatDuration(stats.uptime_seconds ?? 0)}</p>
              <p className="text-sm text-muted-foreground">Uptime</p>
            </div>
          </div>
        ) : (
          <p className="text-muted-foreground">Serviço indisponível</p>
        )}
      </CardContent>
    </Card>
  )
}
