import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  User,
  Shield,
  Bell,
  Palette,
  Server,
  Activity,
  CheckCircle,
  XCircle,
  RefreshCw,
} from 'lucide-react'
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
  Input,
  Badge,
} from '@/components/ui'
import { useAuthStore } from '@/store/authStore'
import { useTheme } from '@/hooks/useTheme'
import { streamingService } from '@/services/api'
import { formatBytes, formatDuration } from '@/lib/utils'

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile')

  const tabs = [
    { id: 'profile', label: 'Perfil', icon: User },
    { id: 'system', label: 'Sistema', icon: Server },
    { id: 'notifications', label: 'Notificações', icon: Bell },
    { id: 'appearance', label: 'Aparência', icon: Palette },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Configurações</h1>
        <p className="text-muted-foreground">Gerencie suas preferências</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <nav className="lg:w-56 flex-shrink-0">
          <div className="flex lg:flex-col gap-1 overflow-x-auto lg:overflow-visible pb-2 lg:pb-0">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </nav>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {activeTab === 'profile' && <ProfileSettings />}
          {activeTab === 'system' && <SystemSettings />}
          {activeTab === 'notifications' && <NotificationSettings />}
          {activeTab === 'appearance' && <AppearanceSettings />}
        </div>
      </div>
    </div>
  )
}

// Profile Settings
function ProfileSettings() {
  const { user } = useAuthStore()
  const [name, setName] = useState(user?.name ?? '')
  const [email, setEmail] = useState(user?.email ?? '')

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Informações do Perfil</CardTitle>
          <CardDescription>
            Atualize suas informações pessoais
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center">
              <User className="w-8 h-8 text-muted-foreground" />
            </div>
            <div>
              <p className="font-medium">{user?.name}</p>
              <p className="text-sm text-muted-foreground">{user?.role}</p>
            </div>
          </div>

          <div className="grid gap-4 pt-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Nome</label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <Button className="mt-4">Salvar Alterações</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Segurança</CardTitle>
          <CardDescription>
            Altere sua senha e configurações de segurança
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Senha Atual</label>
            <Input type="password" placeholder="••••••••" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Nova Senha</label>
            <Input type="password" placeholder="••••••••" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Confirmar Nova Senha</label>
            <Input type="password" placeholder="••••••••" />
          </div>
          <Button variant="outline" className="mt-4">
            <Shield className="w-4 h-4 mr-2" />
            Alterar Senha
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

// System Settings
function SystemSettings() {
  const { data: stats, isLoading, refetch } = useQuery({
    queryKey: ['streaming-stats'],
    queryFn: streamingService.getStats,
    refetchInterval: 10000,
  })

  const services = [
    { name: 'API Backend', status: 'online', port: 8000 },
    { name: 'Streaming Service', status: stats ? 'online' : 'offline', port: 8001 },
    { name: 'MediaMTX', status: 'online', port: 8888 },
    { name: 'Redis Cache', status: 'online', port: 6379 },
    { name: 'PostgreSQL', status: 'online', port: 5432 },
  ]

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Status do Sistema</CardTitle>
            <CardDescription>
              Monitoramento dos serviços em tempo real
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Atualizar
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {services.map((service) => (
              <div
                key={service.name}
                className="flex items-center justify-between py-3 border-b border-border last:border-0"
              >
                <div className="flex items-center gap-3">
                  {service.status === 'online' ? (
                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-destructive" />
                  )}
                  <div>
                    <p className="font-medium">{service.name}</p>
                    <p className="text-xs text-muted-foreground">
                      Porta: {service.port}
                    </p>
                  </div>
                </div>
                <Badge variant={service.status === 'online' ? 'success' : 'destructive'}>
                  {service.status}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Streaming Stats
          </CardTitle>
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
                <p className="text-2xl font-bold">
                  {formatBytes(stats.total_bytes_sent ?? 0)}
                </p>
                <p className="text-sm text-muted-foreground">Dados Enviados</p>
              </div>
              <div className="p-4 rounded-lg bg-secondary">
                <p className="text-2xl font-bold">
                  {formatDuration(stats.uptime_seconds ?? 0)}
                </p>
                <p className="text-sm text-muted-foreground">Uptime</p>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">Serviço indisponível</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// Notification Settings
function NotificationSettings() {
  const [settings, setSettings] = useState({
    emailAlerts: true,
    pushNotifications: false,
    detectionAlerts: true,
    systemAlerts: true,
    dailyReport: false,
  })

  const toggleSetting = (key: keyof typeof settings) => {
    setSettings((s) => ({ ...s, [key]: !s[key] }))
  }

  const options = [
    {
      key: 'emailAlerts' as const,
      title: 'Alertas por Email',
      description: 'Receba alertas importantes por email',
    },
    {
      key: 'pushNotifications' as const,
      title: 'Notificações Push',
      description: 'Notificações no navegador',
    },
    {
      key: 'detectionAlerts' as const,
      title: 'Alertas de Detecção',
      description: 'Notificar quando veículos específicos forem detectados',
    },
    {
      key: 'systemAlerts' as const,
      title: 'Alertas do Sistema',
      description: 'Câmeras offline, erros de conexão, etc.',
    },
    {
      key: 'dailyReport' as const,
      title: 'Relatório Diário',
      description: 'Resumo diário por email às 8h',
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Preferências de Notificação</CardTitle>
        <CardDescription>
          Configure como você deseja receber alertas
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {options.map((option) => (
            <div
              key={option.key}
              className="flex items-center justify-between py-3 border-b border-border last:border-0"
            >
              <div>
                <p className="font-medium">{option.title}</p>
                <p className="text-sm text-muted-foreground">
                  {option.description}
                </p>
              </div>
              <button
                onClick={() => toggleSetting(option.key)}
                className={`relative w-11 h-6 rounded-full transition-colors ${
                  settings[option.key] ? 'bg-primary' : 'bg-secondary'
                }`}
              >
                <span
                  className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${
                    settings[option.key] ? 'translate-x-5' : ''
                  }`}
                />
              </button>
            </div>
          ))}
        </div>

        <Button className="mt-6">Salvar Preferências</Button>
      </CardContent>
    </Card>
  )
}

// Appearance Settings - Clean version
function AppearanceSettings() {
  const { theme, setTheme } = useTheme()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Aparência</CardTitle>
        <CardDescription>
          Personalize a interface do sistema
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div>
            <p className="text-sm font-medium mb-3">Tema</p>
            <div className="grid grid-cols-3 gap-3">
              {['light', 'dark', 'system'].map((t) => (
                <button
                  key={t}
                  onClick={() => setTheme(t as 'light' | 'dark' | 'system')}
                  className={`p-4 rounded-lg border text-center transition-colors ${
                    theme === t
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-muted-foreground'
                  }`}
                >
                  <Palette className="w-5 h-5 mx-auto mb-2" />
                  <span className="text-sm capitalize">
                    {t === 'system' ? 'Sistema' : t === 'light' ? 'Claro' : 'Escuro'}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm font-medium mb-3">Layout do Grid de Câmeras</p>
            <p className="text-sm text-muted-foreground">
              Você pode alterar o layout diretamente na página de câmeras usando
              os botões de grade.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}