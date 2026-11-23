"""Migrate scraped koipun.com blog posts into Hugo page bundles.

usage: migrate.py <archive_dir> <content_dir>
"""
import sys, re, json, glob, shutil, hashlib, mimetypes, unicodedata
from pathlib import Path
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import MarkdownConverter

ARCHIVE = Path(sys.argv[1])
CONTENT = Path(sys.argv[2])
SITE = ARCHIVE / "scrape/www.koipun.com"
EXT = ARCHIVE / "scrape-external"
SKIP = {"page", "rss", "author", "category"}
report = {"posts": [], "missing_images": [], "kept_html": []}
ALT = json.loads((Path(__file__).parent / "alt-overrides.json").read_text(encoding="utf-8"))
INLINE_MAX_W = 160  # images narrower than this may stay inline (glyphs, icons)


def alt_for(url, alt):
    """Best alt text: manual override → original (unless junk) → ''."""
    src = local_image(url)
    if src:
        try:
            key = str(src.relative_to(EXT))
            if key in ALT:
                return ALT[key]
        except ValueError:
            pass
    alt = (alt or "").strip()
    return "" if alt.lower() in ("undefined", "null", "image") else alt


def img_width(url):
    import subprocess
    src = local_image(url)
    if not src:
        return 0
    out = subprocess.run(["sips", "-g", "pixelWidth", str(src)], capture_output=True, text=True).stdout
    m = re.search(r"pixelWidth: (\d+)", out)
    return int(m.group(1)) if m else 0


def slugify(s, maxlen=60):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:maxlen].rstrip("-") or "image"


def q(s):  # YAML-safe scalar (JSON strings are valid YAML)
    return json.dumps(s, ensure_ascii=False)


def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else ""


# ---------------------------------------------------------------- image lookup
def local_image(url):
    """Map a remote/legacy image URL to a file in the archive."""
    if not url:
        return None
    url = url.replace("&amp;", "&")
    if url.startswith("//"):
        url = "https:" + url
    u = urlparse(url)
    # Filestack resize proxy → original ButterCMS handle (full resolution)
    m = re.search(r"https://cdn\.buttercms\.com/([A-Za-z0-9]+)", url)
    if "filestackapi.com" in u.netloc and m:
        p = EXT / "cdn.buttercms.com" / m.group(1)
        return p if p.exists() else None
    if u.netloc in ("", "www.koipun.com", "koipun.com", "localhost"):
        p = SITE / unquote(u.path).lstrip("/")
        return p if p.exists() else None
    p = EXT / u.netloc / unquote(u.path).lstrip("/")
    return p if p.exists() else None


def ext_for(path):
    import subprocess
    mime = subprocess.run(["file", "-b", "--mime-type", str(path)], capture_output=True, text=True).stdout.strip()
    return {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp",
            "image/svg+xml": ".svg"}.get(mime) or mimetypes.guess_extension(mime) or ".bin"


class Bundle:
    """Copies images into a page bundle with stable, descriptive names."""

    def __init__(self, dirpath):
        self.dir = dirpath
        self.by_src = {}
        self.names = set()

    def add(self, url, alt="", name=None):
        src = local_image(url)
        if not src:
            report["missing_images"].append({"page": self.dir.name, "url": url})
            return None
        key = str(src)
        if key in self.by_src:
            return self.by_src[key]
        base = name or slugify(alt or Path(urlparse(url).path).stem, 50)
        fname = base + ext_for(src)
        i = 2
        while fname in self.names:
            fname = f"{base}-{i}{ext_for(src)}"
            i += 1
        self.names.add(fname)
        shutil.copy2(src, self.dir / fname)
        self.by_src[key] = fname
        return fname


# ---------------------------------------------------------------- HTML → Markdown
SNIPS = []


def block(md):
    SNIPS.append(md)
    return NavigableString(f" KPBLOCK{len(SNIPS)-1}X ")


def inline(md):
    SNIPS.append(md)
    return NavigableString(f"KPINLINE{len(SNIPS)-1}X")


YOUTUBE = re.compile(r"(?:youtube(?:-nocookie)?\.com/embed/|youtu\.be/)([\w-]{11})")


