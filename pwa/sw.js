// Minimal service worker for PWA installation
self.addEventListener('install', (e) => {
  e.waitUntil(self.skipWaiting());
});
self.addEventListener('activate', (e) => {
  e.waitUntil(self.clients.claim());
});
self.addEventListener('fetch', (e) => {
  // Network-first for API, cache-first for static
  const url = new URL(e.request.url);
  if (url.pathname.startsWith('/api/') || url.pathname === '/health') {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
  } else {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
  }
});
