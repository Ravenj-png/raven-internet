const CACHE_NAME = 'raven-pwa-v2';
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/howto.html',
  '/privacy.html',
  '/terms.html',
  '/rules.html'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(ASSETS))
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith('/api') || url.pathname === '/health') {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
  } else {
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request))
    );
  }
});