def ruby_shortcode(rb):
    """<ruby>先<rt>せん</rt>生<rt>せい</rt></ruby> → {{< ruby "先生" "せん|せい" >}}"""
    bases, readings, cur = [], [], ""
    for node in rb.children:
        if isinstance(node, NavigableString):
            cur += str(node)
        elif node.name == "rb":
            cur += node.get_text()
        elif node.name == "rt":
            bases.append(cur.strip())
            readings.append(node.get_text().strip())
            cur = ""
    if cur.strip() or not bases or any(not b for b in bases):
        return None
    if len(bases) == 1:
        return f'{{{{< ruby "{bases[0]}" "{readings[0]}" >}}}}'
    if all(len(b) == 1 for b in bases):
        return f'{{{{< ruby "{"".join(bases)}" "{"|".join(readings)}" >}}}}'
    return " ".join(f'{{{{< ruby "{b}" "{r}" >}}}}' for b, r in zip(bases, readings))


def preprocess(body, bundle):
    """Normalise the DOM before markdownify; returns nothing (mutates)."""
    # unwrap layout wrappers
    for div in body.find_all("div"):
        div.unwrap()
    # YouTube / other iframes
    for ifr in body.find_all("iframe"):
        m = YOUTUBE.search(ifr.get("src", ""))
        if m:
            ifr.replace_with(block(f"{{{{< youtube {m.group(1)} >}}}}"))
        else:
            ifr["loading"] = "lazy"
            ifr["title"] = ifr.get("title") or "Embedded audio"
            for a in ("frameborder", "scrolling"):
                ifr.attrs.pop(a, None)
            ifr["style"] = "border:0;width:100%"
            report["kept_html"].append({"page": bundle.dir.name, "html": str(ifr)[:200]})
            ifr.replace_with(block(f"{str(ifr)}"))
    # ruby → shortcode
    for rb in body.find_all("ruby"):
        sc = ruby_shortcode(rb)
        if sc:
            rb.replace_with(inline(f"{sc}"))
        else:
            rb["lang"] = "ja"
            report["kept_html"].append({"page": bundle.dir.name, "html": str(rb)})
            rb.replace_with(inline(f"{str(rb)}"))
    # figures with captions
    for fig in body.find_all("figure"):
        img = fig.find("img")
        cap = text(fig.find("figcaption"))
        if not img:
            fig.unwrap()
            continue
        alt_text = alt_for(img.get("src"), img.get("alt"))
        fname = bundle.add(img.get("src"), alt_text or bundle.dir.name)
        cls = " ".join(img.get("class", []))
        attr = "\n{.float-left}" if "float-left" in cls else "\n{.float-right}" if "float-right" in cls else ""
        alt = alt_text.replace("]", "\\]")
        title = f' "{cap.replace(chr(34), "&quot;")}"' if cap else ""
        md = f"![{alt}]({fname}{title}){attr}" if fname else f"<!-- missing image: {img.get('src')} -->"
        fig.replace_with(block(f"{md}"))
    # remaining images: floated ones are hoisted before their block as figures
    for img in body.find_all("img"):
        alt_text = alt_for(img.get("src"), img.get("alt"))
        fname = bundle.add(img.get("src"), alt_text or bundle.dir.name)
        alt = alt_text.replace("]", "\\]")
        if not fname:
            img.replace_with(NavigableString(f"<!-- missing image: {img.get('src')} -->"))
            continue
        cls = " ".join(img.get("class", []))
        side = "left" if "float-left" in cls else "right" if "float-right" in cls else None
        parent = img.find_parent(["p", "li", "blockquote", "h2", "h3"])
        if side and parent is not None:
            img.extract()
            parent.insert_before(block(f"![{alt}]({fname})\n{{.float-{side}}}"))
        elif parent is not None and not text(parent) and len(parent.find_all("img")) == 1:
            parent.replace_with(block(f"![{alt}]({fname})"))
        elif parent is not None and img_width(img.get("src")) > INLINE_MAX_W:
            img.extract()  # large image glued to text → its own figure before the block
            parent.insert_before(block(f"![{alt}]({fname})"))
        else:
            img.replace_with(inline(f"![{alt}]({fname})"))
    # links: absolute koipun.com → root-relative; clean tracking
    for a in body.find_all("a", href=True):
        h = a["href"].strip()
        h = re.sub(r"^https?://(www\.)?koipun\.com", "", h) or "/"
        if h == "/blog/march-month-in-review":
            h = "/blog/march-month-in-review-2017/"
        if re.match(r"^/[^#?]*[^/#?.]$", h):  # add trailing slash to internal paths
            h += "/"
        a["href"] = h


class Converter(MarkdownConverter):
    def convert_br(self, el, text, parent_tags):
        return "  \n"


