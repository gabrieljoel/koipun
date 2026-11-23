# Koipun

Rebuild of [koipun.com](https://www.koipun.com): Hugo + Tailwind CSS v4, deployed on Netlify.

## Stack

| | Version | Notes |
|---|---|---|
| Hugo | 0.170.1 (min 0.165) | Standard edition is enough; AVIF/WebP encoding is built in |
| Tailwind CSS | 4.3.5 | CSS-first config (`@theme` in `assets/css/main.css`), compiled by Hugo's `css.TailwindCSS` |
| @tailwindcss/typography | 0.5.20 | Long-form post styling |
| Node | ≥ 22 | Only needed for the Tailwind CLI |

No JavaScript ships to the browser.

## Develop

```sh
npm install
npm run dev       # http://localhost:1313, drafts included
npm run build     # production build → public/
npm run preview   # serve the production build locally
npm run check     # exactly what Netlify runs: class order, clean build, legacy URLs, SEO audit
```

## Layout

```
content/                 Markdown. Posts are page bundles: content/blog/<slug>/index.md + images
  authors/<slug>/        Author term pages (bio + avatar) → /blog/author/<slug>/
  categories/<slug>/     Category descriptions → /blog/category/<slug>/
layouts/
  baseof.html            HTML shell
  home.html  list.html  page.html  taxonomy.html  listing.html  404.html
  blog/page.html         Blog post
  page.markdown.md       Markdown twin of every page (AEO)
  home.llms.txt          /llms.txt
  rss.xml  robots.txt
  _markup/               Render hooks: image → <picture>, link, heading anchors
  _partials/
    head/                seo.html (meta/OG), schema.html (JSON-LD), css.html, icons.html
    components/          picture, post-card, post-grid, post-meta, page-header, prose,
                         pagination, breadcrumbs, author-box, button, nav-links, icon
    func/                featured-image, paginator (return-value helpers)
assets/css/main.css      The Genkō design system (tokens, utilities, typography)
assets/fonts/            Subset web fonts (web/) + TTFs for social cards; regenerate: scripts/fonts/subset.sh
assets/icons/            Inline SVG icons
assets/images/           Logo, hero photo, Anki pattern (SVG), social-card overlays
_archive/                Scrape of the old site (gitignored) — see _archive/README.md
```

## Writing a post

```yaml
# content/blog/my-post/index.md   (put featured.jpg + other images in the same folder)
---
title: Full headline
seoTitle: Shorter title for <title>/OG   # optional
description: 150–160 char summary — used for meta description, cards, RSS, llms.txt
date: 2026-11-23
authors: [gabriel-j-perez-irizarry]                       # term keys (slugs) —
categories: [how-i-learned-japanese-an-interview-series]   # display names live in content/{authors,categories}/
tags: [anki, kanji]
imageAlt: Describe featured.jpg
ogImage: social.jpg                       # optional: hand-made landscape crop for the social card
ogImageAlt: Describe social.jpg           # when ogImage shows something other than featured.jpg
interviewee: { name: Jane Doe, url: https://…, level: JLPT N2 }   # interviews only
---
![Alt text](photo.jpg "Optional caption")
{.float-right}            # optional: float the figure
```

Furigana: `{{< ruby "漢字" "かんじ" >}}` (whole word) or `{{< ruby "先生" "せん|せい" >}}` (per character). It outputs native `<ruby lang="ja">` with `<rp>` fallbacks. Tested in Chromium, Firefox and WebKit: readings sit above the base text, an annotated word never splits across lines, and copied text contains only the kanji.

Images are resized to 480/768/1080/1536 px (never upscaled) and served as **AVIF → WebP**, with a single JPEG/PNG fallback for very old browsers. Animated GIFs become **animated WebP**, about ⅓ the size. `sizes` matches the rendered width (floats ≈ 460px), every image has intrinsic dimensions (no layout shift), the hero gets `fetchpriority="high"`, and the rest lazy-load. Hashed variants are cached as `immutable`. Measured image weight per page view is 80–95% lower than the old site (e.g. the blog index went from 1.9 MB to 102 KB).

## Design system: Genkō

Named after 原稿用紙, the squared paper Japanese learners write on: grid-paper ground, sumi ink, and the logo's koi red used as a teacher's red pen. Mockups: the "Koipun brand refresh" canvas.

All of it lives in `assets/css/main.css` (Tailwind v4, CSS-first, no preprocessor):

| Layer | What | Use in templates |
|---|---|---|
| Primitives (`@theme`) | `koi-50…950` (600 = logo red), `sumi-50…950` warm neutrals, fonts `sans` (Inter) / `display` (Zen Kaku Gothic New) / `hand` (Caveat) / `ja`. Tailwind's default palette is removed. | Rarely |
| Semantic tokens | `surface` `raised` `tint` `fg` `body` `muted` `subtle` `line` `hairline` `grid` `pen` `pen-mark` `btn*`, shadows `shadow-paper` `shadow-paper-lg` `shadow-press`. Swapped in one place for dark mode ("night study") and `.theme-brand`. | Always: `text-fg`, `border-line`, `bg-raised`… Never `dark:` |
| Utilities (`@utility`) | `paper-grid`, `card`, `chip-hand`, `pen-underline`, `link-pen`, `prose-genko`, `dropcap`, `container-page`, `container-prose` | Compose freely, with variants |
| Components | `layouts/_partials/components/` (button: primary / secondary / link, post-card, category-chip, hero, split-section…) | `partial "components/…"` |

Rules of thumb: red-pen text uses `text-pen` (4.5:1 on every ground) and strokes use `pen-mark`. Handwriting (`font-hand`) is for labels, captions and one note per page, never for paragraphs.

## SEO / AEO built in

- **URL parity** with the legacy site (`/blog/<slug>/`, `/blog/page/N/`, `/blog/category/…`, `/blog/author/…`). Legacy-only URLs get 301s in the generated `_redirects` (from `data/redirects.yaml`), and so do `<page>.html` twins and `page/1/`.
- Canonical URLs (overridable with `canonical:`), robots meta (drafts and non-production builds are `noindex`), and paginated titles.
- Open Graph and X cards, with a 1200×630 social image cropped automatically from `featured.*`. Pages without one fall back to the default image.
- JSON-LD `@graph`: Organization, WebSite, Person, the page node (BlogPosting / Blog / AboutPage / CollectionPage) and BreadcrumbList.
- `sitemap.xml`, full-content RSS (site, blog, and each category/author), and `robots.txt` with a sitemap line and Content-Signal.
- **For answer engines:** `/llms.txt` plus a clean Markdown twin of every page at `<url>index.md`, linked via `rel="alternate"`.
- Performance: zero JS, self-hosted subset fonts (about 50 KB preloaded), AVIF images, one fingerprinted CSS file with SRI, and immutable caching for hashed assets.

## Deploy (Netlify)

| File | Role |
|---|---|
| `netlify.toml` | Build command, pinned `HUGO_VERSION` / `NODE_VERSION`, security headers + CSP, cache rules |
| `scripts/build.sh` | The build Netlify runs (and `npm run check` locally). Fails the deploy if any gate fails |
| `data/redirects.yaml` → `layouts/home.redirects` → `public/_redirects` | Every legacy URL, `.html` twins, `page/1/`, `blog.koipun.com` |

**Gates on every deploy:**
1. Tailwind class order.
2. A clean Hugo build.
3. All 154 legacy URLs resolve under Netlify's routing rules (`scripts/migration/linkcheck.mjs`).
4. Production only: the SEO audit.

**Contexts:**
- Production builds `koipun.com`.
- Deploy previews and branch deploys build with `--environment preview` on their own URL. Every page is `noindex` and `robots.txt` disallows everything, so previews never compete with the real site.

**Headers:**
- A strict CSP (no scripts at all), `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`.
- Hashed files (`/css/*`, `/fonts/*`, `*_hu_*` images) are immutable for a year. Everything else revalidates by ETag.
- Markdown twins and `llms.txt` are `noindex`.

**Test locally like Netlify:** `npm run check && netlify dev --dir public --offline` serves the build with the real redirect and header engine.

### One-time setup

1. Push the repo to GitHub, then in Netlify choose **Add new site → Import from Git**. `netlify.toml` provides the rest. No environment variables are needed.
2. **Domains:** set `www.koipun.com` as primary. Add `koipun.com`, which Netlify redirects to www, and `blog.koipun.com` as a domain alias (the 2015 Tumblr redirects in `_redirects` depend on it).
3. **DNS, a day before cut-over:** lower the TTL on the current records to 300 s. Then point `www` and `blog` as CNAME to `<site>.netlify.app`, and the apex to Netlify's load balancer (or use Netlify DNS). HTTPS is provisioned automatically.
4. **After cut-over:**
   - Check `curl -I https://www.koipun.com/blog/rss/` returns a 301 to `/blog/index.xml`.
   - Spot-check a few legacy URLs.
   - Submit `sitemap.xml` in Google Search Console and Bing Webmaster Tools.

## Content

36 posts (34 from ButterCMS, 2 recovered from the 2015 Tumblr blog) plus the About, Help, Anki and Privacy pages, with 176 images at original resolution. `scripts/migration/` holds the converter, the hand-written alt text, the SEO audit and the legacy link checker.

## To do

- [x] Migrate posts and pages from `_archive/`
- [x] Netlify one-time setup (above): site, domains incl. `blog.koipun.com`, DNS (live since 2026-11-23)
- [x] Set `enableGitInfo = true` (migrated posts pin `lastmod` to their original date)
- [x] Decide `ai-train=` in `layouts/robots.txt`: `yes`
- [ ] Higher-res logo (the best surviving one is 232 px)
- [ ] Verify in Search Console and submit the sitemap
- [x] Manga Sensei interview: the deleted SoundCloud track is replaced by the same episode on Spreaker

## Contributing

Pull requests are welcome: dead links in old posts, accessibility fixes, furigana corrections, bugs and design-system improvements. Old posts and interviews keep their original wording. See [CONTRIBUTING.md](CONTRIBUTING.md) for what's useful and how to run the checks before you open a PR.

## License

Code (templates, CSS, scripts) is MIT. The writing, interviews, photos and the Koipun name and logo are all rights reserved. Fonts and icons keep their own licenses. Details in [LICENSE](LICENSE).
