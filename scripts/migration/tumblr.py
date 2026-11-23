import sys, re
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify
W = Path(sys.argv[1]); C = Path(sys.argv[2])
posts = [
  ("110390648373/using-anki-to-learn-hiragana", "using-anki-to-learn-hiragana", "2015-02-07",
   "How to use Anki and spaced repetition to learn hiragana — setup steps and tips for building a daily review habit.",
   ["anki", "hiragana", "spaced repetition"]),
  ("114272662048/strengthening-your-genki-studies-with-the-genki", "genki-annihilation-anki-deck", "2015-03-21",
   "How to use the Genki Annihilation Anki deck — native audio, furigana and lesson tags — to retain GENKI grammar and vocabulary.",
   ["anki", "genki", "spaced repetition"]),
]
for src, slug, date, desc, tags in posts:
    s = BeautifulSoup(open(W / src, encoding="utf-8"), "html.parser")
    post = s.select_one(".post .text-body") or s.select_one(".text-body")
    title = s.select_one(".post h2, .post h1, .post .title")
    title = title.get_text(strip=True) if title else None
    for a in post.find_all("a"):
        a.attrs.pop("target", None)
        a["href"] = a["href"].replace("http://ankisrs.net/", "https://apps.ankiweb.net/")
    md = markdownify(str(post), heading_style="ATX", bullets="-", escape_underscores=False, escape_misc=False)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    out = C / "blog" / slug; out.mkdir(parents=True, exist_ok=True)
    fm = f'''---
title: "{title}"
description: "{desc}"
date: {date}
authors: [gabriel-j-perez-irizarry]
categories: [my-japanese-journey]
tags: [{", ".join(tags)}]
legacy: "Originally published on blog.koipun.com"
---

'''
    (out / "index.md").write_text(fm + md + "\n", encoding="utf-8")
    print(slug, title, len(md.split()), "words")
