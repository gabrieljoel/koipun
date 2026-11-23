/**
 * Sorts Tailwind classes in Hugo templates into Tailwind's canonical order (the same order
 * prettier-plugin-tailwindcss uses, which can't parse Go templates). Uses the project's real
 * design system (assets/css/main.css), so custom utilities like `card` sort correctly too.
 *
 *   node scripts/tailwind/sort-classes.mjs           # rewrite templates
 *   node scripts/tailwind/sort-classes.mjs --check   # exit 1 if anything is unsorted (CI / npm run check)
 *
 * Sorted: class="…" attributes, ("class" "…") partial params, `$link := "…"` / `$label := "…"`
 * variables, and the variant maps in components/button.html. Strings containing template actions
 * ({{ … }}) are skipped. Unknown tokens (e.g. `group`) keep their place at the front, like Prettier.
 */
import { __unstable__loadDesignSystem } from '@tailwindcss/node';
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const root = new URL('../../', import.meta.url).pathname;
const check = process.argv.includes('--check');
const ds = await __unstable__loadDesignSystem(readFileSync(join(root, 'assets/css/main.css'), 'utf8'), { base: root });

const sortList = (list) => {
  const tokens = list.trim().split(/\s+/);
  const order = ds.getClassOrder(tokens);
  return order
    .map(([cls, rank], i) => ({ cls, rank, i }))
    .sort((a, b) => (a.rank === null) !== (b.rank === null) ? (a.rank === null ? -1 : 1)
      : a.rank === null ? a.i - b.i : a.rank < b.rank ? -1 : a.rank > b.rank ? 1 : a.i - b.i)
    .map((t) => t.cls)
    .join(' ');
};

const patterns = [
  /(\bclass=")([^"{}]+)(")/g,
  /("class" ")([^"{}]+)(")/g,
  /(\$(?:link|label|h2) := ")([^"{}]+)(")/g,
  /(\n\s*"(?:primary|secondary|link|md|lg)" ")([^"{}]+)(")/g,
];

const walk = (dir) => readdirSync(dir).flatMap((f) => {
  const p = join(dir, f);
  return statSync(p).isDirectory() ? walk(p) : p.endsWith('.html') ? [p] : [];
});

let changed = 0;
for (const file of walk(join(root, 'layouts'))) {
  const src = readFileSync(file, 'utf8');
  let out = src;
  for (const re of patterns) out = out.replace(re, (_, a, list, z) => a + sortList(list) + z);
  if (out !== src) {
    changed++;
    console.log(`${check ? 'unsorted' : 'sorted  '} ${relative(root, file)}`);
    if (!check) writeFileSync(file, out);
  }
}
console.log(changed ? `${changed} file(s) ${check ? 'need sorting: run npm run format:classes' : 'sorted'}` : 'Tailwind classes are in canonical order');
process.exit(check && changed ? 1 : 0);
