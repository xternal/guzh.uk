#!/usr/bin/env bash
# Regenerate assets/og.png — the 1200x630 link-preview card.
#
# Run this whenever the headline, the lead line, the portrait treatment or favicon.svg changes,
# or the card will quietly disagree with the page. Requires ImageMagick (brew install imagemagick)
# and rsvg-convert (brew install librsvg).
#
#   ./tools/make-og.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

FONT_DIR="${TMPDIR:-/tmp}/guzh-og-fonts"
FONT="$FONT_DIR/Geist-var.ttf"

# Geist is not a system font. Grab the variable TTF from the Google Fonts repo.
# (The Google Fonts CSS API serves woff2/EOT, which ImageMagick cannot read.)
if [ ! -f "$FONT" ]; then
  mkdir -p "$FONT_DIR"
  curl -sL -o "$FONT" \
    "https://raw.githubusercontent.com/google/fonts/main/ofl/geist/Geist%5Bwght%5D.ttf"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Match the CSS filter on .portrait img in index.html (currently: warm).
# warm  -> -modulate 103,102,100 -brightness-contrast 0x2
# mono  -> -colorspace Gray -colorspace sRGB -brightness-contrast 0x4
magick assets/pavel-web.png \
  -modulate 103,102,100 -brightness-contrast 0x2 \
  -resize 360x360^ -gravity center -extent 360x360 "$TMP/portrait.png"

# The mark is favicon.svg itself, without its square and recoloured from the dark palette to the
# card's ink and blue, so the card and the favicon cannot drift apart. At 44 px the line it draws
# spans 33x22 and starts 5.5 px in from the left, 11 px down from the top.
sed -e 's#<rect[^>]*/>##' -e 's/#EFE7DA/#171613/g' -e 's/#E2B26F/#1F3BC4/g' favicon.svg > "$TMP/mark.svg"
grep -q '#171613' "$TMP/mark.svg" && grep -q '#1F3BC4' "$TMP/mark.svg" \
  || { echo "favicon.svg no longer uses #EFE7DA and #E2B26F: update the recolour above" >&2; exit 1; }
rsvg-convert -w 44 -h 44 "$TMP/mark.svg" -o "$TMP/mark.png"

# NB: -gravity set inside a \( \) group leaks out, which silently pushes the
# composite off-canvas. Hence the separate portrait render above and the
# explicit -gravity NorthWest below.
magick -size 1200x630 xc:'#F1EFE9' \
  "$TMP/portrait.png" -gravity NorthWest -geometry +768+135 -composite \
  "$TMP/mark.png" -geometry +66+505 -composite \
  -font "$FONT" -gravity NorthWest \
  -fill '#171613' -stroke '#171613' -strokewidth 0.55 -pointsize 56 \
  -annotate +72+112 'I build and run' \
  -annotate +72+178 'companies.' \
  -stroke none \
  -gravity None -fill '#1F3BC4' -draw 'rectangle 72,268 136,271' \
  -gravity NorthWest \
  -fill '#544F46' -pointsize 21 \
  -annotate +72+310 'Zero to one, four times. Two exits. One unicorn.' \
  -annotate +72+344 'Still an unfulfilled desire to build things that matter.' \
  -fill '#8B857A' -pointsize 19 \
  -annotate +119+520 'Pavel Guzhikov, London, guzh.uk' \
  assets/og.png

echo "wrote assets/og.png ($(magick identify -format '%wx%h' assets/og.png))"
