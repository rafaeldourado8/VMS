/**
 * Player HLS Otimizado para VMS
 * Reduz consumo de memória e melhora estabilidade
 */

class OptimizedHLSPlayer {
    constructor(videoElement, streamUrl, options = {}) {
        this.video = videoElement;
        this.streamUrl = streamUrl;
        this.hls = null;
        this.isDestroyed = false;
        
        // Configurações otimizadas
        this.config = {
            // VOD Configuration
            maxBufferLength: 30,
            maxMaxBufferLength: 60,
            backBufferLength: 10,
            maxBufferHole: 2,
            
            // Disable live features
            lowLatencyMode: false,
            liveSyncDuration: undefined,
            liveMaxLatencyDuration: undefined,
            liveDurationInfinity: false,
            
            // Network
            manifestLoadingTimeOut: 10000,
            manifestLoadingMaxRetry: 1,
            levelLoadingTimeOut: 10000,
            levelLoadingMaxRetry: 1,
            fragLoadingTimeOut: 20000,
            fragLoadingMaxRetry: 1,
            
            // Performance
            enableWorker: true,
            startLevel: -1,
            autoStartLoad: true,
            
            ...options
        };
        
        this.setupPlayer();
        this.setupCleanupInterval();
    }
    
    setupPlayer() {
        if (!window.Hls?.isSupported()) {
            console.error('HLS não suportado neste navegador');
            return;
        }
        
        this.hls = new window.Hls(this.config);
        
        // Event listeners otimizados
        this.hls.on(window.Hls.Events.MEDIA_ATTACHED, () => {
            console.log('🎥 Player anexado ao elemento de vídeo');
        });
        
        this.hls.on(window.Hls.Events.MANIFEST_PARSED, () => {
            console.log('📋 Manifest carregado, iniciando reprodução');
            this.video.play().catch(e => console.warn('Autoplay bloqueado:', e));
        });
        
        // Tratamento de erros com recuperação automática
        this.hls.on(window.Hls.Events.ERROR, (event, data) => {
            if (data.fatal) {
                this.handleFatalError(data);
            } else {
                console.warn('⚠️ Erro não-fatal:', data.type, data.details);
            }
        });
        
        // Ignora erros de manifest loading inicial (normal para streams on-demand)
        this.hls.on(window.Hls.Events.MANIFEST_LOADING, () => {
            console.log('📡 Carregando manifest...');
        });
        
        this.hls.on(window.Hls.Events.MANIFEST_LOAD_ERROR, (event, data) => {
            if (data.response?.code === 404) {
                console.log('⏳ Stream ainda não disponível, tentando novamente...');
                // Retry automático após 2s
                setTimeout(() => {
                    if (!this.isDestroyed && this.hls) {
                        this.hls.loadSource(this.streamUrl);
                    }
                }, 2000);
            }
        });
        
        // Monitoramento de buffer
        this.hls.on(window.Hls.Events.BUFFER_APPENDED, () => {
            this.cleanupOldBuffer();
        });
        
        // Drift check desabilitado para VOD
        
        this.hls.attachMedia(this.video);
        this.hls.loadSource(this.streamUrl);
    }
    
    handleFatalError(data) {
        console.error('❌ Erro fatal:', data.type, data.details);
        
        switch (data.type) {
            case window.Hls.ErrorTypes.NETWORK_ERROR:
                console.log('🔄 Tentando recuperar erro de rede...');
                this.hls.startLoad();
                break;
                
            case window.Hls.ErrorTypes.MEDIA_ERROR:
                console.log('🔄 Tentando recuperar erro de mídia...');
                this.hls.recoverMediaError();
                break;
                
            default:
                console.log('🔄 Reiniciando player...');
                this.restart();
                break;
        }
    }
    

    
    cleanupOldBuffer() {
        if (!this.video) return;
        
        const currentTime = this.video.currentTime;
        const buffered = this.video.buffered;
        
        // Remove buffer antigo (mais de 10s atrás)
        for (let i = 0; i < buffered.length; i++) {
            const start = buffered.start(i);
            const end = buffered.end(i);
            
            if (end < currentTime - 10) {
                // Buffer muito antigo, pode ser removido
                // HLS.js faz isso automaticamente com backBufferLength
                continue;
            }
        }
    }
    
    setupCleanupInterval() {
        // Limpeza periódica a cada 30 segundos
        this.cleanupInterval = setInterval(() => {
            if (this.isDestroyed) {
                clearInterval(this.cleanupInterval);
                return;
            }
            
            this.cleanupOldBuffer();
            
            // Força garbage collection se disponível
            if (window.gc) {
                window.gc();
            }
        }, 30000);
    }
    
    restart() {
        console.log('🔄 Reiniciando player HLS...');
        
        if (this.hls) {
            this.hls.destroy();
        }
        
        // Aguarda um pouco antes de recriar
        setTimeout(() => {
            if (!this.isDestroyed) {
                this.setupPlayer();
            }
        }, 1000);
    }
    
    destroy() {
        console.log('🗑️ Destruindo player HLS');
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
    
    // Métodos de controle
    play() {
        return this.video?.play();
    }
    
    pause() {
        this.video?.pause();
    }
    
    setVolume(volume) {
        if (this.video) {
            this.video.volume = Math.max(0, Math.min(1, volume));
        }
    }
    
    getCurrentTime() {
        return this.video?.currentTime || 0;
    }
    
    isPlaying() {
        return this.video && !this.video.paused && !this.video.ended;
    }
}

// Gerenciador de múltiplos players para mosaico
class MosaicPlayerManager {
    constructor() {
        this.players = new Map();
        this.maxPlayers = 4; // Limite do MVP
    }
    
    addPlayer(containerId, streamUrl, options = {}) {
        if (this.players.size >= this.maxPlayers) {
            console.warn('⚠️ Limite de players atingido');
            return null;
        }
        
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Container não encontrado:', containerId);
            return null;
        }
        
        const video = container.querySelector('video') || this.createVideoElement(container);
        const player = new OptimizedHLSPlayer(video, streamUrl, options);
        
        this.players.set(containerId, player);
        return player;
    }
    
    createVideoElement(container) {
        const video = document.createElement('video');
        video.controls = false;
        video.muted = true;
        video.playsInline = true;
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
    
    removeAllPlayers() {
        for (const [containerId, player] of this.players) {
            player.destroy();
        }
        this.players.clear();
    }
    
    getPlayerCount() {
        return this.players.size;
    }
    
    // Pausa todos os players exceto um (para economizar recursos)
    focusPlayer(activeContainerId) {
        for (const [containerId, player] of this.players) {
            if (containerId === activeContainerId) {
                player.play();
            } else {
                player.pause();
            }
        }
    }
    
    // Resume todos os players
    resumeAll() {
        for (const [containerId, player] of this.players) {
            player.play();
        }
    }
}

// Exporta para uso global
window.OptimizedHLSPlayer = OptimizedHLSPlayer;
window.MosaicPlayerManager = MosaicPlayerManager;

export { OptimizedHLSPlayer, MosaicPlayerManager };