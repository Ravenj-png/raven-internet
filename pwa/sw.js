const CACHE_NAME = 'raven-pwa-v2';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './howto.html',
  './privacy.html',
  './terms.html'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  
  // API calls - Network first
  if (url.pathname.startsWith('/api/') || url.pathname === '/health') {
    e.respondWith(
      fetch(e.request).catch(() => {
        return caches.match(e.request);
      })
    );
  } else {
    // Static assets - Cache first
    e.respondWith(
      caches.match(e.request).then(response => {
        return response || fetch(e.request);
      })
    );
  }
});
