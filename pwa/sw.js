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
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  
  if (url.pathname.startsWith('/api/') || url.pathname === '/health') {
    // Network-first for API calls
    e.respondWith(
      fetch(e.request).catch(() => {
        return caches.match(e.request);
      })
    );
  } else {
    // Cache-first for static assets
    e.respondWith(
      caches.match(e.request).then(response => {
        return response || fetch(e.request);
      })
    );
  }
});
