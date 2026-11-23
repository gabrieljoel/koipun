/**
 * Every URL the legacy site ever exposed must still resolve on Netlify.
 * Simulates Netlify's static routing against the built site:
 *   1. A file at the path wins (shadowing), unless the rule is forced (`301!`)
 *   2. /dir → /dir/ when /dir/index.html exists
 *   3. Otherwise the first matching rule in public/_redirects. Netlify ignores a trailing slash when
 *      matching; supports :placeholder (one segment) and a trailing * (→ :splat)
 * Rules with a host (https://blog.koipun.com/…) match only that host; host-less rules match on every
 * domain of the site, as on Netlify (domain aliases such as blog.koipun.com serve the same site).
 *
 * usage: node linkcheck.mjs <public> <urls.txt>          exits 1 if any URL fails
 *        VERBOSE=1 node linkcheck.mjs …                  prints every hop
 */
import { readFileSync, existsSync, statSync } from 'node:fs';
import { join } from 'node:path';

const [pub, urlsPath] = process.argv.slice(2);
const isFile = (p) => existsSync(p) && statSync(p).isFile();

const rules = readFileSync(join(pub, '_redirects'), 'utf8').split('\n')
  .map((l) => l.trim()).filter((l) => l && !l.startsWith('#'))
  .map((l) => {
    const [from, to, code = '301'] = l.split(/\s+/);
    const url = /^https?:\/\//.test(from) ? new URL(from.replace('*', 'SPLAT')) : null;
    const path = url ? url.pathname.replace('SPLAT', '*') : from;
    const names = [];
    const rx = path.replace(/\/$/, '').replace(/[.+?^${}()|[\]\\]/g, '\\$&')
      .replace(/:(\w+)/g, (_, n) => { names.push(n); return '([^/]+)'; })
      .replace(/\/\*$/, () => { names.push('splat'); return '(?:/(.*))?'; });
    return { host: url?.host ?? null, re: new RegExp(`^${rx}/?$`), names, to, status: parseInt(code), force: code.endsWith('!') };
  });

const serves = (path) => {
  const p = decodeURIComponent(path);
  if (isFile(join(pub, p))) return 'file';
  if (isFile(join(pub, p, 'index.html'))) return p.endsWith('/') ? 'file' : 'dir';
  return null;
};

function route(url, host = 'www.koipun.com', hops = []) {
  if (hops.length > 5) return { status: 'LOOP', hops };
  const u = new URL(url, `https://${host}`);
  const path = u.pathname;
  const hit = serves(path);
  for (const r of rules) {
    if (r.host && r.host !== u.host) continue;        // host-less rules apply on every domain of the site
    if (hit && !r.force) continue;                    // shadowing: the file wins over unforced rules
    const m = r.re.exec(path);
    if (!m) continue;
    const params = Object.fromEntries(r.names.map((n, i) => [n, m[i + 1] ?? '']));
    const dest = r.to.replace(/:(\w+)/g, (s, n) => params[n] ?? s);
    return route(dest, u.host, [...hops, `${r.status} → ${dest}`]);
  }
  if (hit === 'dir') return route(`${path}/`, u.host, [...hops, `301 → ${path}/`]);
  if (hit) return { status: u.host === 'www.koipun.com' ? 200 : 'OFFSITE', path, hops };
  return { status: 404, path, hops };
}

const urls = [...new Set(readFileSync(urlsPath, 'utf8').split('\n').map((s) => s.trim()).filter(Boolean))];
// The 2015 Tumblr blog lived on its own host
const hosted = [
  ...urls.map((u) => [u, 'www.koipun.com']),
  ['/post/110390648373/using-anki-to-learn-hiragana', 'blog.koipun.com'],
  ['/post/114272662048/genki-annihilation-anki-deck', 'blog.koipun.com'],
  ['/', 'blog.koipun.com'],
];
let bad = 0;
for (const [u, host] of hosted) {
  const r = route(u, host);
  const ok = r.status === 200;
  if (!ok) bad++;
  if (!ok || process.env.VERBOSE) console.log(`${ok ? '✓' : '✗'} ${r.status} ${host === 'www.koipun.com' ? '' : host}${u} ${r.hops.join(' ')}`);
}
console.log(`${hosted.length - bad}/${hosted.length} legacy URLs resolve on Netlify (200 directly or via redirect)`);
process.exit(bad ? 1 : 0);
