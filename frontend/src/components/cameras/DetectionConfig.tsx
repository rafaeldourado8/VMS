import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { Save, Plus, Trash2, Settings, Edit } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui'
import { ROIEditor } from './ROIEditor'
import { aiService, cameraService, streamingService } from '@/services/api'
import type { Camera, ROIArea, VirtualLine, ZoneTrigger } from '@/types'

interface DetectionConfigProps {
  camera: Camera
  onClose: () => void
}

export function DetectionConfig({ camera, onClose }: DetectionConfigProps) {
  const queryClient = useQueryClient()
  const [showROIEditor, setShowROIEditor] = useState(false)
  
  // Estados para configurações
  const [roiAreas, setRoiAreas] = useState<ROIArea[]>(camera.roi_areas || [])
  const [virtualLines, setVirtualLines] = useState<VirtualLine[]>(camera.virtual_lines || [])
  const [tripwires, setTripwires] = useState<VirtualLine[]>(camera.tripwires || [])
  const [zoneTriggers, setZoneTriggers] = useState<ZoneTrigger[]>(camera.zone_triggers || [])
  const [retentionDays, setRetentionDays] = useState(camera.recording_retention_days || 30)
  const [aiEnabled, setAiEnabled] = useState(camera.ai_enabled || false)
  const [testingAI, setTestingAI] = useState(false)

  // Query para status da IA
  const { data: aiStatus, refetch: refetchAIStatus } = useQuery({
    queryKey: ['ai-status', camera.id],
    queryFn: () => aiService.getStatus(camera.id),
    enabled: aiEnabled,
    refetchInterval: aiEnabled ? 5000 : false, // Atualiza a cada 5s se IA ativa
  })

  const updateMutation = useMutation({
    mutationFn: (config: any) => cameraService.updateDetectionConfig(camera.id, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
      onClose()
    },
  })

  const toggleAIMutation = useMutation({
    mutationFn: (enabled: boolean) => cameraService.toggleAI(camera.id, enabled),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
    },
  })

  const hasDetectionConfig = roiAreas.length > 0 || virtualLines.length > 0 || tripwires.length > 0 || zoneTriggers.length > 0

  const handleAIToggle = async (enabled: boolean) => {
    if (enabled && !hasDetectionConfig) {
      alert('Configure pelo menos uma área ROI, linha virtual, tripwire ou zona de trigger antes de ativar a IA.')
      return
    }
    setAiEnabled(enabled)
    try {
      if (enabled) {
        await aiService.startProcessing(camera.id)
      } else {
        await aiService.stopProcessing(camera.id)
      }
      toggleAIMutation.mutate(enabled)
      // Atualizar status após toggle
      setTimeout(() => refetchAIStatus(), 1000)
    } catch (error) {
      console.error('Erro ao alterar IA:', error)
      setAiEnabled(!enabled) // Reverter em caso de erro
    }
  }

  const testAI = async () => {
    setTestingAI(true)
    try {
      const result = await aiService.testDetection(camera.id)
      alert(`Teste da IA: ${result.success ? 'Sucesso' : 'Falha'} - ${result.message}`)
    } catch (error) {
      alert('Erro ao testar IA')
    } finally {
      setTestingAI(false)
    }
  }

  const handleSave = () => {
    updateMutation.mutate({
      roi_areas: roiAreas,
      virtual_lines: virtualLines,
      tripwires: tripwires,
      zone_triggers: zoneTriggers,
      recording_retention_days: retentionDays,
      ai_enabled: aiEnabled,
    })
  }

  const addROIArea = () => {
    const newArea: ROIArea = {
      id: Date.now().toString(),
      name: `Área ${roiAreas.length + 1}`,
      points: [
        { x: 0.2, y: 0.2 },
        { x: 0.8, y: 0.2 },
        { x: 0.8, y: 0.8 },
        { x: 0.2, y: 0.8 },
      ],
      enabled: true,
    }
    setRoiAreas([...roiAreas, newArea])
  }

  const addVirtualLine = () => {
    const newLine: VirtualLine = {
      id: Date.now().toString(),
      name: `Linha ${virtualLines.length + 1}`,
      start: { x: 0.3, y: 0.5 },
      end: { x: 0.7, y: 0.5 },
      direction: 'both',
      enabled: true,
    }
    setVirtualLines([...virtualLines, newLine])
  }

  const addTripwire = () => {
    const newTripwire: VirtualLine = {
      id: Date.now().toString(),
      name: `Tripwire ${tripwires.length + 1}`,
      start: { x: 0.2, y: 0.6 },
      end: { x: 0.8, y: 0.6 },
      direction: 'both',
      enabled: true,
    }
    setTripwires([...tripwires, newTripwire])
  }

  const addZoneTrigger = () => {
    const newZone: ZoneTrigger = {
      id: Date.now().toString(),
      name: `Zona ${zoneTriggers.length + 1}`,
      points: [
        { x: 0.1, y: 0.1 },
        { x: 0.5, y: 0.1 },
        { x: 0.5, y: 0.5 },
        { x: 0.1, y: 0.5 },
      ],
      triggerType: 'enter',
      enabled: true,
    }
    setZoneTriggers([...zoneTriggers, newZone])
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-card rounded-xl">
        <div className="sticky top-0 bg-card border-b p-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Configurações de Detecção - {camera.name}
            </h2>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button onClick={handleSave} disabled={updateMutation.isPending}>
              <Save className="w-4 h-4 mr-2" />
              Salvar
            </Button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Configurações de IA */}
          <Card>
            <CardHeader>
              <CardTitle>Inteligência Artificial</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium">Ativar IA</label>
                    <p className="text-xs text-muted-foreground">Habilita detecção automática de eventos</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={aiEnabled}
                      onChange={(e) => handleAIToggle(e.target.checked)}
                      disabled={!hasDetectionConfig && !aiEnabled}
                      className="sr-only peer"
                    />
                    <div className={`w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600 ${!hasDetectionConfig && !aiEnabled ? 'opacity-50 cursor-not-allowed' : ''}`}></div>
                  </label>
                </div>
                {aiEnabled && (
                  <div className="space-y-3">
                    <div className="text-sm text-green-600 bg-green-50 p-3 rounded">
                      ✓ IA ativa - Processando detecções em tempo real
                    </div>
                    {aiStatus && (
                      <div className="text-xs space-y-2">
                        <div className="bg-gray-50 p-2 rounded font-mono">
                          <div>Status: <span className={aiStatus.status === 'active' ? 'font-bold text-green-600' : 'font-bold text-red-600'}>{aiStatus.status}</span></div>
                          <div>Última detecção: {aiStatus.last_detection || 'Nenhuma'}</div>
                          <div>Detecções hoje: {aiStatus.detections_today || 0}</div>
                          {aiStatus.error && (
                            <div className="text-red-600">Erro: {aiStatus.error}</div>
                          )}
                        </div>
                      </div>
                    )}
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={testAI} disabled={testingAI}>
                        {testingAI ? 'Testando...' : 'Testar IA'}
                      </Button>
                    </div>
                  </div>
                )}
                {!aiEnabled && (
                  <div className="space-y-3">
                    <div className="text-sm text-amber-600 bg-amber-50 p-3 rounded">
                      ⚠ IA desativada - Configure áreas de detecção e ative para começar
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Dica: Configure pelo menos uma área ROI, linha virtual ou tripwire antes de ativar a IA
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Configurações de Gravação */}
          <Card>
            <CardHeader>
              <CardTitle>Configurações de Gravação</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Retenção de Gravações</label>
                  <select 
                    value={retentionDays.toString()} 
                    onChange={(e) => setRetentionDays(parseInt(e.target.value))}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="7">7 dias</option>
                    <option value="15">15 dias</option>
                    <option value="30">30 dias</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* ROI Areas */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Áreas ROI (Região de Interesse)</CardTitle>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => setShowROIEditor(true)}>
                  <Edit className="w-4 h-4 mr-2" />
                  Editor Visual
                </Button>
                <Button size="sm" onClick={addROIArea}>
                  <Plus className="w-4 h-4 mr-2" />
                  Adicionar Área
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Define onde a IA deve detectar objetos. Apenas detecções dentro dessas áreas serão processadas.
              </p>
              <div className="space-y-3">
                {roiAreas.map((area, index) => (
                  <div key={area.id} className="flex items-center gap-3 p-3 border rounded">
                    <Input
                      value={area.name}
                      onChange={(e) => {
                        const updated = [...roiAreas]
                        updated[index].name = e.target.value
                        setRoiAreas(updated)
                      }}
                      className="flex-1"
                    />
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setRoiAreas(roiAreas.filter(a => a.id !== area.id))}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
                {roiAreas.length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    Nenhuma área ROI configurada. A detecção será feita em toda a imagem.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Virtual Lines */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Linhas Virtuais</CardTitle>
              <Button size="sm" onClick={addVirtualLine}>
                <Plus className="w-4 h-4 mr-2" />
                Adicionar Linha
              </Button>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Dispara evento quando um objeto cruza a linha virtual.
              </p>
              <div className="space-y-3">
                {virtualLines.map((line, index) => (
                  <div key={line.id} className="flex items-center gap-3 p-3 border rounded">
                    <Input
                      value={line.name}
                      onChange={(e) => {
                        const updated = [...virtualLines]
                        updated[index].name = e.target.value
                        setVirtualLines(updated)
                      }}
                      className="flex-1"
                    />
                    <select
                      value={line.direction}
                      onChange={(e) => {
                        const updated = [...virtualLines]
                        updated[index].direction = e.target.value as any
                        setVirtualLines(updated)
                      }}
                      className="w-40 flex h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <option value="both">Ambas direções</option>
                      <option value="left-to-right">Esquerda → Direita</option>
                      <option value="right-to-left">Direita → Esquerda</option>
                    </select>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setVirtualLines(virtualLines.filter(l => l.id !== line.id))}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Tripwires */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Tripwires (Linhas de Gatilho)</CardTitle>
              <Button size="sm" onClick={addTripwire}>
                <Plus className="w-4 h-4 mr-2" />
                Adicionar Tripwire
              </Button>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Linhas de gatilho mais sensíveis para detecção de intrusão.
              </p>
              <div className="space-y-3">
                {tripwires.map((wire, index) => (
                  <div key={wire.id} className="flex items-center gap-3 p-3 border rounded">
                    <Input
                      value={wire.name}
                      onChange={(e) => {
                        const updated = [...tripwires]
                        updated[index].name = e.target.value
                        setTripwires(updated)
                      }}
                      className="flex-1"
                    />
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setTripwires(tripwires.filter(w => w.id !== wire.id))}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Zone Triggers */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Zonas de Trigger</CardTitle>
              <Button size="sm" onClick={addZoneTrigger}>
                <Plus className="w-4 h-4 mr-2" />
                Adicionar Zona
              </Button>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Dispara evento quando objeto entra ou sai da área definida.
              </p>
              <div className="space-y-3">
                {zoneTriggers.map((zone, index) => (
                  <div key={zone.id} className="flex items-center gap-3 p-3 border rounded">
                    <Input
                      value={zone.name}
                      onChange={(e) => {
                        const updated = [...zoneTriggers]
                        updated[index].name = e.target.value
                        setZoneTriggers(updated)
                      }}
                      className="flex-1"
                    />
                    <select
                      value={zone.triggerType}
                      onChange={(e) => {
                        const updated = [...zoneTriggers]
                        updated[index].triggerType = e.target.value as any
                        setZoneTriggers(updated)
                      }}
                      className="w-32 flex h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <option value="enter">Entrada</option>
                      <option value="exit">Saída</option>
                      <option value="both">Ambos</option>
                    </select>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setZoneTriggers(zoneTriggers.filter(z => z.id !== zone.id))}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
      {/* ROI Editor Modal */}
      {showROIEditor && (
        <ROIEditor
          videoSrc={streamingService.getHlsUrl(camera.id)}
          onSave={(config) => {
            setRoiAreas(config.roi_areas)
            setVirtualLines(config.virtual_lines)
            setTripwires(config.tripwires)
            setZoneTriggers(config.zone_triggers)
            setShowROIEditor(false)
          }}
          onClose={() => setShowROIEditor(false)}
          initialConfig={{
            roi_areas: roiAreas,
            virtual_lines: virtualLines,
            tripwires: tripwires,
            zone_triggers: zoneTriggers
          }}
        />
      )}
    </div>
  )
}