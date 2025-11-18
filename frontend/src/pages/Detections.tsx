import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FileSpreadsheet, FileText, Search } from 'lucide-react';
import api from '@/lib/axios';
import { useToast } from '@/hooks/use-toast';
import * as XLSX from 'xlsx';

interface Detection {
  id: number;
  plate: string;
  camera_name: string;
  timestamp: string;
  confidence: number;
  image_url?: string;
}

interface Camera {
  id: number;
  name: string;
}

const Detections = () => {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [filters, setFilters] = useState({
    camera_id: '',
    plate: '',
    start_date: '',
    end_date: '',
    brand_model: '',
  });
  const { toast } = useToast();

  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const response = await api.get('/cameras/');
        const raw = response.data;

        // Suporta resposta paginada ({ results: [...] }) ou array direto
        const list = Array.isArray(raw) ? raw : (Array.isArray(raw?.results) ? raw.results : []);

        // Normaliza (caso precise mais campos no futuro)
        const normalized = list.map((c: any) => ({
          id: c.id,
          name: c.name,
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

    fetchCameras();
  }, [toast]);

  const handleSearch = async () => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await api.get(`/detections/?${params.toString()}`);
      const raw = response.data;
      // Se sua API também paginar detecções, trate aqui (ex.: results)
      const list = Array.isArray(raw) ? raw : (Array.isArray(raw?.results) ? raw.results : []);
      setDetections(list);
    } catch (error) {
      console.error('Erro ao buscar detecções:', error);
      toast({
        title: 'Erro ao buscar detecções',
        variant: 'destructive',
      });
    }
  };

  const exportToCSV = () => {
    if (detections.length === 0) {
      toast({
        title: 'Nenhum dado para exportar',
        description: 'Realize uma busca primeiro',
        variant: 'destructive',
      });
      return;
    }

    const csvData = detections.map((detection) => ({
      Placa: detection.plate,
      Câmera: detection.camera_name,
      'Data/Hora': new Date(detection.timestamp).toLocaleString('pt-BR'),
      'Confiança (%)': (detection.confidence * 100).toFixed(1),
    }));

    const headers = Object.keys(csvData[0]).join(',');
    const rows = csvData.map((row) =>
      Object.values(row)
        .map((value) => `"${value}"`)
        .join(',')
    );
    const csv = [headers, ...rows].join('\n');

    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `deteccoes_lpr_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    toast({
      title: 'Exportação concluída',
      description: 'Arquivo CSV baixado com sucesso',
    });
  };

  const exportToExcel = () => {
    if (detections.length === 0) {
      toast({
        title: 'Nenhum dado para exportar',
        description: 'Realize uma busca primeiro',
        variant: 'destructive',
      });
      return;
    }

    const excelData = detections.map((detection) => ({
      Placa: detection.plate,
      Câmera: detection.camera_name,
      'Data/Hora': new Date(detection.timestamp).toLocaleString('pt-BR'),
      'Confiança (%)': (detection.confidence * 100).toFixed(1),
      Timestamp: detection.timestamp,
    }));

    const worksheet = XLSX.utils.json_to_sheet(excelData);
    const columnWidths = [
      { wch: 15 },
      { wch: 25 },
      { wch: 20 },
      { wch: 12 },
      { wch: 20 },
    ];
    worksheet['!cols'] = columnWidths;

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Detecções LPR');

    const infoSheet = XLSX.utils.aoa_to_sheet([
      ['Relatório de Detecções LPR'],
      ['Data de Geração:', new Date().toLocaleString('pt-BR')],
      ['Total de Registros:', detections.length],
      [''],
      ['Filtros Aplicados:'],
      ['Câmera:', filters.camera_id || 'Todas'],
      ['Placa:', filters.plate || 'Todas'],
      ['Data Inicial:', filters.start_date || 'Não especificada'],
      ['Data Final:', filters.end_date || 'Não especificada'],
      ['Marca/Modelo:', filters.brand_model || 'Não especificado'],
    ]);
    XLSX.utils.book_append_sheet(workbook, infoSheet, 'Informações');

    XLSX.writeFile(workbook, `deteccoes_lpr_${new Date().toISOString().split('T')[0]}.xlsx`);

    toast({
      title: 'Exportação concluída',
      description: 'Arquivo Excel baixado com sucesso',
    });
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Detecções LPR</h1>
        <p className="text-muted-foreground">Busque e visualize detecções de placas</p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros de Busca</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Câmera</Label>
              <Select
                value={filters.camera_id}
                onValueChange={(value) => setFilters({ ...filters, camera_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione uma câmera" />
                </SelectTrigger>
                <SelectContent>
                  {Array.isArray(cameras) && cameras.map((camera) => (
                    <SelectItem key={camera.id} value={camera.id.toString()}>
                      {camera.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="plate">Placa</Label>
              <Input
                id="plate"
                placeholder="ABC1234"
                value={filters.plate}
                onChange={(e) => setFilters({ ...filters, plate: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="brand">Marca/Modelo</Label>
              <Input
                id="brand"
                placeholder="Ex: Toyota Corolla"
                value={filters.brand_model}
                onChange={(e) => setFilters({ ...filters, brand_model: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="start_date">Data Inicial</Label>
              <Input
                id="start_date"
                type="date"
                value={filters.start_date}
                onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="end_date">Data Final</Label>
              <Input
                id="end_date"
                type="date"
                value={filters.end_date}
                onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button onClick={handleSearch} className="gap-2">
              <Search className="h-4 w-4" />
              Buscar
            </Button>
            <Button 
              variant="outline" 
              className="gap-2"
              onClick={exportToExcel}
              disabled={detections.length === 0}
            >
              <FileSpreadsheet className="h-4 w-4" />
              Exportar Excel
            </Button>
            <Button 
              variant="outline" 
              className="gap-2"
              onClick={exportToCSV}
              disabled={detections.length === 0}
            >
              <FileText className="h-4 w-4" />
              Exportar CSV
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results Table */}
      <Card>
        <CardHeader>
          <CardTitle>Resultados ({detections.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b">
                <tr className="text-left">
                  <th className="pb-3 font-medium text-muted-foreground">Imagem</th>
                  <th className="pb-3 font-medium text-muted-foreground">Placa</th>
                  <th className="pb-3 font-medium text-muted-foreground">Câmera</th>
                  <th className="pb-3 font-medium text-muted-foreground">Data/Hora</th>
                  <th className="pb-3 font-medium text-muted-foreground">Confiança</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {detections.map((detection) => (
                  <tr key={detection.id} className="hover:bg-muted/50">
                    <td className="py-3">
                      {detection.image_url ? (
                        <img
                          src={detection.image_url}
                          alt="Placa"
                          className="h-12 w-20 object-cover rounded"
                        />
                      ) : (
                        <div className="h-12 w-20 bg-muted rounded flex items-center justify-center text-xs text-muted-foreground">
                          Sem imagem
                        </div>
                      )}
                    </td>
                    <td className="py-3 font-mono font-semibold">{detection.plate}</td>
                    <td className="py-3">{detection.camera_name}</td>
                    <td className="py-3">
                      {new Date(detection.timestamp).toLocaleString('pt-BR')}
                    </td>
                    <td className="py-3">
                      <span className="px-2 py-1 bg-success/10 text-success rounded text-sm">
                        {(detection.confidence * 100).toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
                {detections.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-muted-foreground">
                      Nenhuma detecção encontrada. Use os filtros acima para buscar.
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

export default Detections;