import { useQuery } from '@tanstack/react-query'
import {
  Camera,
  Car,
  TrendingUp,
  AlertTriangle,
  Activity,
  Clock,
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardContent, Badge, Skeleton } from '@/components/ui'
import { dashboardService, cameraService } from '@/services/api'
import { formatRelativeTime, getVehicleTypeLabel } from '@/lib/utils'
import { CameraCard } from '@/components/cameras/CameraCard'

// Cores para o gráfico de pizza
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

// Dados mock para o gráfico de área (últimas 24h)
const mockHourlyData = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i}:00`,
  detections: Math.floor(Math.random() * 50) + 10,
}))

export function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardService.getStats,
    refetchInterval: 30000, // Atualiza a cada 30s
  })

  const { data: cameras, isLoading: camerasLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: cameraService.list,
  })

  // Preparar dados para o gráfico de pizza
  const pieData = stats?.detections_by_type
    ? Object.entries(stats.detections_by_type).map(([type, count]) => ({
        name: getVehicleTypeLabel(type),
        value: count,
      }))
    : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Visão geral do sistema</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Câmeras"
          value={stats?.total_cameras ?? 0}
          subtitle={`${stats?.cameras_status?.online ?? 0} online`}
          icon={Camera}
          loading={statsLoading}
        />
        <StatCard
          title="Detecções (24h)"
          value={stats?.detections_24h ?? 0}
          subtitle="Veículos detectados"
          icon={Car}
          loading={statsLoading}
          trend={12}
        />
        <StatCard
          title="Câmeras Online"
          value={stats?.cameras_status?.online ?? 0}
          subtitle={`${stats?.cameras_status?.offline ?? 0} offline`}
          icon={Activity}
          loading={statsLoading}
          variant={stats?.cameras_status?.offline ? 'warning' : 'success'}
        />
        <StatCard
          title="Alertas"
          value={0}
          subtitle="Nenhum alerta ativo"
          icon={AlertTriangle}
          loading={statsLoading}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Area Chart - Detections over time */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base font-medium flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Detecções por Hora
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockHourlyData}>
                  <defs>
                    <linearGradient id="colorDetections" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="hour"
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(222 47% 8%)',
                      border: '1px solid hsl(217 33% 17%)',
                      borderRadius: '8px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="detections"
                    stroke="#3b82f6"
                    fillOpacity={1}
                    fill="url(#colorDetections)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Pie Chart - Vehicle Types */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium flex items-center gap-2">
              <Car className="w-4 h-4" />
              Tipos de Veículos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center">
              {pieData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((_, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(222 47% 8%)',
                        border: '1px solid hsl(217 33% 17%)',
                        borderRadius: '8px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-muted-foreground">Sem dados</p>
              )}
            </div>
            {/* Legend */}
            <div className="flex flex-wrap gap-3 mt-4 justify-center">
              {pieData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-1.5">
                  <div
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-xs text-muted-foreground">{entry.name}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Atividade Recente
            </CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : stats?.recent_activity?.length ? (
              <div className="space-y-3">
                {stats.recent_activity.slice(0, 5).map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-center justify-between py-2 border-b border-border last:border-0"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center">
                        <Car className="w-4 h-4 text-muted-foreground" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">
                          {activity.plate || 'Sem placa'}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {activity.camera}
                        </p>
                      </div>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {formatRelativeTime(activity.time)}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">
                Nenhuma atividade recente
              </p>
            )}
          </CardContent>
        </Card>

        {/* Camera Preview */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base font-medium flex items-center gap-2">
              <Camera className="w-4 h-4" />
              Câmeras em Destaque
            </CardTitle>
          </CardHeader>
          <CardContent>
            {camerasLoading ? (
              <div className="grid grid-cols-2 gap-3">
                {[1, 2].map((i) => (
                  <Skeleton key={i} className="aspect-video rounded-lg" />
                ))}
              </div>
            ) : cameras?.length ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {cameras.slice(0, 2).map((camera) => (
                  <CameraCard key={camera.id} camera={camera} compact />
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">
                Nenhuma câmera configurada
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// Stat Card Component
interface StatCardProps {
  title: string
  value: number
  subtitle: string
  icon: React.ElementType
  loading?: boolean
  trend?: number
  variant?: 'default' | 'success' | 'warning'
}

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  loading,
  trend,
  variant = 'default',
}: StatCardProps) {
  const variantStyles = {
    default: 'bg-primary/10 text-primary',
    success: 'bg-emerald-500/10 text-emerald-500',
    warning: 'bg-amber-500/10 text-amber-500',
  }

  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            {loading ? (
              <Skeleton className="h-8 w-16 mt-1" />
            ) : (
              <p className="text-2xl font-bold mt-1">{value.toLocaleString()}</p>
            )}
            <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
          </div>
          <div className={`p-2.5 rounded-lg ${variantStyles[variant]}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
        {trend !== undefined && (
          <div className="flex items-center gap-1 mt-3">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
            <span className="text-xs text-emerald-500">+{trend}%</span>
            <span className="text-xs text-muted-foreground">vs ontem</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
