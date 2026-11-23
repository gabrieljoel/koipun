# Koipun brand guide: Genkō

> **Genkō** (原稿用紙, *genkō yōshi*) is the squared paper every Japanese learner writes on.
> Koipun looks like a well-used study notebook: grid-paper ground, sumi-ink outlines,
> and the logo's koi red used the way a teacher uses a red pen.

- **Live reference:** [`/styleguide/`](https://www.koipun.com/styleguide/) renders every token and component from the real CSS (noindex).
- **Source of truth:** [`assets/css/main.css`](assets/css/main.css). This guide explains it, and the CSS wins if they ever disagree.
- **Mockups:** the "Koipun brand refresh" design canvas (direction A, chosen 2026-11-23).

**Contents:** [Principles](#principles) · [Logo](#logo) · [Color](#color) · [Typography](#typography) · [Furigana](#furigana) · [Shape and depth](#shape-and-depth) · [Imagery](#imagery) · [Components](#components) · [Voice](#voice) · [Accessibility](#accessibility) · [Implementation](#implementation) · [Changing the system](#changing-the-system)

---

## Principles

1. **A notebook, not a magazine.** Paper, ink, red pen, margin notes. Everything should feel handled and personal, never glossy.
2. **Red means "the teacher marked this."** Koi red is rare and meaningful: the main action, a key word, a reading. If everything is red, nothing is.
3. **Reading comes first.** Long interviews are the product. Text sits on clean paper with no grid behind it, at a comfortable measure (about 70 characters).
4. **Japanese is first-class.** Furigana, kana and kanji get real typographic care. They are never an afterthought or set in brackets.
5. **Light on the wire.** No JavaScript, self-hosted subset fonts, AVIF images. Speed is part of the brand.

---

## Logo

The hand-lettered **koipun** speech bubble: white letters on koi red. **It is not changing.**

| Rule | Value |
|---|---|
| File | `assets/images/logo.png` (232 × 232 px, the best surviving original; a vector or 1024 px version is a to-do) |
| Minimum size | 32 px on screen (the header uses 36 px on phones, 44 px on desktop) |
| Clear space | At least ¼ of the logo's width on every side |
| Wordmark beside it | "Koipun" in Zen Kaku Gothic New Black, `text-fg` |
| Backgrounds | Paper, night (dark mode), or the brand pattern. The red bubble carries its own contrast. |

**Don't** recolor, outline, rotate, stretch, add shadows to, or crop the logo, place it on a busy photo, or redraw the lettering in a font.

---

## Color

Two scales plus one line color. Tailwind's default palette is **removed**, so only these exist.

### Primitives

**Koi** (the logo red): `koi-600` is the logo itself.

| Token | Hex | Used for |
|---|---|---|
| `koi-50` | `#FFF4F1` | Quote and tint fills (light) |
| `koi-100` | `#FFE3DD` | |
| `koi-200` | `#FFC2B7` | Text selection; red-pen text on the brand theme |
| `koi-300` | `#FF9A8A` | Red-pen strokes on the brand theme |
| `koi-400` | `#FF7A66` | Red-pen text in dark mode |
| `koi-500` | `#F0432C` | Red-pen strokes in dark mode |
| **`koi-600`** | **`#D9230F`** | **Logo, primary buttons, red-pen strokes (light)** |
| `koi-700` | `#B81D0C` | Red-pen **text** (light); button hover |
| `koi-800` | `#8F1608` | Button "pressed edge" |
| `koi-900` | `#561B15` | Brand-theme ground (the Anki pattern page) |
| `koi-950` | `#2E0D09` | Button edge on the brand theme |

**Sumi** (warm paper to ink):

| Token | Hex | Used for |
|---|---|---|
| **`sumi-50`** | **`#FFFDF8`** | **Paper** (page and card ground) |
| `sumi-100` | `#F7F2EA` | Code text on dark blocks |
| `sumi-200` | `#E9E2D6` | Hairlines (light) |
| `sumi-300` | `#D3CABC` | |
| `sumi-400` | `#B9B0A2` | Muted text (dark) |
| `sumi-500` | `#8C8478` | |
| `sumi-600` | `#6B645C` | Meta text: dates, breadcrumbs |
| `sumi-700` | `#4A453F` | Secondary text |
| `sumi-750` | `#3A352E` | Night rule: borders in dark mode |
| `sumi-800` | `#2A2622` | Body text |
| `sumi-850` | `#1C1915` | Night paper: cards in dark mode |
| **`sumi-900`** | **`#1C1A17`** | **Ink**: headings, outlines, offset shadows |
| `sumi-950` | `#14120F` | Night: page ground in dark mode |

**Grid blue** `#E3EAF3`: grid-paper lines only, never text or fills.

### Semantic roles: what templates actually use

Components never name a primitive. They name a **role**, and each theme decides what the role is.

| Role | Meaning | Light | Dark ("night study") | Brand theme (`.theme-brand`) |
|---|---|---|---|---|
| `surface` | Page ground, under the grid | sumi-50 | sumi-950 | koi-900 |
| `raised` | Cards, panels, header | sumi-50 | sumi-850 | white 6% |
| `tint` | Quotes, hover fills | koi-50 | koi-400 12% on night paper | white 10% |
| `fg` | Headings, strong text | sumi-900 | `#EEE7DB` (chalk) | white |
| `body` | Long-form text | sumi-800 | `#DCD4C7` | white 92% |
| `muted` | Secondary text | sumi-700 | sumi-400 | white 88% |
| `subtle` | Meta: dates, counts | sumi-600 | sumi-400 | white 78% |
| `line` | Ink outlines | sumi-900 | sumi-750 | white |
| `hairline` | Quiet separators | sumi-200 | sumi-750 | white 25% |
| `grid` | Grid-paper lines | grid blue | white 5% | n/a (pattern) |
| `pen` | Red-pen **text** | koi-700 | koi-400 | koi-200 |
| `pen-mark` | Red-pen **strokes** (underlines, chip borders, drop cap) | koi-600 | koi-500 | koi-300 |
| `btn` / `btn-fg` | Primary button | koi-600 / white | koi-600 / white | white / koi-700 |
| `btn-hover` | Primary hover | koi-700 | koi-700 | koi-50 |

**`pen` vs `pen-mark`:** use `text-pen` for any red words people read; it passes 4.5:1 on every ground. `pen-mark` is for strokes and large decoration, where 3:1 is enough.

### Contrast (measured, WCAG 2.2)

| Pair | Light | Dark | Brand |
|---|---|---|---|
| `fg` on `surface` | 17.1 | 15.2 | 13.4 |
| `body` on `surface` | 14.8 | 12.7 | n/a |
| `muted` on `surface` | 9.3 | 8.7 | n/a |
| `subtle` on `surface` | 5.7 | 8.7 | n/a |
| `pen` on `surface` | 6.4 | 7.3 | 8.7 |
| `pen` on `tint` / `raised` | 6.1 | 6.9 | n/a |
| `btn-fg` on `btn` | 5.0 | 5.0 | 6.5 |
| `btn-fg` on `btn-hover` | 6.5 | 6.5 | n/a |
| `pen-mark` on `surface` (strokes) | 4.9 | n/a | n/a |

Everything a person reads clears **AA (4.5:1)**. Re-measure when you change a color (see [Changing the system](#changing-the-system)).

---

## Typography

| Family | Role | Weights | Notes |
|---|---|---|---|
| **Zen Kaku Gothic New** | `font-display`: headings, wordmark, quotes, drop cap. Japanese in headings. | 700, 900 | One family for both scripts, so mixed titles stay even. Japanese glyphs load only when a heading uses them. |
| **Inter** | `font-sans`: body, UI, card titles | 400–700 (variable) | Body runs at 17–19 px with 1.75 line height. |
| **Caveat** | `font-hand`: margin notes, category chips, captions, pager | 600 | Decoration only. Never paragraphs, never more than about 8 words. |
| System Japanese | `font-ja`: Japanese in body text | n/a | Hiragino, Noto Sans JP, Yu Gothic. No download, native rendering. |

**Scale:**
- Hero: `text-5xl` to `xl:text-7xl`, `font-black`, tight tracking.
- Page and post H1: `text-4xl` / `sm:text-5xl`, `font-black`.
- H2 in sections: `text-3xl` / `sm:text-4xl`, `font-black`. In prose, H2 follows the `prose-lg` scale.
- Card title: Inter `text-xl` semibold.
- Meta: `text-sm`, `subtle`.

Headings use `text-balance` and paragraphs use `text-pretty`, so there are no orphans.

**Handwriting budget:** about one note per screen. Hand-lettered items are the category chip, eyebrow notes, image captions, the hero note and the pager. That's the full list.

---

## Furigana

Readings are written in **red pen above the kanji**, never in brackets.

- Author with the shortcode: `{{</* ruby "漢字" "かん|じ" */>}}` (per character) or `{{</* ruby "先生" "せんせい" */>}}` (whole word).
- It renders native `<ruby lang="ja">` with `<rp>` fallbacks. Readings are `0.5em`, weight 500, color `pen`.
- An annotated word never wraps mid-word. Copying the text gives clean kanji without the readings. Lines containing ruby get extra leading (2.1).
- Tested in Chromium, Firefox and WebKit.

---

## Shape and depth

| Element | Rule |
|---|---|
| Outlines | **2 px ink** (`border-2 border-line`) on cards, images and menus. Hairlines (`border-hairline`, 1 px) only for separators inside a card. |
| Corners | `rounded-md` (6 px) for paper and images, `rounded-lg` (8 px) for buttons, `rounded-full` for chips and portraits. |
| Shadows | Hard offset, no blur, like paper on a desk: `shadow-paper` (4 px, hover and menus), `shadow-paper-lg` (8 px, featured images), `shadow-press` (button edge). Never soft drop shadows. |
| Tilt | Only the hero photo (`rotate-[1.5deg]`) and handwritten notes (`-rotate-2` / `-rotate-3`). Body images stay straight. |
| Grid paper | `paper-grid` on the page: 24 px squares on phones, 32 px from `sm`. Long text sits on a solid `surface` panel. |
| Motion | Small and physical: clickable cards lift 2 px on hover (`lift`), buttons press down 2 px. Nothing animates on its own. |

---

## Imagery

- **Photos:** real Japan and real learning: izakaya, lanterns, manga, textbooks, worksheets. Warm, a little grainy is fine. No stock "smiling student with laptop".
- **Treatment:** 2 px ink outline, `rounded-md`. Featured images also get `shadow-paper-lg`. Post images keep their authored size (never upscaled), float beside the text from 640 px, and stack centered on phones.
- **Pattern:** the 12-icon line-art tile (`assets/images/patterns/japan-icons.svg`) belongs to the brand theme only (the Anki page). It's vector, so redraw it rather than rasterize it.
- **Social cards:** generated at 1200 × 630 from the page photo, with shading, logo + koipun.com, the title in Zen Kaku Gothic New Black, and a koi-red bottom bar (`func/og-image.html`).
- **Alt text:** describe what the photo shows, not the post title.

---

## Components

All live in `layouts/_partials/components/`. Compose these rather than inventing new styles.

| Component | Recipe |
|---|---|
| Button: `primary` | Koi red, white text, `shadow-press` edge, presses down on click. **One per view.** |
| Button: `secondary` | Ink-outlined paper (`border-2 border-line bg-raised`) |
| Button: `link` | Red-pen underlined text: the quiet second action beside a primary |
| `card` + `lift` | Paper sheet with ink outline. Add `lift` when it is clickable (raises 2 px with `shadow-paper`). |
| `category-chip` | Handwritten red-pen pill (`chip-hand`), lowercased label from the term's `short:` field |
| `hero` | Note + headline with `pen-underline` on the `*emphasized*` word + CTAs + tilted photo with handwritten caption |
| `post-card` | Card: 16:9 image, chip, Inter title, 3-line excerpt, meta footer |
| `split-section` | Text + image (`rounded-md` or circle), outlined with `shadow-paper-lg` |
| `prose` | `prose prose-lg prose-genko` (+ `dropcap` on posts): token-driven typography, red-pen links, card-style quotes, handwritten captions |
| `pagination`, `breadcrumbs`, `author-box`, `page-header`, `statement` | Built from the same tokens |

**Links:** in text, use `link-pen` (ink text, red underline, red on hover). In navigation, use plain `text-fg`; the current page gets a 3 px red underline.

---

## Voice

- **First person, peer to peer.** "I", "you", a fellow learner who's a few steps ahead, never a guru.
- **Honest about difficulty.** Struggle, mistakes and method are the story. Avoid "master Japanese fast" claims.
- **Plain English with Japanese where it helps**, always with a reading or gloss: 居酒屋 (izakaya).
- **Old posts are archival.** Keep their original wording and typos.

---

## Accessibility

- Text clears **4.5:1** in all three themes (table above); focus rings are 2 px `pen-mark` outlines.
- Touch targets are **at least 44 px** (header menu, buttons, pager).
- Real elements only: `<a>`, `<button>`, `<details>` for the mobile menu (works without JS).
- Color is never the only signal: active nav has an underline, links are underlined.
- `lang="ja"` on Japanese text so screen readers switch voices.

---

## Implementation

Tailwind CSS v4, **CSS-first, no preprocessor** (Tailwind v4 is its own: nesting, imports, prefixing). Compiled by Hugo's `css.TailwindCSS`.

```
@theme              primitives: koi-*, sumi-*, grid-blue, fonts. Defaults removed (--color-*: initial)
@theme inline       roles: --color-surface: var(--surface) … plus shadow-paper / shadow-press
@utility theme-*    theme-paper · theme-night · theme-brand set every role. :root applies paper,
                    dark mode applies night, and any element can apply one (the style guide does).
@utility            paper-grid · card · lift · chip-hand · pen-underline · link-pen · prose-genko · dropcap · container-page · container-prose
partials            components compose roles + utilities
```

**Rules:**
- Templates use roles (`text-fg`, `border-line`, `bg-raised`, `text-pen`) and the Genkō utilities. **Never `dark:`** (themes handle it) and **never raw hex**.
- New theme? Add one `@utility theme-…` that sets every role, like `theme-brand`.
- Prefer native utilities over arbitrary values (`aspect-4/3`, not `aspect-[4/3]`). Arbitrary values are for one-off layout tracks only.
- Class order is Tailwind's canonical order, enforced: `npm run format:classes` fixes it, and `npm run check` fails if it's off.
- Long-form styles go in `prose-genko`, not in per-template arbitrary variants.
- Fonts are self-hosted subsets in `assets/fonts/web/`, fingerprinted by `head/fonts.html`. Regenerate with `scripts/fonts/subset.sh` (it picks up new kanji from content).

## Changing the system

1. Change the token in `assets/css/main.css` (primitive or role), not in a template.
2. Check `/styleguide/` in light and dark (`npm run dev`, then toggle the OS theme).
3. Re-measure any text pair you touched for 4.5:1 and update the contrast table here.
4. Run `npm run check` and the SEO audit.
