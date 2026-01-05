// Component: ROI Drawer
import React, { useRef, useState, useEffect } from 'react';
import { Point } from '../../domain/value-objects/Point';

interface ROIDrawerProps {
  videoWidth: number;
  videoHeight: number;
  onComplete: (points: Point[]) => void;
  existingPoints?: Point[];
}

export const ROIDrawer: React.FC<ROIDrawerProps> = ({
  videoWidth,
  videoHeight,
  onComplete,
  existingPoints = []
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [points, setPoints] = useState<Point[]>(existingPoints);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    drawPolygon();
  }, [points]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newPoint = new Point(x, y);
    setPoints([...points, newPoint]);
    setIsDrawing(true);
  };

  const drawPolygon = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Limpa canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (points.length === 0) return;

    // Desenha polígono
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }

    if (points.length > 2) {
      ctx.closePath();
      ctx.fillStyle = 'rgba(0, 255, 0, 0.2)';
      ctx.fill();
    }

    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Desenha pontos
    points.forEach((point, index) => {
      ctx.beginPath();
      ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
      ctx.fillStyle = '#00ff00';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();
    });
  };

  const handleComplete = () => {
    if (points.length >= 3) {
      onComplete(points);
      setIsDrawing(false);
    }
  };

  const handleClear = () => {
    setPoints([]);
    setIsDrawing(false);
  };

  return (
    <div className="roi-drawer">
      <canvas
        ref={canvasRef}
        width={videoWidth}
        height={videoHeight}
        onClick={handleCanvasClick}
        style={{ cursor: 'crosshair', border: '2px solid #00ff00' }}
      />
      <div className="roi-controls">
        <button onClick={handleComplete} disabled={points.length < 3}>
          Concluir ROI ({points.length} pontos)
        </button>
        <button onClick={handleClear}>Limpar</button>
      </div>
    </div>
  );
};
