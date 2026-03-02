import { useState } from 'react'
import { User, Shield, Save } from 'lucide-react'
import { Button, Card, CardHeader, CardTitle, CardContent, CardDescription, Input, Badge, Label } from '@/components/ui'
import { useAuthStore } from '@/store/authStore'

export function ProfileSettings() {
  const { user } = useAuthStore()
  const [name, setName] = useState(user?.name ?? '')
  const [email, setEmail] = useState(user?.email ?? '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Informações do Perfil</CardTitle>
          <CardDescription>Atualize suas informações pessoais</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
              <User className="w-8 h-8 text-white" />
            </div>
            <div>
              <p className="font-medium text-lg">{user?.name}</p>
              <Badge variant={user?.role === 'admin' ? 'default' : 'secondary'}>
                {user?.role === 'admin' ? 'Administrador' : 'Visualizador'}
              </Badge>
            </div>
          </div>

          <div className="grid gap-4 pt-4">
            <div className="space-y-2">
              <Label>Nome</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Seu nome completo" />
            </div>
            <div className="space-y-2">
              <Label>Email</Label>
              <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="seu@email.com" />
            </div>
          </div>

          <Button className="mt-4">
            <Save className="w-4 h-4 mr-2" />
            Salvar Alterações
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Segurança</CardTitle>
          <CardDescription>Altere sua senha e configurações de segurança</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Senha Atual</Label>
            <Input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} placeholder="••••••••" />
          </div>
          <div className="space-y-2">
            <Label>Nova Senha</Label>
            <Input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="••••••••" />
            <p className="text-xs text-muted-foreground">Mínimo de 8 caracteres</p>
          </div>
          <div className="space-y-2">
            <Label>Confirmar Nova Senha</Label>
            <Input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="••••••••" />
          </div>
          <Button variant="outline" disabled={!currentPassword || !newPassword || !confirmPassword} className="mt-4">
            <Shield className="w-4 h-4 mr-2" />
            Alterar Senha
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
