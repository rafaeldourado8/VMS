// Hook: useCameras
import { useState, useEffect } from 'react';
import { Camera } from '../../domain/entities/Camera';
import { apiClient } from '../../infrastructure/api/ApiClient';
import { CreateCameraUseCase } from '../../application/use-cases/CreateCameraUseCase';

export const useCameras = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createCameraUseCase = new CreateCameraUseCase(apiClient);

  const fetchCameras = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getCameras();
      setCameras(data);
    } catch (err) {
      setError('Erro ao carregar câmeras');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createCamera = async (data: any) => {
    setLoading(true);
    setError(null);
    try {
      await createCameraUseCase.execute(data);
      await fetchCameras();
    } catch (err: any) {
      setError(err.message || 'Erro ao criar câmera');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteCamera = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.deleteCamera(id);
      await fetchCameras();
    } catch (err) {
      setError('Erro ao deletar câmera');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCameras();
  }, []);

  return {
    cameras,
    loading,
    error,
    fetchCameras,
    createCamera,
    deleteCamera
  };
};
