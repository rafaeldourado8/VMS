const CACHE_NAME = 'vms-video-cache-v1';
const MAX_CACHE_SIZE = 100 * 1024 * 1024; // 100MB

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Apenas cachear vídeos MP4 do storage service
  if (!url.pathname.includes('/download/') || !url.pathname.endsWith('.mp4')) {
    return;
  }

  event.respondWith(
    caches.open(CACHE_NAME).then(async (cache) => {
      const cachedResponse = await cache.match(event.request);
      
      if (cachedResponse) {
        console.log('[SW] Cache hit:', url.pathname);
        return cachedResponse;
      }

      console.log('[SW] Fetching:', url.pathname);
      const response = await fetch(event.request);
      
      if (response.ok && response.status === 200) {
        const clonedResponse = response.clone();
        
        // Verificar tamanho do cache antes de adicionar
        const keys = await cache.keys();
        let totalSize = 0;
        
        for (const key of keys) {
          const res = await cache.match(key);
          if (res) {
            const blob = await res.blob();
            totalSize += blob.size;
          }
        }
        
        // Se cache está cheio, remover itens mais antigos
        if (totalSize > MAX_CACHE_SIZE) {
          console.log('[SW] Cache cheio, limpando...');
          await cache.delete(keys[0]);
        }
        
        cache.put(event.request, clonedResponse);
      }
      
      return response;
    })
  );
});
