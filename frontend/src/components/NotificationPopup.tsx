import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, X, XCircle, Server, AlertCircle, Trash2, Check } from 'lucide-react'
import { notificationService } from '@/services/api'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export function NotificationPopup() {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: notifications = [] } = useQuery({
    queryKey: ['notifications'],
    queryFn: notificationService.getNotifications,
    refetchInterval: 30000, // Atualiza a cada 30s
  })

  const deleteNotificationMutation = useMutation({
    mutationFn: notificationService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const deleteAllMutation = useMutation({
    mutationFn: notificationService.deleteAll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const markAllAsReadMutation = useMutation({
    mutationFn: notificationService.markAllAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const unreadCount = notifications.filter((n: any) => !n.read_at).length

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'camera_offline': return XCircle
      case 'system': return Server
      default: return AlertCircle
    }
  }

  const handleDeleteNotification = (id: number, e: React.MouseEvent) => {
    e.stopPropagation()
    deleteNotificationMutation.mutate(id)
  }

  const handleDeleteAll = () => {
    deleteAllMutation.mutate()
  }

  const handleMarkAllAsRead = () => {
    markAllAsReadMutation.mutate()
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg hover:bg-secondary transition-colors"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 top-12 w-96 bg-card border border-border rounded-xl shadow-2xl z-50 max-h-[500px] flex flex-col">
            <div className="p-4 border-b border-border flex items-center justify-between">
              <h3 className="font-semibold">Notificações</h3>
              <div className="flex items-center gap-2">
                {notifications.length > 0 && (
                  <>
                    {unreadCount > 0 && (
                      <button
                        onClick={handleMarkAllAsRead}
                        className="text-xs text-blue-500 hover:text-blue-600 flex items-center gap-1"
                        disabled={markAllAsReadMutation.isPending}
                      >
                        <Check className="w-3 h-3" />
                        Marcar todas como lidas
                      </button>
                    )}
                    <button
                      onClick={handleDeleteAll}
                      className="text-xs text-red-500 hover:text-red-600 flex items-center gap-1"
                      disabled={deleteAllMutation.isPending}
                    >
                      <Trash2 className="w-3 h-3" />
                      Apagar todas
                    </button>
                  </>
                )}
                <button onClick={() => setIsOpen(false)} className="text-muted-foreground hover:text-foreground">
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="overflow-y-auto flex-1">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground">
                  <Bell className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Nenhuma notificação</p>
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {notifications.map((notification: any) => {
                    const Icon = getCategoryIcon(notification.category)
                    return (
                      <div
                        key={notification.id}
                        className={`p-4 hover:bg-secondary/50 transition-colors group ${
                          !notification.read_at ? 'bg-primary/5' : ''
                        }`}
                      >
                        <div className="flex gap-3">
                          <div className={`p-2 rounded-lg h-fit ${
                            notification.category === 'camera_offline' ? 'bg-red-500/10' : 'bg-yellow-500/10'
                          }`}>
                            <Icon className={`w-4 h-4 ${
                              notification.category === 'camera_offline' ? 'text-red-500' : 'text-yellow-500'
                            }`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm">{notification.title}</p>
                            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                              {notification.message}
                            </p>
                            <p className="text-xs text-muted-foreground mt-2">
                              {formatDistanceToNow(new Date(notification.sent_at), { 
                                addSuffix: true, 
                                locale: ptBR 
                              })}
                            </p>
                          </div>
                          <button
                            onClick={(e) => handleDeleteNotification(notification.id, e)}
                            className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:text-red-600 transition-all"
                            disabled={deleteNotificationMutation.isPending}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
