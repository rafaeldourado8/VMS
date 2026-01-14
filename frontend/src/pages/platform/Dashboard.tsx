import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, Users, CreditCard, LogOut } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button } from '@/components/ui';
import axios from 'axios';

interface Stats {
  organizations: number;
  subscriptions: number;
  users: number;
}

export default function PlatformDashboard() {
  const [stats, setStats] = useState<Stats>({ organizations: 0, subscriptions: 0, users: 0 });
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('platform_token');
    if (!token) {
      navigate('/platform/login');
      return;
    }
    loadStats();
  }, []);

  const loadStats = async () => {
    const token = localStorage.getItem('platform_token');
    try {
      const [orgs, subs, users] = await Promise.all([
        axios.get('http://localhost:8000/api/organizations/', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get('http://localhost:8000/api/subscriptions/', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get('http://localhost:8000/api/usuarios/', {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      setStats({
        organizations: orgs.data.length || orgs.data.count || 0,
        subscriptions: subs.data.length || subs.data.count || 0,
        users: users.data.length || users.data.count || 0
      });
    } catch (err) {
      console.error('Erro ao carregar stats:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('platform_token');
    localStorage.removeItem('platform_user');
    navigate('/platform/login');
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-xl font-bold text-white">Platform Admin</h1>
            <Button variant="ghost" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              Sair
            </Button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Organizations</p>
                  <p className="text-3xl font-bold text-white mt-2">{stats.organizations}</p>
                </div>
                <Building2 className="w-12 h-12 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Subscriptions</p>
                  <p className="text-3xl font-bold text-white mt-2">{stats.subscriptions}</p>
                </div>
                <CreditCard className="w-12 h-12 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Total Users</p>
                  <p className="text-3xl font-bold text-white mt-2">{stats.users}</p>
                </div>
                <Users className="w-12 h-12 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button onClick={() => navigate('/platform/organizations')} className="w-full">
                Gerenciar Organizations
              </Button>
              <Button
                variant="outline"
                onClick={() => window.open('http://localhost:8000/admin', '_blank')}
                className="w-full"
              >
                Django Admin (Full Access)
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
