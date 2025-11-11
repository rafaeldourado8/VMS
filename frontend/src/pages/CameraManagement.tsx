import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import api from '@/lib/axios';
import { useToast } from '@/hooks/use-toast';

interface Camera {
  id: number;
  name: string;
  location: string;
  status: string;
  stream_url: string;
  detection_settings?: string;
}

const CameraManagement = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCamera, setEditingCamera] = useState<Camera | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    stream_url: '',
    detection_settings: '{}',
  });
  const { toast } = useToast();

  const fetchCameras = async () => {
    try {
      const response = await api.get('/cameras/');
      setCameras(response.data);
    } catch (error) {
      toast({
        title: 'Erro ao carregar câmeras',
        variant: 'destructive',
      });
    }
  };

  useEffect(() => {
    fetchCameras();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingCamera) {
        await api.put(`/cameras/${editingCamera.id}/`, formData);
        toast({ title: 'Câmera atualizada com sucesso' });
      } else {
        await api.post('/cameras/', formData);
        toast({ title: 'Câmera adicionada com sucesso' });
      }
      fetchCameras();
      setIsDialogOpen(false);
      resetForm();
    } catch (error) {
      toast({
        title: 'Erro ao salvar câmera',
        variant: 'destructive',
      });
    }
  };

  const handleEdit = (camera: Camera) => {
    setEditingCamera(camera);
    setFormData({
      name: camera.name,
      location: camera.location,
      stream_url: camera.stream_url,
      detection_settings: camera.detection_settings || '{}',
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir esta câmera?')) return;
    
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

  const resetForm = () => {
    setFormData({
      name: '',
      location: '',
      stream_url: '',
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
                <Label htmlFor="location">Localização</Label>
                <Input
                  id="location"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="stream_url">URL do Stream</Label>
                <Input
                  id="stream_url"
                  value={formData.stream_url}
                  onChange={(e) => setFormData({ ...formData, stream_url: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="detection_settings">Configurações de Detecção (JSON)</Label>
                <Input
                  id="detection_settings"
                  value={formData.detection_settings}
                  onChange={(e) => setFormData({ ...formData, detection_settings: e.target.value })}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" className="flex-1">Salvar</Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsDialogOpen(false)}
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
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CameraManagement;
