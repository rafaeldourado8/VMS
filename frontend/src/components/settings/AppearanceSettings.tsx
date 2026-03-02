import { Palette } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui'
import { useTheme } from '@/hooks/useTheme'

export function AppearanceSettings() {
  const { theme, setTheme } = useTheme()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Aparência</CardTitle>
        <CardDescription>Personalize a interface do sistema</CardDescription>
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
                    theme === t ? 'border-primary bg-primary/10' : 'border-border hover:border-muted-foreground'
                  }`}
                >
                  <Palette className="w-5 h-5 mx-auto mb-2" />
                  <span className="text-sm capitalize">{t === 'system' ? 'Sistema' : t === 'light' ? 'Claro' : 'Escuro'}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm font-medium mb-3">Layout do Grid de Câmeras</p>
            <p className="text-sm text-muted-foreground">Você pode alterar o layout diretamente na página de câmeras usando os botões de grade.</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
