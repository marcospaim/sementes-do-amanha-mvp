const CACHE = "sementes-v1";
const ASSETS = [
  "/static/css/app.css",
  "/static/manifest.webmanifest",
  "/offline/",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((chaves) =>
      Promise.all(chaves.filter((c) => c !== CACHE).map((c) => caches.delete(c)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const requisicao = event.request;
  if (requisicao.method !== "GET") return;

  if (requisicao.mode === "navigate") {
    event.respondWith(
      fetch(requisicao).catch(() => caches.match("/offline/"))
    );
    return;
  }

  if (new URL(requisicao.url).pathname.startsWith("/static/")) {
    event.respondWith(
      caches.match(requisicao).then((cacheado) => cacheado || fetch(requisicao))
    );
  }
});
