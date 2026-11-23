#!/usr/bin/env bash
# Regenerates assets/fonts/ from the Google Fonts sources (SIL OFL 1.1).
# Needs: python3 with fonttools + brotli  (pip install fonttools brotli)
#
# - Latin files cover Western European + romaji macrons (ā ē ī ō ū).
# - Japanese files hold all kana, Japanese punctuation, full-width forms and only the
#   kanji used on the site. Run again after adding posts with new kanji in headings.
#   (Body Japanese uses the system font, so only heading kanji really matter.)
set -euo pipefail
cd "$(dirname "$0")/../.."
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
src=https://raw.githubusercontent.com/google/fonts/main/ofl

curl -sfL -o "$work/Inter.ttf"     "$src/inter/Inter%5Bopsz,wght%5D.ttf"
curl -sfL -o "$work/Caveat.ttf"    "$src/caveat/Caveat%5Bwght%5D.ttf"
curl -sfL -o "$work/ZKG-Bold.ttf"  "$src/zenkakugothicnew/ZenKakuGothicNew-Bold.ttf"
curl -sfL -o "$work/ZKG-Black.ttf" "$src/zenkakugothicnew/ZenKakuGothicNew-Black.ttf"

python3 - "$work" <<'EOF'
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
d = sys.argv[1]
for name, axes in [("Inter-400-700", {"opsz": 14, "wght": (400, 700)}), ("Inter-600", {"opsz": 14, "wght": 600})]:
    f = TTFont(f"{d}/Inter.ttf"); instancer.instantiateVariableFont(f, axes, inplace=True); f.save(f"{d}/{name}.ttf")
f = TTFont(f"{d}/Caveat.ttf"); instancer.instantiateVariableFont(f, {"wght": 600}, inplace=True); f.save(f"{d}/Caveat-600.ttf")
EOF

kanji=$(python3 - <<'EOF'
import pathlib
s = set()
for p in [*pathlib.Path("content").rglob("*.md"), *pathlib.Path("layouts").rglob("*.*"), pathlib.Path("hugo.toml")]:
    s |= {c for c in p.read_text("utf-8", errors="ignore") if 0x3400 <= ord(c) <= 0x9FFF}
print("".join(sorted(s)))
EOF
)

latin="U+0000-00FF,U+0100-017F,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2190-2199,U+2212,U+2215,U+FEFF,U+FFFD"
ja="U+3000-303F,U+3040-309F,U+30A0-30FF,U+FF00-FFEF"
web=(--flavor=woff2 --no-hinting --desubroutinize)
out=assets/fonts/web

pyftsubset "$work/Inter-400-700.ttf" --unicodes="$latin" --layout-features+=tnum,case "${web[@]}" --output-file=$out/inter-latin.woff2
pyftsubset "$work/Caveat-600.ttf" --unicodes="U+0020-007E,U+00A0-00FF,U+2010-2027,U+2190-2193" "${web[@]}" --output-file=$out/caveat-600-latin.woff2
for w in 700:Bold 900:Black; do
  pyftsubset "$work/ZKG-${w#*:}.ttf" --unicodes="$latin" --layout-features='*' "${web[@]}" --output-file=$out/zen-kaku-gothic-new-${w%:*}-latin.woff2
  pyftsubset "$work/ZKG-${w#*:}.ttf" --unicodes="$ja" --text="$kanji" --layout-features='*' "${web[@]}" --output-file=$out/zen-kaku-gothic-new-${w%:*}-ja.woff2
done
# TTFs for build-time social cards (images.Text needs TTF/OTF)
pyftsubset "$work/ZKG-Black.ttf" --unicodes="$latin,$ja" --text="$kanji" --layout-features='*' --output-file=assets/fonts/ZenKakuGothicNew-Black.ttf
pyftsubset "$work/Inter-600.ttf" --unicodes="$latin" --layout-features='*' --output-file=assets/fonts/Inter-SemiBold.ttf
ls -la $out assets/fonts/*.ttf
