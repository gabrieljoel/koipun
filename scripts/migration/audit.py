"""Audit a built Hugo site: legacy URL parity, broken internal refs, SEO tags, JSON-LD."""
import sys, re, json
from pathlib import Path
from urllib.parse import urlparse, unquote

PUB = Path(sys.argv[1]); INVENTORY = Path(sys.argv[2]); REDIRECTS = Path(sys.argv[3])  # Netlify _redirects
redirect_sources = [l.split()[0] for l in REDIRECTS.read_text().splitlines()
                    if l.strip() and not l.startswith("#") and not l.startswith("http")]


def exists(path):
    p = unquote(urlparse(path).path)
    f = PUB / p.lstrip("/")
    return f.is_file() or (f / "index.html").is_file()


def redirected(path):
    """First Netlify rule matching the path (trailing slash ignored; :name = one segment; trailing * = rest)."""
    p = path.rstrip("/") or "/"
    for src in redirect_sources:
        rx = re.escape(src.rstrip("/") or "/").replace(r"\*", "*")
        rx = re.sub(r":(\w+)", r"[^/]+", rx)
        rx = "^" + re.sub(r"/\*$", r"(?:/.*)?", rx) + "/?$"
        if re.match(rx, p):
            return src
    return None


problems = []
# 1. Legacy URL parity
for url in INVENTORY.read_text().split():
    if not exists(url) and not redirected(url):
        problems.append(f"LEGACY URL LOST: {url}")

# 2. Per-page checks
pages = sorted(PUB.rglob("*.html"))
seen_titles = {}
for f in pages:
    rel = "/" + str(f.relative_to(PUB)).removesuffix("index.html")
    h = f.read_text(encoding="utf-8")
    if 'http-equiv=refresh' in h:  # Hugo alias redirect pages
        continue
    for attr in re.findall(r'(?:href|src)="?(/[^" >]*)', h):
        if attr.startswith("//") or attr.startswith("/#"):
            continue
        if not exists(attr) and not redirected(attr):
            problems.append(f"BROKEN REF on {rel}: {attr}")
    for srcset in re.findall(r'srcset="([^"]+)"', h):
        for u in [x.strip().split(" ")[0] for x in srcset.split(",")]:
            if u.startswith("/") and not exists(u):
                problems.append(f"BROKEN SRCSET on {rel}: {u}")
    if rel == "/404.html":
        continue
    title = re.search(r"<title>(.*?)</title>", h)
    desc = re.search(r'<meta name=description content="([^"]*)"', h)
    for name, ok in [("title", title), ("description", desc and desc.group(1).strip()),
                     ("canonical", 'rel=canonical' in h), ("og:image", 'og:image"' in h),
                     ("h1", "<h1" in h), ("lang", "<html lang=" in h)]:
        if not ok:
            problems.append(f"MISSING {name}: {rel}")
    if title:
        seen_titles.setdefault(title.group(1), []).append(rel)
    if h.count("<h1") > 1:
        problems.append(f"MULTIPLE h1: {rel}")
    for m in re.findall(r"<script type=application/ld\+json>(.*?)</script>", h, re.S):
        try:
            json.loads(m)
        except Exception as e:
            problems.append(f"BAD JSON-LD {rel}: {e}")
    for img in re.findall(r"<img [^>]*>", h):
        if not re.search(r"\salt(=|[\s>])", img):
            problems.append(f"IMG WITHOUT alt on {rel}: {img[:80]}")
for t, rels in seen_titles.items():
    if len(rels) > 1:
        problems.append(f"DUPLICATE TITLE '{t}': {rels}")

# 3. Feeds / AEO files
for p in ["sitemap.xml", "robots.txt", "llms.txt", "index.xml", "blog/index.xml"]:
    if not (PUB / p).is_file():
        problems.append(f"MISSING FILE {p}")
md = list(PUB.rglob("index.md"))
print(f"pages={len(pages)} markdown_twins={len(md)} sitemap_urls={(PUB/'sitemap.xml').read_text().count('<loc>')} "
      f"blog_feed_items={(PUB/'blog/index.xml').read_text().count('<item>')}")
print(f"{len(problems)} problems")
for p in problems:
    print(" ", p)
