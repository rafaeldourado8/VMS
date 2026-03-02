import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, Activity, XCircle, Server, HardDrive, Save } from 'lucide-react'
import { Button, Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui'
import { notificationService } from '@/services/api'

export function NotificationSettings() {
  const queryClient = useQueryClient()
  
  const { data: preferences, isLoading } = useQuery({
    queryKey: ['notification-preferences'],
    queryFn: notificationService.getPreferences,
  })

  const updateMutation = useMutation({
    mutationFn: notificationService.updatePreferences,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-preferences'] })
    },
  })

  const toggleSetting = (key: string) => {
    if (!preferences) return
    updateMutation.mutate({ [key]: !preferences[key] })
  }

  const options = [
    { key: 'email_alerts', title: 'Alertas por Email', description: 'Receba alertas importantes por email', icon: Bell },
    { key: 'push_notifications', title: 'Notificações Push', description: 'Notificações no navegador', icon: Bell },
    { key: 'camera_offline', title: 'Câmera Offline', description: 'Alertar quando uma câmera ficar offline', icon: XCircle },
    { key: 'system_alerts', title: 'Alertas do Sistema', description: 'Erros de conexão, falhas de serviço, etc.', icon: Server },
  ]

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-muted-foreground">Carregando...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Preferências de Notificação</CardTitle>
        <CardDescription>Configure como você deseja receber alertas</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {options.map((option) => (
            <div key={option.key} className="flex items-center justify-between py-3 border-b border-border last:border-0">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-secondary">
                  <option.icon className="w-4 h-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="font-medium">{option.title}</p>
                  <p className="text-sm text-muted-foreground">{option.description}</p>
                </div>
              </div>
              <button
                onClick={() => toggleSetting(option.key)}
                disabled={updateMutation.isPending}
                className={`relative w-11 h-6 rounded-full transition-colors ${
                  preferences?.[option.key] ? 'bg-primary' : 'bg-secondary'
                }`}
              >
                <span
                  className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${
                    preferences?.[option.key] ? 'translate-x-5' : ''
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
