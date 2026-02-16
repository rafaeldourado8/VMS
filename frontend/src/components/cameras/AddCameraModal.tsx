import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/ui'
import { cameraService, streamingService } from '@/services/api'
import type { CameraCreateRequest } from '@/types'

const RETENTION_PLANS = [
  { value: 7, label: '7 dias', description: 'Retenção curta - ideal para monitoramento básico' },
  { value: 15, label: '15 dias', description: 'Retenção média - balanceamento entre espaço e histórico' },
  { value: 30, label: '30 dias', description: 'Retenção longa - máximo histórico disponível' },
]

interface AddCameraModalProps {
  onClose: () => void
}

export function AddCameraModal({ onClose }: AddCameraModalProps) {
  const queryClient = useQueryClient()
  const [mode, setMode] = useState<'select' | 'easy' | 'advanced'>('select')
  const [protocol, setProtocol] = useState<'rtsp' | 'rtmp' | 'ip' | 'p2'>('rtsp')
  const [locationMode, setLocationMode] = useState<'text' | 'address' | 'coords' | 'url'>('text')
  const [formData, setFormData] = useState<CameraCreateRequest>({
    name: '',
    stream_url: '',
    location: '',
    recording_retention_days: 30,
  })
  const [locationInput, setLocationInput] = useState('')
  const [addressData, setAddressData] = useState({
    street: '',
    number: '',
    neighborhood: '',
    city: '',
    state: '',
  })
  const [coordsData, setCoordsData] = useState({
    latitude: '',
    longitude: '',
  })

  // Extrai coordenadas de URL do Google Maps
  const extractCoordinatesFromUrl = (url: string) => {
    try {
      const patterns = [
        /@([+-]?\d+\.\d+),([+-]?\d+\.\d+)/,  // @-20.5039951,-54.6228302
        /!3d([+-]?\d+\.\d+)!4d([+-]?\d+\.\d+)/,  // !3d-20.5039951!4d-54.6228302
        /[?&]q=([+-]?\d+\.\d+),([+-]?\d+\.\d+)/,  // ?q=-20.5039951,-54.6228302
      ]
      
      for (const pattern of patterns) {
        const match = url.match(pattern)
        if (match) {
          return {
            latitude: parseFloat(match[1]),
            longitude: parseFloat(match[2]),
          }
        }
      }
    } catch (e) {
      console.error('Erro ao extrair coordenadas:', e)
    }
    return null
  }

  const handleLocationChange = (value: string) => {
    setLocationInput(value)
    
    // Auto-detectar tipo de entrada
    if (value.includes('google.com/maps') || value.includes('maps.google.com')) {
      setLocationMode('url')
      const coords = extractCoordinatesFromUrl(value)
      if (coords) {
        setFormData(f => ({
          ...f,
          location: value,
          latitude: coords.latitude,
          longitude: coords.longitude,
          maps_url: value,
        }))
      }
    } else {
      setLocationMode('text')
      setFormData(f => ({ ...f, location: value }))
    }
  }

  const handleAddressChange = () => {
    const parts = []
    if (addressData.street) {
      let street = addressData.street
      if (addressData.number) street += `, ${addressData.number}`
      parts.push(street)
    }
    if (addressData.neighborhood) parts.push(addressData.neighborhood)
    if (addressData.city) parts.push(addressData.city)
    if (addressData.state) parts.push(addressData.state)
    
    setFormData(f => ({
      ...f,
      location: parts.join(' - '),
      address_street: addressData.street,
      address_number: addressData.number,
      address_neighborhood: addressData.neighborhood,
      address_city: addressData.city,
      address_state: addressData.state,
    }))
  }

  const handleCoordsChange = () => {
    const lat = parseFloat(coordsData.latitude)
    const lng = parseFloat(coordsData.longitude)
    if (!isNaN(lat) && !isNaN(lng)) {
      setFormData(f => ({
        ...f,
        latitude: lat,
        longitude: lng,
        location: `${lat}, ${lng}`,
      }))
    }
  }

  const createMutation = useMutation({
    mutationFn: async (data: CameraCreateRequest) => {
      const camera = await cameraService.create(data)
      await streamingService.provisionCamera(camera.id, data.stream_url, data.name)
      return camera
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  if (mode === 'select') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
        <div className="absolute inset-0 bg-black/80" onClick={onClose} />
        <Card className="relative w-full max-w-md animate-slide-in">
          <CardHeader>
            <CardTitle>Adicionar Câmera</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button onClick={() => setMode('easy')} className="w-full h-20 text-lg" variant="outline" disabled>
              <div>
                <div className="font-semibold">Modo Fácil</div>
                <div className="text-xs text-muted-foreground">Em desenvolvimento</div>
              </div>
            </Button>
            <Button onClick={() => setMode('advanced')} className="w-full h-20 text-lg" variant="outline">
              <div>
                <div className="font-semibold">Modo Avançado</div>
                <div className="text-xs text-muted-foreground">URL completa</div>
              </div>
            </Button>
            <Button onClick={onClose} variant="ghost" className="w-full">
              Cancelar
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (mode === 'easy') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
        <div className="absolute inset-0 bg-black/80" onClick={onClose} />
        <Card className="relative w-full max-w-md animate-slide-in max-h-[90vh] overflow-y-auto">
          <CardHeader>
            <CardTitle>Modo Fácil - Selecione o Protocolo</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Protocolo</label>
                <div className="grid grid-cols-2 gap-2">
                  {(['rtsp', 'rtmp', 'ip', 'p2'] as const).map((p) => (
                    <Button
                      key={p}
                      type="button"
                      variant={protocol === p ? 'default' : 'outline'}
                      onClick={() => setProtocol(p)}
                      className="h-16"
                    >
                      {p === 'ip' ? 'IP/HTTP' : p === 'p2' ? 'P2P' : p.toUpperCase()}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Nome *</label>
                <Input
                  placeholder="Ex: Entrada Principal"
                  value={formData.name}
                  onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))}
                  required
                />
              </div>

              {protocol === 'rtsp' && (
                <div className="space-y-2">
                  <label className="text-sm font-medium">URL RTSP *</label>
                  <Input
                    placeholder="rtsp://usuario:senha@192.168.1.100:554/stream"
                    value={formData.stream_url}
                    onChange={(e) => setFormData(f => ({ ...f, stream_url: e.target.value }))}
                    required
                  />
                </div>
              )}

              {protocol === 'rtmp' && (
                <div className="space-y-2">
                  <label className="text-sm font-medium">URL RTMP *</label>
                  <Input
                    placeholder="rtmp://192.168.1.100:1935/live/stream"
                    value={formData.stream_url}
                    onChange={(e) => setFormData(f => ({ ...f, stream_url: e.target.value }))}
                    required
                  />
                </div>
              )}

              {protocol === 'p2' && (
                <>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">ID P2P *</label>
                    <Input
                      placeholder="XXXXX-XXXXX-XXXXX"
                      onChange={(e) => setFormData(f => ({ ...f, stream_url: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="p-3 rounded-lg bg-yellow-50 text-sm text-yellow-800">
                    ⚠️ P2P requer gateway externo. Insira a URL RTSP do gateway.
                  </div>
                </>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium">Localização *</label>
                <div className="flex gap-2 mb-2">
                  <Button
                    type="button"
                    size="sm"
                    variant={locationMode === 'text' ? 'default' : 'outline'}
                    onClick={() => setLocationMode('text')}
                  >
                    Texto
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant={locationMode === 'address' ? 'default' : 'outline'}
                    onClick={() => setLocationMode('address')}
                  >
                    Endereço
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant={locationMode === 'coords' ? 'default' : 'outline'}
                    onClick={() => setLocationMode('coords')}
                  >
                    Coordenadas
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant={locationMode === 'url' ? 'default' : 'outline'}
                    onClick={() => setLocationMode('url')}
                  >
                    URL Maps
                  </Button>
                </div>

                {locationMode === 'text' && (
                  <Input
                    placeholder="Digite o local"
                    value={locationInput}
                    onChange={(e) => handleLocationChange(e.target.value)}
                    required
                  />
                )}

                {locationMode === 'address' && (
                  <div className="space-y-2">
                    <Input
                      placeholder="Rua"
                      value={addressData.street}
                      onChange={(e) => {
                        setAddressData(d => ({ ...d, street: e.target.value }))
                        handleAddressChange()
                      }}
                      required
                    />
                    <div className="grid grid-cols-2 gap-2">
                      <Input
                        placeholder="Número"
                        value={addressData.number}
                        onChange={(e) => {
                          setAddressData(d => ({ ...d, number: e.target.value }))
                          handleAddressChange()
                        }}
                      />
                      <Input
                        placeholder="Bairro"
                        value={addressData.neighborhood}
                        onChange={(e) => {
                          setAddressData(d => ({ ...d, neighborhood: e.target.value }))
                          handleAddressChange()
                        }}
                      />
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <Input
                        placeholder="Cidade"
                        className="col-span-2"
                        value={addressData.city}
                        onChange={(e) => {
                          setAddressData(d => ({ ...d, city: e.target.value }))
                          handleAddressChange()
                        }}
                        required
                      />
                      <Input
                        placeholder="UF"
                        maxLength={2}
                        value={addressData.state}
                        onChange={(e) => {
                          setAddressData(d => ({ ...d, state: e.target.value.toUpperCase() }))
                          handleAddressChange()
                        }}
                      />
                    </div>
                  </div>
                )}

                {locationMode === 'coords' && (
                  <div className="grid grid-cols-2 gap-2">
                    <Input
                      placeholder="Latitude"
                      type="number"
                      step="any"
                      value={coordsData.latitude}
                      onChange={(e) => {
                        setCoordsData(d => ({ ...d, latitude: e.target.value }))
                        handleCoordsChange()
                      }}
                      required
                    />
                    <Input
                      placeholder="Longitude"
                      type="number"
                      step="any"
                      value={coordsData.longitude}
                      onChange={(e) => {
                        setCoordsData(d => ({ ...d, longitude: e.target.value }))
                        handleCoordsChange()
                      }}
                      required
                    />
                  </div>
                )}

                {locationMode === 'url' && (
                  <Input
                    placeholder="Cole a URL do Google Maps"
                    value={locationInput}
                    onChange={(e) => handleLocationChange(e.target.value)}
                    required
                  />
                )}

                {formData.latitude && formData.longitude && (
                  <p className="text-xs text-green-600">
                    ✓ Coordenadas: {formData.latitude.toFixed(6)}, {formData.longitude.toFixed(6)}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Plano de Gravação *</label>
                <select
                  className="w-full px-3 py-2 border rounded-md dark:bg-gray-700"
                  value={formData.recording_retention_days}
                  onChange={(e) => setFormData(f => ({ ...f, recording_retention_days: parseInt(e.target.value) }))}
                  required
                >
                  {RETENTION_PLANS.map(plan => (
                    <option key={plan.value} value={plan.value}>
                      {plan.label}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500">
                  {RETENTION_PLANS.find(p => p.value === formData.recording_retention_days)?.description}
                </p>
              </div>

              {createMutation.isError && (
                <div className="p-3 rounded-lg bg-destructive/10 text-sm text-destructive">
                  Erro ao criar câmera. Verifique os dados.
                </div>
              )}

              <div className="flex gap-3">
                <Button type="button" variant="outline" className="flex-1" onClick={() => setMode('select')}>
                  Voltar
                </Button>
                <Button type="submit" className="flex-1" disabled={createMutation.isPending}>
                  {createMutation.isPending ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Criando...</>
                  ) : 'Criar'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <Card className="relative w-full max-w-md animate-slide-in">
        <CardHeader>
          <CardTitle>Modo Avançado</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Nome *</label>
              <Input
                placeholder="Ex: Entrada Principal"
                value={formData.name}
                onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">URL do Stream *</label>
              <Input
                placeholder="rtsp://usuario:senha@ip:porta/stream"
                value={formData.stream_url}
                onChange={(e) => setFormData(f => ({ ...f, stream_url: e.target.value }))}
                required
              />
              <p className="text-xs text-muted-foreground">
                RTSP, RTMP, HTTP ou qualquer URL suportada
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Localização *</label>
              <div className="flex gap-2 mb-2">
                <Button
                  type="button"
                  size="sm"
                  variant={locationMode === 'text' ? 'default' : 'outline'}
                  onClick={() => setLocationMode('text')}
                >
                  Texto
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={locationMode === 'address' ? 'default' : 'outline'}
                  onClick={() => setLocationMode('address')}
                >
                  Endereço
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={locationMode === 'coords' ? 'default' : 'outline'}
                  onClick={() => setLocationMode('coords')}
                >
                  Coordenadas
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={locationMode === 'url' ? 'default' : 'outline'}
                  onClick={() => setLocationMode('url')}
                >
                  URL Maps
                </Button>
              </div>

              {locationMode === 'text' && (
                <Input
                  placeholder="Digite o local"
                  value={locationInput}
                  onChange={(e) => handleLocationChange(e.target.value)}
                  required
                />
              )}

              {locationMode === 'address' && (
                <div className="space-y-2">
                  <Input
                    placeholder="Rua"
                    value={addressData.street}
                    onChange={(e) => {
                      setAddressData(d => ({ ...d, street: e.target.value }))
                      handleAddressChange()
                    }}
                    required
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <Input
                      placeholder="Número"
                      value={addressData.number}
                      onChange={(e) => {
                        setAddressData(d => ({ ...d, number: e.target.value }))
                        handleAddressChange()
                      }}
                    />
                    <Input
                      placeholder="Bairro"
                      value={addressData.neighborhood}
                      onChange={(e) => {
                        setAddressData(d => ({ ...d, neighborhood: e.target.value }))
                        handleAddressChange()
                      }}
                    />
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <Input
                      placeholder="Cidade"
                      className="col-span-2"
                      value={addressData.city}
                      onChange={(e) => {
                        setAddressData(d => ({ ...d, city: e.target.value }))
                        handleAddressChange()
                      }}
                      required
                    />
                    <Input
                      placeholder="UF"
                      maxLength={2}
                      value={addressData.state}
                      onChange={(e) => {
                        setAddressData(d => ({ ...d, state: e.target.value.toUpperCase() }))
                        handleAddressChange()
                      }}
                    />
                  </div>
                </div>
              )}

              {locationMode === 'coords' && (
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    placeholder="Latitude"
                    type="number"
                    step="any"
                    value={coordsData.latitude}
                    onChange={(e) => {
                      setCoordsData(d => ({ ...d, latitude: e.target.value }))
                      handleCoordsChange()
                    }}
                    required
                  />
                  <Input
                    placeholder="Longitude"
                    type="number"
                    step="any"
                    value={coordsData.longitude}
                    onChange={(e) => {
                      setCoordsData(d => ({ ...d, longitude: e.target.value }))
                      handleCoordsChange()
                    }}
                    required
                  />
                </div>
              )}

              {locationMode === 'url' && (
                <Input
                  placeholder="Cole a URL do Google Maps"
                  value={locationInput}
                  onChange={(e) => handleLocationChange(e.target.value)}
                  required
                />
              )}

              {formData.latitude && formData.longitude && (
                <p className="text-xs text-green-600">
                  ✓ Coordenadas: {formData.latitude.toFixed(6)}, {formData.longitude.toFixed(6)}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Plano de Gravação *</label>
              <select
                className="w-full px-3 py-2 border rounded-md dark:bg-gray-700"
                value={formData.recording_retention_days}
                onChange={(e) => setFormData(f => ({ ...f, recording_retention_days: parseInt(e.target.value) }))}
                required
              >
                {RETENTION_PLANS.map(plan => (
                  <option key={plan.value} value={plan.value}>
                    {plan.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500">
                {RETENTION_PLANS.find(p => p.value === formData.recording_retention_days)?.description}
              </p>
            </div>

            {createMutation.isError && (
              <div className="p-3 rounded-lg bg-destructive/10 text-sm text-destructive">
                Erro ao criar câmera. Verifique os dados.
              </div>
            )}

            <div className="flex gap-3">
              <Button type="button" variant="outline" className="flex-1" onClick={() => setMode('select')}>
                Voltar
              </Button>
              <Button type="submit" className="flex-1" disabled={createMutation.isPending}>
                {createMutation.isPending ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Criando...</>
                ) : 'Criar Câmera'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
