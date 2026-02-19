import { useState } from 'react';

interface TimeFilterProps {
  onApply: (filter: { start: string; end: string }) => void;
  onClear: () => void;
  isActive: boolean;
}

export const TimeFilter = ({ onApply, onClear, isActive }: TimeFilterProps) => {
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');

  return (
    <div className="absolute bottom-2 left-2 flex gap-2 items-center bg-white/95 px-3 py-2 rounded-lg border border-gray-300 shadow-lg">
      <span className="text-gray-600 text-xs font-medium">Filtrar:</span>
      <input
        type="time"
        className="bg-white text-gray-900 text-xs px-2 py-1.5 rounded border border-gray-300 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none"
        value={start}
        onChange={(e) => setStart(e.target.value)}
      />
      <span className="text-gray-400 text-xs">→</span>
      <input
        type="time"
        className="bg-white text-gray-900 text-xs px-2 py-1.5 rounded border border-gray-300 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none"
        value={end}
        onChange={(e) => setEnd(e.target.value)}
      />
      <button
        onClick={() => {
          if (start && end) {
            onApply({ start, end });
          }
        }}
        disabled={!start || !end}
        className="text-xs px-3 py-1.5 rounded bg-cyan-400 text-white hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
      >
        Aplicar
      </button>
      {isActive && (
        <button
          onClick={() => {
            onClear();
            setStart('');
            setEnd('');
          }}
          className="text-xs px-2 py-1.5 rounded bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30 transition-colors"
        >
          ×
        </button>
      )}
    </div>
  );
};