def html_to_md(body):
    md = Converter(heading_style="ATX", bullets="-", strong_em_symbol="*", escape_underscores=False,
                   escape_asterisks=False, escape_misc=False).convert_soup(body)
    # restore protected snippets (markdownify escapes nothing inside them now)
    md = re.sub(r"\s*KPBLOCK(\d+)X\s*", lambda m: "\n\n" + SNIPS[int(m.group(1))] + "\n\n", md)
    md = re.sub(r"KPINLINE(\d+)X", lambda m: SNIPS[int(m.group(1))], md)
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"(?m)^(#{1,6} [^\n]*?)[ \t]*\n(?!\n)", r"\1\n\n", md)  # blank line after headings
    return md.strip() + "\n"


# ---------------------------------------------------------------- metadata sources
def rss_dates():
    s = BeautifulSoup(open(SITE / "blog/rss/index.html", encoding="utf-8"), "xml")
    out = {}
    for it in s.find_all("item"):
        slug = it.link.get_text().rstrip("/").split("/")[-1]
        out[slug] = parsedate_to_datetime(it.pubDate.get_text())
    return out


def card_data():
    """slug → {name, level, image} from listing cards across the archive."""
    out = {}
    for f in SITE.rglob("*.html"):
        s = BeautifulSoup(open(f, encoding="utf-8"), "html.parser")
        for panel in s.select("div.panel"):
            a = panel.select_one("a.post-card-anchor")
            if not a:
                continue
            slug = a["href"].rstrip("/").split("/")[-1]
            foot = panel.select_one(".panel-footer")
            d = out.setdefault(slug, {})
            if foot:
                lvl = foot.select_one(".label")
                name = foot.select_one(".pull-right")
                if name and text(name):
                    d["name"] = text(name)
                if lvl and text(lvl):
                    d["level"] = text(lvl)
            img = a.find("img")
            if img and img.get("src"):
                d.setdefault("image", img["src"])
    return out


# ---------------------------------------------------------------- main
def migrate_post(path, dates, cards):
    slug = path.parent.name
    s = BeautifulSoup(open(path, encoding="utf-8"), "html.parser")
    body = s.select_one("div.blog-post")
    col = body.find_parent("div", class_="col-md-8")
    title = text(col.select_one("h1.blog-title"))
    lead = text(col.select_one("p.lead"))
    meta_desc = (s.find("meta", attrs={"name": "description"}) or {}).get("content", "").strip()
    page_title = text(s.title).removeprefix("Koipun - ").strip()
    og_image = (s.find("meta", property="og:image") or {}).get("content")
    author_a = col.select_one('a[href*="/blog/author/"]')
    posted_in = col.find("h6")
    categories = [text(a) for a in posted_in.find_all("a")] if posted_in else []
    author = author_a["href"].rstrip("/").split("/")[-1] if author_a else "gabriel-j-perez-irizarry"
    category = categories[0] if categories else None

    out = CONTENT / "blog" / slug
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    bundle = Bundle(out)

    card = cards.get(slug, {})
    featured = bundle.add(og_image or card.get("image"), name="featured") if (og_image or card.get("image")) else None
    preprocess(body, bundle)
    md = html_to_md(body)

    date = dates.get(slug)
    fm = ["---", f"title: {q(title)}"]
    if page_title and page_title.lower() != title.lower():
        fm.append(f"seoTitle: {q(page_title)}")
    fm.append(f"description: {q(lead or meta_desc)}")
    if date:
        fm.append(f"date: {date.isoformat()}")
    else:
        report.setdefault("no_date", []).append(slug)
    fm.append(f"authors: [{author}]")
    if category:
        fm.append("categories: [" + ", ".join(slugify(c) for c in categories) + "]")  # term keys; titles live in content/categories/
    if featured:
        fm.append(f"image: {featured}")
        fm.append(f"imageAlt: {q(title)}")
    if card.get("name") and category and "Interview" in category:
        iv = f"name: {q(card['name'])}"
        if card.get("level"):
            iv += f", level: {q(card['level'])}"
        fm.append(f"interviewee: {{ {iv} }}")
    fm.append("---\n")
    (out / "index.md").write_text("\n".join(fm) + "\n" + md, encoding="utf-8")
    report["posts"].append({"slug": slug, "date": str(date)[:10], "category": category,
                            "images": len(bundle.names), "words": len(md.split()),
                            "interviewee": card.get("name") if category and "Interview" in category else None})


if __name__ == "__main__":
    dates, cards = rss_dates(), card_data()
    for p in sorted(SITE.glob("blog/*/index.html")):
        if p.parent.name not in SKIP:
            migrate_post(p, dates, cards)
    print(json.dumps(report, ensure_ascii=False, indent=1))
