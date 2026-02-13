/**
 * ==========================================
 * SERVICE WORKER - THEGRANITO PORTFOLIO PWA
 * Version: 2.0
 * Author: Uttam Kumar
 * ==========================================
 */

const CACHE_NAME = 'thegranito-v2.0';
const RUNTIME_CACHE = 'thegranito-runtime-v2.0';

// Files to cache on install
const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/images/logo.png',
  '/static/images/profile.jpg',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png',
  '/offline.html',
  // Add more static assets here
];

// External resources to cache
const EXTERNAL_RESOURCES = [
  'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
  'https://unpkg.com/aos@2.3.1/dist/aos.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
  'https://unpkg.com/aos@2.3.1/dist/aos.js'
];

// Routes to cache dynamically
const DYNAMIC_ROUTES = [
  '/about',
  '/projects',
  '/contact',
  '/blog'
];

// ==================== INSTALL EVENT ====================
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        
        // Cache static assets
        cache.addAll(STATIC_ASSETS);
        
        // Cache external resources (don't fail if these fail)
        EXTERNAL_RESOURCES.forEach(url => {
          cache.add(url).catch(err => {
            console.warn(`[Service Worker] Failed to cache: ${url}`, err);
          });
        });
        
        // Cache dynamic routes
        DYNAMIC_ROUTES.forEach(route => {
          cache.add(route).catch(err => {
            console.warn(`[Service Worker] Failed to cache route: ${route}`, err);
          });
        });
      })
      .then(() => {
        console.log('[Service Worker] Installation complete');
        return self.skipWaiting(); // Activate immediately
      })
  );
});

// ==================== ACTIVATE EVENT ====================
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              // Delete old caches
              return cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE;
            })
            .map((cacheName) => {
              console.log(`[Service Worker] Deleting old cache: ${cacheName}`);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        console.log('[Service Worker] Activation complete');
        return self.clients.claim(); // Take control immediately
      })
  );
});

// ==================== FETCH EVENT ====================
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip cross-origin requests
  if (url.origin !== location.origin && !EXTERNAL_RESOURCES.includes(request.url)) {
    return;
  }
  
  // Handle different types of requests
  if (request.method !== 'GET') {
    // Don't cache non-GET requests
    return;
  }
  
  // API requests - Network first, then cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // HTML pages - Cache first, then network
  if (request.headers.get('Accept')?.includes('text/html')) {
    event.respondWith(cacheFirst(request));
    return;
  }
  
  // Static assets - Cache first
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(cacheFirst(request));
    return;
  }
  
  // Default: Stale while revalidate
  event.respondWith(staleWhileRevalidate(request));
});

// ==================== CACHING STRATEGIES ====================

/**
 * Cache First Strategy
 * Try cache first, fallback to network, then offline page
 */
async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      console.log(`[Service Worker] Cache hit: ${request.url}`);
      return cachedResponse;
    }
    
    console.log(`[Service Worker] Cache miss, fetching: ${request.url}`);
    const networkResponse = await fetch(request);
    
    // Cache the new response
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error(`[Service Worker] Fetch failed: ${request.url}`, error);
    
    // Return offline page for HTML requests
    if (request.headers.get('Accept')?.includes('text/html')) {
      const offlineResponse = await caches.match('/offline.html');
      return offlineResponse || new Response('Offline - Please check your connection', {
        status: 503,
        statusText: 'Service Unavailable'
      });
    }
    
    return new Response('Network error', {
      status: 408,
      statusText: 'Request Timeout'
    });
  }
}

/**
 * Network First Strategy
 * Try network first, fallback to cache
 */
async function networkFirst(request) {
  try {
    console.log(`[Service Worker] Network first: ${request.url}`);
    const networkResponse = await fetch(request);
    
    // Cache the new response
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error(`[Service Worker] Network failed, trying cache: ${request.url}`, error);
    
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response(JSON.stringify({ error: 'Offline' }), {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Stale While Revalidate Strategy
 * Return cache immediately, update cache in background
 */
async function staleWhileRevalidate(request) {
  const cachedResponse = await caches.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    // Update cache in background
    if (networkResponse.ok) {
      caches.open(RUNTIME_CACHE).then((cache) => {
        cache.put(request, networkResponse.clone());
      });
    }
    return networkResponse;
  }).catch((error) => {
    console.error(`[Service Worker] Background fetch failed: ${request.url}`, error);
  });
  
  // Return cached response immediately, or wait for network
  return cachedResponse || fetchPromise;
}

// ==================== BACKGROUND SYNC ====================
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync:', event.tag);
  
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  }
});

async function syncMessages() {
  // Implement your background sync logic here
  console.log('[Service Worker] Syncing messages...');
  // Example: Send pending messages when online
}

// ==================== PUSH NOTIFICATIONS ====================
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push received:', event);
  
  const options = {
    body: event.data?.text() || 'New notification from TheGranito',
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/icon-192x192.png',
    vibrate: [200, 100, 200],
    tag: 'thegranito-notification',
    requireInteraction: false,
    actions: [
      { action: 'explore', title: 'View', icon: '/static/images/icon-192x192.png' },
      { action: 'close', title: 'Close', icon: '/static/images/icon-192x192.png' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('TheGranito Portfolio', options)
  );
});

// ==================== NOTIFICATION CLICK ====================
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification click:', event.action);
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// ==================== MESSAGE HANDLER ====================
self.addEventListener('message', (event) => {
  console.log('[Service Worker] Message received:', event.data);
  
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
  
  if (event.data.action === 'clearCache') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      })
    );
  }
});

// ==================== PERIODIC BACKGROUND SYNC ====================
self.addEventListener('periodicsync', (event) => {
  console.log('[Service Worker] Periodic sync:', event.tag);
  
  if (event.tag === 'update-content') {
    event.waitUntil(updateContent());
  }
});

async function updateContent() {
  console.log('[Service Worker] Updating content...');
  // Implement periodic content update logic
}

// ==================== ERROR HANDLER ====================
self.addEventListener('error', (event) => {
  console.error('[Service Worker] Error:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
  console.error('[Service Worker] Unhandled promise rejection:', event.reason);
});

console.log('[Service Worker] Loaded successfully');
