/**
 * IndexNow: tell Bing, Yandex, Naver, Seznam and Yep which URLs changed (Google doesn't use it).
 * The key is public by design: static/<key>.txt must be live before you ping.
 *
 * usage: npm run indexnow                 every URL in the live sitemap (after a relaunch)
 *        npm run indexnow -- <url> …      only these URLs (after editing a few pages)
 *        DRY_RUN=1 npm run indexnow       print what would be sent
 */
import { readdirSync } from 'node:fs';

const HOST = 'www.koipun.com';
const keyFile = readdirSync(new URL('../static/', import.meta.url)).find((f) => /^[0-9a-f]{32}\.txt$/.test(f));
if (!keyFile) throw new Error('No IndexNow key file (static/<32 hex>.txt)');
const key = keyFile.slice(0, -4);
const keyLocation = `https://${HOST}/${keyFile}`;

// The key must be served before engines will accept the ping
const live = await fetch(keyLocation);
if (!live.ok || (await live.text()).trim() !== key) throw new Error(`Key not live at ${keyLocation}: deploy first`);

let urlList = process.argv.slice(2);
if (!urlList.length) {
  const xml = await (await fetch(`https://${HOST}/sitemap.xml`)).text();
  urlList = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
}
urlList = urlList.filter((u) => new URL(u).host === HOST);
if (!urlList.length) throw new Error('No URLs to submit');

const body = { host: HOST, key, keyLocation, urlList };
if (process.env.DRY_RUN) { console.log(JSON.stringify(body, null, 2)); process.exit(0); }

const res = await fetch('https://api.indexnow.org/indexnow', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json; charset=utf-8' },
  body: JSON.stringify(body),
});
// 200 OK, 202 Accepted (key validation pending) are success; 4xx explain themselves
console.log(`IndexNow: ${res.status} ${res.statusText} for ${urlList.length} URLs`);
if (res.status >= 300) { console.error(await res.text()); process.exit(1); }
