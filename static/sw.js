const CACHE_NAME = 'clinica-v1.0.0';
const STATIC_CACHE = 'static-v1.0.0';
const DYNAMIC_CACHE = 'dynamic-v1.0.0';

// Arquivos para cache estático
const STATIC_FILES = [
  '/',
  '/static/css/main.css',
  '/static/css/components.css',
  '/static/js/main.js',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js',
  'https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css',
  'https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.js'
];

// Estratégia de cache: Network First para APIs, Cache First para recursos estáticos
const CACHE_STRATEGIES = {
  STATIC: 'cache-first',
  API: 'network-first',
  DYNAMIC: 'stale-while-revalidate'
};

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker instalando...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Cache estático aberto');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Arquivos estáticos em cache');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Erro ao instalar cache:', error);
      })
  );
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker ativando...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Removendo cache antigo:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker ativado');
        return self.clients.claim();
      })
  );
});

// Interceptação de requisições
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Pular requisições não-GET
  if (request.method !== 'GET') {
    return;
  }
  
  // Estratégia para APIs
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // Estratégia para recursos estáticos
  if (isStaticResource(request)) {
    event.respondWith(handleStaticRequest(request));
    return;
  }
  
  // Estratégia para páginas HTML
  if (request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(handleHtmlRequest(request));
    return;
  }
  
  // Estratégia padrão
  event.respondWith(handleDefaultRequest(request));
});

// Estratégia para APIs (Network First)
async function handleApiRequest(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache da resposta da API
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('API offline, tentando cache:', error);
    
    // Fallback para cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Resposta offline padrão para APIs
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'Sem conexão com internet. Dados podem estar desatualizados.' 
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Estratégia para recursos estáticos (Cache First)
async function handleStaticRequest(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Recurso estático offline:', error);
    
    // Retornar página offline para recursos críticos
    if (request.url.includes('bootstrap') || request.url.includes('main.css')) {
      return new Response('/* Offline - Recurso não disponível */', {
        headers: { 'Content-Type': 'text/css' }
      });
    }
    
    throw error;
  }
}

// Estratégia para páginas HTML (Stale While Revalidate)
async function handleHtmlRequest(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  // Tentar buscar da rede em background
  const networkPromise = fetch(request).then((response) => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => null);
  
  // Retornar cache se disponível, senão aguardar rede
  if (cachedResponse) {
    return cachedResponse;
  }
  
  const networkResponse = await networkPromise;
  if (networkResponse) {
    return networkResponse;
  }
  
  // Fallback para página offline
  return getOfflinePage();
}

// Estratégia padrão
async function handleDefaultRequest(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

// Verificar se é recurso estático
function isStaticResource(request) {
  const url = request.url;
  return (
    url.includes('.css') ||
    url.includes('.js') ||
    url.includes('.png') ||
    url.includes('.jpg') ||
    url.includes('.jpeg') ||
    url.includes('.gif') ||
    url.includes('.svg') ||
    url.includes('.woff') ||
    url.includes('.woff2') ||
    url.includes('.ttf') ||
    url.includes('.eot')
  );
}

// Página offline
async function getOfflinePage() {
  const offlineHtml = `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Sistema Clínica - Offline</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          margin: 0;
          padding: 0;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }
        .offline-container {
          text-align: center;
          padding: 2rem;
          background: rgba(255,255,255,0.1);
          border-radius: 1rem;
          backdrop-filter: blur(10px);
          box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .offline-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }
        h1 {
          margin: 0 0 1rem 0;
          font-size: 2rem;
        }
        p {
          margin: 0 0 1.5rem 0;
          opacity: 0.9;
        }
        .retry-btn {
          background: rgba(255,255,255,0.2);
          border: 2px solid rgba(255,255,255,0.3);
          color: white;
          padding: 0.75rem 1.5rem;
          border-radius: 0.5rem;
          cursor: pointer;
          font-size: 1rem;
          transition: all 0.3s ease;
        }
        .retry-btn:hover {
          background: rgba(255,255,255,0.3);
          border-color: rgba(255,255,255,0.5);
        }
      </style>
    </head>
    <body>
      <div class="offline-container">
        <div class="offline-icon">📱</div>
        <h1>Sistema Clínica</h1>
        <p>Você está offline no momento.</p>
        <p>Algumas funcionalidades podem não estar disponíveis.</p>
        <button class="retry-btn" onclick="window.location.reload()">
          Tentar Novamente
        </button>
      </div>
    </body>
    </html>
  `;
  
  return new Response(offlineHtml, {
    headers: { 'Content-Type': 'text/html' }
  });
}

// Sincronização em background
self.addEventListener('sync', (event) => {
  console.log('Sincronização em background:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// Sincronização de dados
async function doBackgroundSync() {
  try {
    // Aqui você implementaria a sincronização de dados offline
    console.log('Sincronizando dados em background...');
    
    // Exemplo: sincronizar agendamentos pendentes
    const pendingData = await getPendingData();
    if (pendingData.length > 0) {
      await syncPendingData(pendingData);
    }
    
    console.log('Sincronização concluída');
  } catch (error) {
    console.error('Erro na sincronização:', error);
  }
}

// Obter dados pendentes (exemplo)
async function getPendingData() {
  // Implementar lógica para obter dados pendentes do IndexedDB
  return [];
}

// Sincronizar dados pendentes (exemplo)
async function syncPendingData(data) {
  // Implementar lógica para sincronizar com o servidor
  console.log('Sincronizando dados:', data);
}

// Push notifications
self.addEventListener('push', (event) => {
  console.log('Push notification recebida:', event);
  
  if (event.data) {
    const data = event.data.json();
    
    const options = {
      body: data.body || 'Nova notificação do Sistema Clínica',
      icon: '/static/icons/icon-192x192.png',
      badge: '/static/icons/icon-72x72.png',
      vibrate: [200, 100, 200],
      data: data.data || {},
      actions: data.actions || [
        {
          action: 'view',
          title: 'Ver',
          icon: '/static/icons/eye.png'
        },
        {
          action: 'close',
          title: 'Fechar',
          icon: '/static/icons/close.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'Sistema Clínica', options)
    );
  }
});

// Clique em notificação
self.addEventListener('notificationclick', (event) => {
  console.log('Notificação clicada:', event);
  
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    );
  }
});

// Mensagens do cliente
self.addEventListener('message', (event) => {
  console.log('Mensagem recebida:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

console.log('Service Worker carregado:', CACHE_NAME);
