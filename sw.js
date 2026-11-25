// Service Worker: macht Techno Events installierbar und offline nutzbar.
// Daten (JSON) immer zuerst frisch aus dem Netz, sonst aus dem Speicher.
// Seite (HTML) ebenfalls frisch aus dem Netz; Icons aus dem Speicher.
const CACHE = "techno-events-v1.39.4";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;

  // Seite selbst (HTML) und Daten (JSON): Netz zuerst, damit Updates sofort ankommen
  if (url.pathname.endsWith(".json") || e.request.mode === "navigate" || url.pathname.endsWith(".html") || url.pathname.endsWith("/")) {
    // Netz zuerst: immer die neuesten Events/Tickets
    e.respondWith(
      fetch(e.request).then((r) => {
        const kopie = r.clone();
        caches.open(CACHE).then((c) => c.put(e.request, kopie));
        return r;
      }).catch(() => caches.match(e.request))
    );
    return;
  }

  // App-Dateien: sofort aus dem Speicher, im Hintergrund neu laden
  e.respondWith(
    caches.match(e.request).then((cached) => {
      const netz = fetch(e.request).then((r) => {
        const kopie = r.clone();
        caches.open(CACHE).then((c) => c.put(e.request, kopie));
        return r;
      }).catch(() => cached);
      return cached || netz;
    })
  );
});
