import React from 'react';

interface ClipTrimmerProps {
  range: { start: number; end: number }; // % de 0 a 100
}

export const ClipTrimmer = ({ range }: ClipTrimmerProps) => {
  return (
    <div 
      className="absolute top-0 bottom-0 pointer-events-none z-20" 
      style={{
        left: `${range.start}%`,
        width: `${range.end - range.start}%`,
        backgroundColor: 'rgba(234, 179, 8, 0.2)', // Amarelo transparente (yellow-500)
        borderLeft: '2px solid #eab308',
        borderRight: '2px solid #eab308',
      }}
    >
      {/* Handles Laterais (Visuais) */}
      <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 w-3 h-6 bg-yellow-500 rounded cursor-ew-resize pointer-events-auto flex items-center justify-center shadow-sm">
        <div className="w-0.5 h-3 bg-black/20" />
      </div>
      <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 w-3 h-6 bg-yellow-500 rounded cursor-ew-resize pointer-events-auto flex items-center justify-center shadow-sm">
        <div className="w-0.5 h-3 bg-black/20" />
      </div>
      
      {/* Label Central */}
      <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-yellow-500 text-black text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
        RECORTAR
      </div>
    </div>
  );
};