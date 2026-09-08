#!/usr/bin/env bash
# Regenerate assets/og.png — the 1200x630 link-preview card.
#
# Run this whenever the headline, the lead line, or the portrait treatment changes,
# or the card will quietly disagree with the page. Requires ImageMagick (brew install imagemagick).
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

# NB: -gravity set inside a \( \) group leaks out, which silently pushes the
# composite off-canvas. Hence the separate portrait render above and the
# explicit -gravity NorthWest below.
magick -size 1200x630 xc:'#F1EFE9' \
  "$TMP/portrait.png" -gravity NorthWest -geometry +768+135 -composite \
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
  -annotate +72+520 'Pavel Guzhikov · London, United Kingdom · guzh.uk' \
  assets/og.png

echo "wrote assets/og.png ($(magick identify -format '%wx%h' assets/og.png))"
