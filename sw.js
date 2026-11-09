/* Mishaling helper: when online, always loads the newest version from the web;
   when offline, uses the saved copy. Also keeps fonts, icons and the voices for offline use. */
const CACHE = "misha-app-v44";
const VCACHE = "mishaling-voices-v1";   /* the voice clips: kept across app updates */
const CORE = ["./", "./index.html", "./manifest.json", "./mishaling-192.png", "./mishaling-512.png", "./mishaling-maskable-512.png", "./mishaling-apple-touch.png"];
self.addEventListener("install", e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).catch(() => {}));
});
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== VCACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())
));
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const u = new URL(req.url);
  const mine = u.origin === location.origin;
  const fonts = /fonts\.(googleapis|gstatic)\.com$/.test(u.host);
  if (!mine && !fonts) return;
  if (mine && /\/audio\/[a-z]+\/[0-9a-f]+\.mp3$/.test(u.pathname)){
    /* Voice clips never change (a new recording gets a new name): saved copy first, otherwise fetch and keep */
    e.respondWith(caches.match(req, {ignoreSearch: true}).then(hit => hit || fetch(req).then(res => {
      if (res && res.ok && res.status === 200){ const copy = res.clone(); caches.open(VCACHE).then(c => c.put(req.url.split("?")[0], copy)); }
      return res;
    })));
    return;
  }
  if (mine && /\/audio\/[a-z]+\/index\.json$/.test(u.pathname)){
    /* The list of voice clips: newest when online, saved copy offline */
    e.respondWith(fetch(req, {cache: "no-store"}).then(res => {
      if (res && res.ok){ const copy = res.clone(); caches.open(VCACHE).then(c => c.put(req.url.split("?")[0], copy)); }
      return res;
    }).catch(() => caches.match(req, {ignoreSearch: true})));
    return;
  }
  if (req.mode === "navigate" || (mine && /\/(index\.html)?$/.test(u.pathname))){
    /* Network first for the app page, so updates show straight away */
    e.respondWith(fetch(req, {cache: "no-store"}).then(res => {
      if (res && res.ok){ const copy = res.clone(); caches.open(CACHE).then(c => c.put("./index.html", copy)); }
      return res;
    }).catch(() => caches.match("./index.html", {ignoreSearch: true}).then(r => r || caches.match("./"))));
    return;
  }
  /* Everything else: saved copy first, refresh in the background */
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(req, {ignoreSearch: true});
    const net = fetch(req).then(res => { if (res && (res.ok || res.type === "opaque")) c.put(req, res.clone()); return res; }).catch(() => hit);
    return hit || net;
  }));
});
