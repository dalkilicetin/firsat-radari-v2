const CACHE = "firsat-radari-v5.15";
const SHELL = [
  "./",
  "./index.html",
  "./app.js",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable-512.png",
  "./apple-touch-icon.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);

  // Gece taramasi sonucu: her zaman agdan
  if (url.pathname.includes("/data/sonuclar.json")) {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
    return;
  }
  // Finnhub API: her zaman ağdan (canlı veri asla cache'lenmez)
  if (url.hostname.includes("finnhub.io")) {
    e.respondWith(fetch(e.request));
    return;
  }

  // Uygulama kabuğu: ONCE AG, yoksa cache (yeni surum aninda gorunur; cevrimdisi de acilir)
  e.respondWith(
    fetch(e.request).then((res) => {
      if (e.request.method === "GET" && res.ok && url.origin === self.location.origin) {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy));
      }
      return res;
    }).catch(() => caches.match(e.request).then((hit) => hit || caches.match("./index.html")))
  );
});
