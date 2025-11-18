import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea'; // Importar Textarea
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import api from '@/lib/axios';
import { useToast } from '@/hooks/use-toast';

// --- 1. Atualizar a Interface ---
interface Camera {
  id: number;
  name: string;
  location: string;
  status: string;
  stream_url: string;
  latitude?: number | null; // Alterado para aceitar null
  longitude?: number | null; // Alterado para aceitar null
  detection_settings?: any;
}

const CameraManagement = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCamera, setEditingCamera] = useState<Camera | null>(null);
  
  // --- 2. Atualizar o estado do formulário ---
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    stream_url: '',
    latitude: '', // Usar string para o input
    longitude: '', // Usar string para o input
    detection_settings: '{}', // Default para JSON
  });
  const { toast } = useToast();

  const fetchCameras = async () => {
    try {
      const response = await api.get('/cameras/');
      const raw = response.data;

      // Suporta resposta paginada ({ results: [...] }) ou array direto
      const list = Array.isArray(raw) ? raw : (Array.isArray(raw?.results) ? raw.results : []);

      const normalized = list.map((c: any) => ({
        id: c.id,
        name: c.name ?? '',
        location: c.location ?? '',
        status: c.status ?? 'offline',
        stream_url: c.stream_url ?? '',
        latitude: c.latitude ?? null,
        longitude: c.longitude ?? null,
        detection_settings: c.detection_settings ?? {},
      }));

      setCameras(normalized);
    } catch (error) {
      console.error('Erro ao carregar câmeras:', error);
      toast({
        title: 'Erro ao carregar câmeras',
        variant: 'destructive',
      });
    }
  };

  useEffect(() => {
    fetchCameras();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [toast]);

  // --- 3. Atualizar o HandleSubmit ---
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Prepara os dados para enviar (converte para números e JSON)
      const dataToSubmit = {
        ...formData,
        latitude: formData.latitude ? parseFloat(formData.latitude) : null,
        longitude: formData.longitude ? parseFloat(formData.longitude) : null,
        // Valida o JSON antes de enviar
        detection_settings: JSON.parse(formData.detection_settings || '{}')
      };

      if (editingCamera) {
        await api.put(`/cameras/${editingCamera.id}/`, dataToSubmit);
        toast({ title: 'Câmera atualizada com sucesso' });
      } else {
        await api.post('/cameras/', dataToSubmit);
        toast({ title: 'Câmera adicionada com sucesso' });
      }
      fetchCameras();
      setIsDialogOpen(false);
      resetForm();
    } catch (error: any) {
      // Captura erros de JSON inválido
      if (error instanceof SyntaxError) {
         toast({
          title: 'Erro no formulário',
          description: 'O campo "Configurações de Detecção" não é um JSON válido.',
          variant: 'destructive',
        });
      } else {
        // Mostra erros de validação do backend (ex: URL RTSP inválido)
        const errorMessages = error.response?.data ? Object.values(error.response.data).join(' ') : 'Verifique os campos.';
        toast({
          title: 'Erro ao salvar câmera',
          description: errorMessages,
          variant: 'destructive',
        });
      }
    }
  };

  // --- 4. Atualizar o HandleEdit ---
  const handleEdit = (camera: Camera) => {
    setEditingCamera(camera);
    setFormData({
      name: camera.name,
      location: camera.location,
      stream_url: camera.stream_url,
      latitude: camera.latitude?.toString() || '',
      longitude: camera.longitude?.toString() || '',
      detection_settings: camera.detection_settings ? JSON.stringify(camera.detection_settings, null, 2) : '{}',
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Tem certeza de que deseja excluir esta câmera?')) return;
    
    try {
      await api.delete(`/cameras/${id}/`);
      toast({ title: 'Câmera excluída com sucesso' });
      fetchCameras();
    } catch (error) {
      toast({
        title: 'Erro ao excluir câmera',
        variant: 'destructive',
      });
    }
  };

  // --- 5. Atualizar o ResetForm ---
  const resetForm = () => {
    setFormData({
      name: '',
      location: '',
      stream_url: '',
      latitude: '',
      longitude: '',
      detection_settings: '{}',
    });
    setEditingCamera(null);
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Gerenciamento de Câmeras</h1>
          <p className="text-muted-foreground">Gerencie todas as câmeras do sistema</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm} className="gap-2">
              <Plus className="h-4 w-4" />
              Adicionar Câmera
            </Button>
          </DialogTrigger>
          {/* --- 6. Atualizar o Formulário (Adicionar campos) --- */}
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingCamera ? 'Editar Câmera' : 'Nova Câmera'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nome</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Localização (Ex: Endereço)</Label>
                <Input
                  id="location"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="Ex: Rua Principal, 123"
                  required
                />
              </div>

              {/* --- Campos Adicionados --- */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="latitude">Latitude</Label>
                  <Input
                    id="latitude"
                    type="number"
                    step="any"
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                    placeholder="-19.000000"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="longitude">Longitude</Label>
                  <Input
                    id="longitude"
                    type="number"
                    step="any"
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                    placeholder="-54.000000"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="stream_url">URL do Stream (RTSP)</Label>
                <Input
                  id="stream_url"
                  value={formData.stream_url}
                  onChange={(e) => setFormData({ ...formData, stream_url: e.target.value })}
                  placeholder="rtsp://usuario:senha@ip:porta/stream"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="detection_settings">Configurações de Detecção (JSON)</Label>
                <Textarea // Usar Textarea para JSON
                  id="detection_settings"
                  value={formData.detection_settings}
                  onChange={(e) => setFormData({ ...formData, detection_settings: e.target.value })}
                  rows={3}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" className="flex-1">Salvar</Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => { setIsDialogOpen(false); resetForm(); }}
                  className="flex-1"
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Câmeras Cadastradas ({cameras.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b">
                <tr className="text-left">
                  <th className="pb-3 font-medium text-muted-foreground">Nome</th>
                  <th className="pb-3 font-medium text-muted-foreground">Localização</th>
                  <th className="pb-3 font-medium text-muted-foreground">Status</th>
                  <th className="pb-3 font-medium text-muted-foreground">URL do Stream</th>
                  <th className="pb-3 font-medium text-muted-foreground">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {cameras.map((camera) => (
                  <tr key={camera.id} className="hover:bg-muted/50">
                    <td className="py-3 font-medium">{camera.name}</td>
                    <td className="py-3">{camera.location}</td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          camera.status === 'online'
                            ? 'bg-success/10 text-success'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        {camera.status}
                      </span>
                    </td>
                    <td className="py-3 text-sm text-muted-foreground truncate max-w-xs">
                      {camera.stream_url}
                    </td>
                    <td className="py-3">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEdit(camera)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(camera.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {cameras.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-muted-foreground">
                      Nenhuma câmera cadastrada.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CameraManagement;