import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { Camera, RefreshCw, Save, X } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface WebcamCaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCapture: (imageSrc: string) => void;
}

export const WebcamCaptureModal: React.FC<WebcamCaptureModalProps> = ({
  isOpen,
  onClose,
  onCapture,
}) => {
  const webcamRef = useRef<Webcam>(null);
  const [imgSrc, setImgSrc] = useState<string | null>(null);

  // Configurações da webcam para garantir boa qualidade na miniatura
  const videoConstraints = {
    width: 720,
    height: 480,
    facingMode: "user"
  };

  // Função para capturar a foto
  const capture = useCallback(() => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setImgSrc(imageSrc);
    }
  }, [webcamRef]);

  // Função para confirmar e enviar a imagem para o componente pai
  const handleConfirm = () => {
    if (imgSrc) {
      onCapture(imgSrc);
      setImgSrc(null); // Limpa após salvar
      onClose();
    }
  };

  // Função para tentar novamente (limpa a foto tirada)
  const retake = () => {
    setImgSrc(null);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Capturar Miniatura</DialogTitle>
          <DialogDescription>
            Posicione a câmara para tirar uma foto de referência para o sistema.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col items-center justify-center p-4 bg-muted/50 rounded-lg min-h-[300px]">
          {imgSrc ? (
            // Exibir a foto capturada
            <div className="relative w-full aspect-video rounded-md overflow-hidden border-2 border-primary">
              <img 
                src={imgSrc} 
                alt="Captura da webcam" 
                className="w-full h-full object-cover"
              />
            </div>
          ) : (
            // Exibir o feed da webcam ao vivo
            <div className="relative w-full aspect-video rounded-md overflow-hidden bg-black shadow-inner">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                width="100%"
                height="100%"
                videoConstraints={videoConstraints}
                className="w-full h-full object-cover"
                onUserMediaError={() => alert('Erro ao acessar a webcam')}
              />
            </div>
          )}
        </div>

        <DialogFooter className="flex sm:justify-between gap-2">
          {imgSrc ? (
            <>
              <Button variant="outline" onClick={retake} className="flex-1 sm:flex-none">
                <RefreshCw className="mr-2 h-4 w-4" />
                Tentar Novamente
              </Button>
              <Button onClick={handleConfirm} className="flex-1 sm:flex-none">
                <Save className="mr-2 h-4 w-4" />
                Usar Esta Foto
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" onClick={onClose}>
                Cancelar
              </Button>
              <Button onClick={capture} className="flex-1 sm:flex-none">
                <Camera className="mr-2 h-4 w-4" />
                Capturar Foto
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};