/**
 * Service Worker - Sistema Clínica PWA
 * Versão Modernizada - Fase 1
 */

const CACHE_NAME = 'clinica-v1.0.0';
const STATIC_CACHE = 'clinica-static-v1.0.0';
const DYNAMIC_CACHE = 'clinica-dynamic-v1.0.0';

// Arquivos para cache estático
const STATIC_FILES = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/js/dashboard.js',
    '/static/js/appointments.js',
    '/static/js/patients.js',
    '/static/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png'
];

// Estratégias de cache
const CACHE_STRATEGIES = {
    STATIC_FIRST: 'static-first',
    NETWORK_FIRST: 'network-first',
    CACHE_ONLY: 'cache-only'
};

// Instalação do Service Worker
self.addEventListener('install', (event) => {
    console.log('🚀 Service Worker instalando...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('📦 Cache estático aberto');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('✅ Cache estático preenchido');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('❌ Erro ao instalar cache:', error);
            })
    );
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
    console.log('🔄 Service Worker ativando...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('🗑️ Removendo cache antigo:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker ativado');
                return self.clients.claim();
            })
    );
});

// Interceptação de requisições
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Estratégia para arquivos estáticos
    if (isStaticFile(request)) {
        event.respondWith(cacheFirst(request));
        return;
    }
    
    // Estratégia para API calls
    if (isApiCall(request)) {
        event.respondWith(networkFirst(request));
        return;
    }
    
    // Estratégia para páginas HTML
    if (isHtmlPage(request)) {
        event.respondWith(networkFirst(request));
        return;
    }
    
    // Estratégia padrão
    event.respondWith(networkFirst(request));
});

// Estratégia: Cache First (para arquivos estáticos)
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('Erro na estratégia cache-first:', error);
        return new Response('Erro de conexão', { status: 503 });
    }
}

// Estratégia: Network First (para conteúdo dinâmico)
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('Rede indisponível, usando cache:', error);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Fallback para páginas HTML
        if (isHtmlPage(request)) {
            return caches.match('/');
        }
        
        return new Response('Conteúdo não disponível offline', { status: 503 });
    }
}

// Verificações de tipo de arquivo
function isStaticFile(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/static/') && 
           (url.pathname.endsWith('.css') || 
            url.pathname.endsWith('.js') || 
            url.pathname.endsWith('.png') || 
            url.pathname.endsWith('.jpg') || 
            url.pathname.endsWith('.ico'));
}

function isApiCall(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/api/') || 
           url.pathname.includes('ajax') ||
           request.method === 'POST';
}

function isHtmlPage(request) {
    const url = new URL(request.url);
    return request.method === 'GET' && 
           !url.pathname.startsWith('/static/') &&
           !url.pathname.startsWith('/api/') &&
           !url.pathname.includes('.');
}

// Sincronização em background
self.addEventListener('sync', (event) => {
    console.log('🔄 Sincronização em background:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

// Sincronização de dados offline
async function doBackgroundSync() {
    try {
        // Aqui você pode implementar sincronização de dados offline
        console.log('🔄 Sincronizando dados em background...');
        
        // Exemplo: sincronizar agendamentos offline
        const offlineData = await getOfflineData();
        if (offlineData.length > 0) {
            await syncOfflineData(offlineData);
        }
        
        console.log('✅ Sincronização concluída');
    } catch (error) {
        console.error('❌ Erro na sincronização:', error);
    }
}

// Função para obter dados offline (implementar conforme necessário)
async function getOfflineData() {
    // Implementar lógica para obter dados salvos offline
    return [];
}

// Função para sincronizar dados offline (implementar conforme necessário)
async function syncOfflineData(data) {
    // Implementar lógica para enviar dados para o servidor
    console.log('📤 Sincronizando dados:', data);
}

// Notificações push
self.addEventListener('push', (event) => {
    console.log('📱 Notificação push recebida');
    
    const options = {
        body: event.data ? event.data.text() : 'Nova notificação do Sistema Clínica',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Ver detalhes',
                icon: '/static/icons/icon-72x72.png'
            },
            {
                action: 'close',
                title: 'Fechar',
                icon: '/static/icons/icon-72x72.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Sistema Clínica', options)
    );
});

// Clique em notificação
self.addEventListener('notificationclick', (event) => {
    console.log('👆 Notificação clicada:', event.notification.tag);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/dashboard')
        );
    } else if (event.action === 'close') {
        // Apenas fecha a notificação
        return;
    } else {
        // Ação padrão: abrir dashboard
        event.waitUntil(
            clients.openWindow('/dashboard')
        );
    }
});

// Mensagens do cliente
self.addEventListener('message', (event) => {
    console.log('💬 Mensagem recebida:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: '1.0.0' });
    }
});

console.log('🚀 Service Worker carregado - Sistema Clínica v1.0.0');
