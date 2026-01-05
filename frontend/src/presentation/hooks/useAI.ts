// Hook: useAI
import { useState } from 'react';
import { Point } from '../../domain/value-objects/Point';
import { apiClient } from '../../infrastructure/api/ApiClient';
import { ToggleAIUseCase } from '../../application/use-cases/ToggleAIUseCase';
import { DrawROIUseCase } from '../../application/use-cases/DrawROIUseCase';

export const useAI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleAIUseCase = new ToggleAIUseCase(apiClient);
  const drawROIUseCase = new DrawROIUseCase(apiClient);

  const toggleAI = async (cameraId: number, enabled: boolean) => {
    setLoading(true);
    setError(null);
    try {
      await toggleAIUseCase.execute(cameraId, enabled);
    } catch (err: any) {
      setError(err.message || 'Erro ao alternar IA');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateROI = async (cameraId: number, points: Point[]) => {
    setLoading(true);
    setError(null);
    try {
      await drawROIUseCase.execute(cameraId, points);
    } catch (err: any) {
      setError(err.message || 'Erro ao atualizar ROI');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getAIStatus = async (cameraId: number) => {
    setLoading(true);
    setError(null);
    try {
      return await apiClient.getAIStatus(cameraId);
    } catch (err: any) {
      setError(err.message || 'Erro ao obter status da IA');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    toggleAI,
    updateROI,
    getAIStatus
  };
};
