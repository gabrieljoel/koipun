# Legacy migration (one-off)

Scripts used on 2026-11-23 to convert the scraped koipun.com (`_archive/`, gitignored) into `content/`.
Kept for provenance and in case a re-import is needed. Re-running **overwrites** the generated post bundles.

```sh
uv run --no-project --with beautifulsoup4 --with markdownify --with lxml \
  python -I scripts/migration/migrate.py _archive content      # 34 ButterCMS posts
uv run --no-project --with beautifulsoup4 --with markdownify \
  python -I scripts/migration/tumblr.py _archive/scrape-wayback/blog.koipun.com/post content   # 2015 Tumblr posts
npm run check   # build + linkcheck + audit: python3 -I scripts/migration/audit.py public scripts/migration/legacy-urls.txt public/_redirects
```

- `alt-overrides.json` holds hand-written alt text for images that had none (`undefined`) in ButterCMS.
- `audit.py` checks legacy URL parity, broken internal refs/srcsets, SEO tags, single h1, JSON-LD validity and alt attributes.
- Standalone pages (about, help, anki, privacy) were ported by hand.
