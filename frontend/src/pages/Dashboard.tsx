import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Camera, CheckCircle2, FileSearch } from 'lucide-react';
import api from '@/lib/axios';
import { useToast } from '@/hooks/use-toast';
import CameraMap from '@/components/CameraMap';

interface DashboardStats {
  total_cameras: number;
  online_cameras: number;
  total_detections_today: number;
}

interface CameraLocation {
  id: number;
  name: string;
  location: string;
  latitude: number;
  longitude: number;
  status: string;
}

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [cameras, setCameras] = useState<CameraLocation[]>([]);
  const { toast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, camerasRes] = await Promise.all([
          api.get('/dashboard/stats/'),
          api.get('/cameras/')
        ]);
        setStats(statsRes.data);
        setCameras(camerasRes.data.results);
      } catch (error) {
        toast({
          title: 'Erro ao carregar dados',
          description: 'Não foi possível carregar as informações do dashboard',
          variant: 'destructive',
        });
      }
    };

    fetchData();
  }, [toast]);

  const statCards = [
    {
      title: 'Total de Câmeras',
      value: stats?.total_cameras || 0,
      icon: Camera,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      title: 'Câmeras Online',
      value: stats?.online_cameras || 0,
      icon: CheckCircle2,
      color: 'text-success',
      bgColor: 'bg-success/10',
    },
    {
      title: 'Detecções Hoje',
      value: stats?.total_detections_today || 0,
      icon: FileSearch,
      color: 'text-warning',
      bgColor: 'bg-warning/10',
    },
  ];

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Visão geral do sistema GT-Vision</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {statCards.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Map */}
      <Card>
        <CardHeader>
          <CardTitle>Localização das Câmeras</CardTitle>
        </CardHeader>
        <CardContent>
          <CameraMap cameras={cameras} />
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
