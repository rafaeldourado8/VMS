// VMS/frontend/src/components/FullscreenWrapper.tsx
import React, { useRef, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Maximize, Minimize } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FullscreenWrapperProps {
  children: React.ReactNode;
  className?: string;
  onFullscreenChange?: (isFullscreen: boolean) => void;
}

export const FullscreenWrapper = ({ children, className, onFullscreenChange }: FullscreenWrapperProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const toggleFullscreen = async () => {
    if (!document.fullscreenElement) {
      await containerRef.current?.requestFullscreen();
    } else {
      await document.exitFullscreen();
    }
  };

  useEffect(() => {
    const handleChange = () => {
      const isFull = !!document.fullscreenElement;
      setIsFullscreen(isFull);
      onFullscreenChange?.(isFull);
    };
    
    document.addEventListener('fullscreenchange', handleChange);
    return () => document.removeEventListener('fullscreenchange', handleChange);
  }, [onFullscreenChange]);

  return (
    <div 
      ref={containerRef} 
      className={cn(
        "relative group bg-black transition-all duration-300", 
        // Se estiver em fullscreen, força ocupar a tela toda
        isFullscreen ? "w-full h-full fixed inset-0 z-50 flex items-center justify-center" : className
      )}
    >
      {children}

      {/* Botão Flutuante de Controle (aparece no hover ou se estiver fullscreen) */}
      <Button
        variant="ghost"
        size="icon"
        onClick={toggleFullscreen}
        className={cn(
          "absolute top-4 right-4 z-50 rounded-full text-white bg-black/40 hover:bg-black/60 backdrop-blur-md transition-opacity",
          isFullscreen ? "opacity-0 group-hover:opacity-100" : ""
        )}
      >
        {isFullscreen ? <Minimize className="h-5 w-5" /> : <Maximize className="h-5 w-5" />}
      </Button>
    </div>
  );
};