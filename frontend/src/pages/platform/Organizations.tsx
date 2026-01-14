import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button } from '@/components/ui';
import axios from 'axios';

interface Organization {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
}

export default function Organizations() {
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('platform_token');
    if (!token) {
      navigate('/platform/login');
      return;
    }
    loadOrgs();
  }, []);

  const loadOrgs = async () => {
    const token = localStorage.getItem('platform_token');
    try {
      const { data } = await axios.get('http://localhost:8000/api/organizations/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOrgs(data.results || data);
    } catch (err) {
      console.error('Erro ao carregar organizations:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-xl font-bold text-white">Organizations</h1>
            <Button variant="ghost" onClick={() => navigate('/platform/dashboard')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar
            </Button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-700/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Slug</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {orgs.map((org) => (
                    <tr key={org.id} className="hover:bg-gray-700/30">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                        {org.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                        {org.slug}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          org.is_active ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'
                        }`}>
                          {org.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                        {new Date(org.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
