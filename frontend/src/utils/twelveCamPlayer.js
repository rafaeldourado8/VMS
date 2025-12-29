/**
 * Player HLS Ultra-Otimizado para 12 Câmeras
 * Configuração para máxima performance e baixa latência
 */

class UltraOptimizedHLSPlayer {
    constructor(videoElement, streamUrl, options = {}) {
        this.video = videoElement;
        this.streamUrl = streamUrl;
        this.hls = null;
        this.isDestroyed = false;
        
        // Configurações ultra-otimizadas para 12 câmeras
        this.config = {
            // Buffer mínimo para baixa latência
            maxBufferLength: 3,             // 3s buffer máximo
            maxMaxBufferLength: 6,          // 6s buffer absoluto
            maxBufferSize: 10 * 1000 * 1000, // 10MB apenas
            maxBufferHole: 0.2,             // 0.2s gap máximo
            
            // Configurações de fragmento ultra-rápidas
            liveSyncDurationCount: 1,       // Apenas 1 segmento para sync
            liveMaxLatencyDurationCount: 2, // Máximo 2 segmentos de atraso
            
            // Timeouts agressivos
            manifestLoadingTimeOut: 5000,
            manifestLoadingMaxRetry: 1,
            levelLoadingTimeOut: 5000,
            levelLoadingMaxRetry: 1,
            fragLoadingTimeOut: 10000,
            fragLoadingMaxRetry: 1,
            
            // Limpeza automática agressiva
            enableWorker: true,
            lowLatencyMode: true,
            backBufferLength: 2,            // Mantém apenas 2s no buffer traseiro
            
            // Configurações específicas para baixa latência
            nudgeOffset: 0.05,
            nudgeMaxRetry: 1,
            maxSeekHole: 1,
            
            // Desabilita features desnecessárias
            enableSoftwareAES: false,
            enableWebVTT: false,
            enableIMSC1: false,
            enableCEA708Captions: false,
            
            ...options
        };
        
        this.setupPlayer();
        this.setupAggressiveCleanup();
    }
    
    setupPlayer() {
        if (!window.Hls?.isSupported()) {
            console.error('HLS não suportado');
            return;
        }
        
        this.hls = new window.Hls(this.config);
        
        // Event listeners mínimos
        this.hls.on(window.Hls.Events.MANIFEST_PARSED, () => {
            this.video.play().catch(() => {});
        });
        
        // Tratamento de erros simplificado
        this.hls.on(window.Hls.Events.ERROR, (event, data) => {
            if (data.fatal) {
                switch (data.type) {
                    case window.Hls.ErrorTypes.NETWORK_ERROR:
                        this.hls.startLoad();
                        break;
                    case window.Hls.ErrorTypes.MEDIA_ERROR:
                        this.hls.recoverMediaError();
                        break;
                    default:
                        this.restart();
                        break;
                }
            }
        });
        
        // Auto-retry para 404 inicial
        this.hls.on(window.Hls.Events.MANIFEST_LOAD_ERROR, (event, data) => {
            if (data.response?.code === 404) {
                setTimeout(() => {
                    if (!this.isDestroyed && this.hls) {
                        this.hls.loadSource(this.streamUrl);
                    }
                }, 1000); // Retry mais rápido
            }
        });
        
        // Limpeza automática de buffer
        this.hls.on(window.Hls.Events.BUFFER_APPENDED, () => {
            this.aggressiveCleanup();
        });
        
        this.hls.attachMedia(this.video);
        this.hls.loadSource(this.streamUrl);
    }
    
    aggressiveCleanup() {
        if (!this.video) return;
        
        const currentTime = this.video.currentTime;
        const buffered = this.video.buffered;
        
        // Remove buffer muito antigo (mais de 3s atrás)
        for (let i = 0; i < buffered.length; i++) {
            const end = buffered.end(i);
            if (end < currentTime - 3) {
                // Buffer antigo será removido automaticamente pelo HLS.js
                continue;
            }
        }
        
        // Força posição no final do buffer se drift > 5s
        if (buffered.length > 0) {
            const bufferEnd = buffered.end(buffered.length - 1);
            const drift = bufferEnd - currentTime;
            
            if (drift > 5) {
                this.video.currentTime = bufferEnd - 1;
            }
        }
    }
    
    setupAggressiveCleanup() {
        // Limpeza a cada 10 segundos
        this.cleanupInterval = setInterval(() => {
            if (this.isDestroyed) {
                clearInterval(this.cleanupInterval);
                return;
            }
            
            this.aggressiveCleanup();
            
            // Força garbage collection
            if (window.gc) {
                window.gc();
            }
        }, 10000);
    }
    
    restart() {
        if (this.hls) {
            this.hls.destroy();
        }
        
        setTimeout(() => {
            if (!this.isDestroyed) {
                this.setupPlayer();
            }
        }, 500); // Restart mais rápido
    }
    
    destroy() {
        this.isDestroyed = true;
        
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
        }
        
        if (this.hls) {
            this.hls.destroy();
            this.hls = null;
        }
        
        if (this.video) {
            this.video.src = '';
            this.video.load();
        }
    }
    
    // Métodos de controle mínimos
    play() { return this.video?.play(); }
    pause() { this.video?.pause(); }
    setVolume(volume) { if (this.video) this.video.volume = Math.max(0, Math.min(1, volume)); }
}

// Gerenciador para 12 câmeras
class TwelveCamManager {
    constructor() {
        this.players = new Map();
        this.maxPlayers = 12;
        this.activeViewers = 0;
    }
    
    addPlayer(containerId, streamUrl, options = {}) {
        if (this.players.size >= this.maxPlayers) {
            console.warn('⚠️ Limite de 12 câmeras atingido');
            return null;
        }
        
        const container = document.getElementById(containerId);
        if (!container) return null;
        
        const video = container.querySelector('video') || this.createVideoElement(container);
        const player = new UltraOptimizedHLSPlayer(video, streamUrl, options);
        
        this.players.set(containerId, player);
        return player;
    }
    
    createVideoElement(container) {
        const video = document.createElement('video');
        video.controls = false;
        video.muted = true;
        video.playsInline = true;
        video.preload = 'none'; // Não pré-carrega
        video.style.width = '100%';
        video.style.height = '100%';
        video.style.objectFit = 'cover';
        
        container.appendChild(video);
        return video;
    }
    
    removePlayer(containerId) {
        const player = this.players.get(containerId);
        if (player) {
            player.destroy();
            this.players.delete(containerId);
        }
    }
    
    // Pausa players não visíveis para economizar recursos
    optimizeForViewport() {
        for (const [containerId, player] of this.players) {
            const container = document.getElementById(containerId);
            if (container && this.isInViewport(container)) {
                player.play();
            } else {
                player.pause();
            }
        }
    }
    
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= window.innerHeight &&
            rect.right <= window.innerWidth
        );
    }
    
    getStats() {
        return {
            totalPlayers: this.players.size,
            maxPlayers: this.maxPlayers,
            memoryUsage: performance.memory ? performance.memory.usedJSHeapSize : 'N/A'
        };
    }
}

// Exporta para uso global
window.UltraOptimizedHLSPlayer = UltraOptimizedHLSPlayer;
window.TwelveCamManager = TwelveCamManager;

export { UltraOptimizedHLSPlayer, TwelveCamManager };