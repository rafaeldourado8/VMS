// Component: AI Toggle
import React, { useState } from 'react';

interface AIToggleProps {
  cameraId: number;
  initialEnabled: boolean;
  onToggle: (cameraId: number, enabled: boolean) => Promise<void>;
}

export const AIToggle: React.FC<AIToggleProps> = ({
  cameraId,
  initialEnabled,
  onToggle
}) => {
  const [enabled, setEnabled] = useState(initialEnabled);
  const [loading, setLoading] = useState(false);

  const handleToggle = async () => {
    setLoading(true);
    try {
      const newState = !enabled;
      await onToggle(cameraId, newState);
      setEnabled(newState);
    } catch (error) {
      console.error('Erro ao alternar IA:', error);
      alert('Erro ao alternar IA');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-toggle">
      <label className="toggle-switch">
        <input
          type="checkbox"
          checked={enabled}
          onChange={handleToggle}
          disabled={loading}
        />
        <span className="slider"></span>
      </label>
      <span className="toggle-label">
        IA {enabled ? 'Ativada' : 'Desativada'}
      </span>
      {loading && <span className="loading-spinner">⏳</span>}
    </div>
  );
};
