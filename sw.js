/* Mishaling helper: the app opens straight from the copy saved on the phone (fast, and works offline).
   The app checks for a newer version in the background and offers an Update button.
   Pictures and voices are kept in their own stores, so app updates don't download them again. */
const CACHE = "misha-app-v61";
const VCACHE = "mishaling-voices-v2";   /* voice clips (v2: original quality) */
const ICACHE = "mishaling-img-v1";      /* pictures */
const CORE = ["./", "./index.html", "./manifest.json", "./mishaling-192.png", "./mishaling-512.png", "./mishaling-maskable-512.png", "./mishaling-apple-touch.png"];
self.addEventListener("install", e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE.map(u => new Request(u, {cache: "no-store"})))).catch(() => {}));
});
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => ![CACHE, VCACHE, ICACHE].includes(k)).map(k => caches.delete(k)))).then(() => self.clients.claim())
));
/* files whose name never changes its content: saved copy first, otherwise fetch and keep */
const keep = (e, store) => e.respondWith(caches.match(e.request, {ignoreSearch: true}).then(hit => hit || fetch(e.request).then(res => {
  if (res && res.status === 200){ const copy = res.clone(); caches.open(store).then(c => c.put(e.request.url.split("?")[0], copy)); }
  return res;
})));
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const u = new URL(req.url);
  const mine = u.origin === location.origin;
  const fonts = /fonts\.(googleapis|gstatic)\.com$/.test(u.host);
  if (!mine && !fonts) return;
  if (mine && /\/voices\/[a-z]+\/[0-9a-f]+\.mp3$/.test(u.pathname)) return keep(e, VCACHE);
  if (mine && /\/img\/[0-9a-f]+\.webp$/.test(u.pathname)) return keep(e, ICACHE);
  if (mine && /\/voices\/[a-z]+\/index\.json$/.test(u.pathname)){
    /* the list of voice clips: newest when online, saved copy offline */
    e.respondWith(fetch(req, {cache: "no-store"}).then(res => {
      if (res && res.ok){ const copy = res.clone(); caches.open(VCACHE).then(c => c.put(req.url.split("?")[0], copy)); }
      return res;
    }).catch(() => caches.match(req, {ignoreSearch: true})));
    return;
  }
  if (req.mode === "navigate" || (mine && /\/(index\.html)?$/.test(u.pathname))){
    if (u.searchParams.has("fresh")){
      /* the app's background check for a new version: fetch it and keep it for the next start */
      e.respondWith(fetch(req, {cache: "no-store"}).then(res => {
        if (res && res.ok){ const copy = res.clone(); caches.open(CACHE).then(c => c.put("./index.html", copy)); }
        return res;
      }).catch(() => caches.match("./index.html")));
      return;
    }
    /* open instantly from the saved copy; only the very first time comes from the internet */
    e.respondWith(caches.open(CACHE).then(async c => {
      const hit = await c.match("./index.html");
      if (hit) return hit;
      return fetch(req, {cache: "no-store"}).then(res => { if (res && res.ok) c.put("./index.html", res.clone()); return res; })
        .catch(() => caches.match("./"));
    }));
    return;
  }
  /* everything else (fonts, icons): saved copy first, refresh in the background */
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(req, {ignoreSearch: true});
    const net = fetch(req).then(res => { if (res && (res.ok || res.type === "opaque")) c.put(req, res.clone()); return res; }).catch(() => hit);
    return hit || net;
  }));
});
