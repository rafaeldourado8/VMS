import { cn } from "@/lib/utils";
import { Signal, WifiOff, Loader2, Video } from "lucide-react";

type StatusType = "online" | "offline" | "loading" | "lpr" | string;

interface CameraStatusBadgeProps {
  status: StatusType;
  className?: string;
  showIcon?: boolean;
}

export const CameraStatusBadge = ({ status, className, showIcon = false }: CameraStatusBadgeProps) => {
  const config: Record<string, { label: string; color: string; icon: any }> = {
    online: { 
      label: "Online", 
      color: "bg-green-500/10 text-green-600 border-green-200", 
      icon: Signal 
    },
    offline: { 
      label: "Offline", 
      color: "bg-red-500/10 text-red-600 border-red-200", 
      icon: WifiOff 
    },
    loading: { 
      label: "Conectando...", 
      color: "bg-yellow-500/10 text-yellow-600 border-yellow-200", 
      icon: Loader2 
    },
    lpr: { 
      label: "LPR Ativo", 
      color: "bg-purple-500/10 text-purple-600 border-purple-200", 
      icon: Video 
    },
  };

  const current = config[status] || config.offline;
  const Icon = current.icon;

  return (
    <div
      className={cn(
        "flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[10px] font-bold uppercase tracking-wider w-fit transition-colors",
        current.color,
        className
      )}
    >
      {/* Bolinha pulsante se estiver online ou loading */}
      {(status === 'online' || status === 'loading') && (
        <span className="relative flex h-1.5 w-1.5 mr-0.5">
          <span className={cn("animate-ping absolute inline-flex h-full w-full rounded-full opacity-75", status === 'online' ? 'bg-green-500' : 'bg-yellow-500')}></span>
          <span className={cn("relative inline-flex rounded-full h-1.5 w-1.5", status === 'online' ? 'bg-green-500' : 'bg-yellow-500')}></span>
        </span>
      )}
      
      {showIcon && <Icon className={cn("w-3 h-3", status === 'loading' && "animate-spin")} />}
      {current.label}
    </div>
  );
};