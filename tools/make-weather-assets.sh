#!/usr/bin/env bash
# Regenerate assets/weather/* — the app icon, the screenshots and the OG card for /weather/.
#
# The images are never hand-made here: they come from the Always Weather repo, which draws them
# from the real app (store/README.md there explains how). This script only resizes them for the
# web, so re-run it whenever those store assets change:
#
#   ./tools/make-weather-assets.sh [path-to-always_weather-repo]
#
# Requires ImageMagick (brew install imagemagick).
set -euo pipefail
cd "$(dirname "$0")/.."

APP="${1:-$HOME/dev/always_weather}"
SHOTS="$APP/store/google-play/metadata/android/en-GB/images/phoneScreenshots"
ICON="$APP/store/google-play/metadata/android/en-GB/images/icon.png"

[ -d "$SHOTS" ] || { echo "No store screenshots at $SHOTS — pass the Always Weather repo path." >&2; exit 1; }

mkdir -p assets/weather

# The icon, as drawn by the launcher's adaptive icon. 512x512, full square: the page rounds it.
cp "$ICON" assets/weather/icon.png

# Store screenshots carry their own caption, drawn in the Look's typeface — that is the artefact
# the stores get, so the page shows exactly it rather than a second, hand-made crop. 600px wide is
# 2x the column they sit in.
shot() { magick "$SHOTS/$1.png" -resize 600x1067 -quality 82 "assets/weather/$2.webp"; }
shot 01_sky-hours    shot-hours
shot 02_sky-sentence shot-sentence
shot 04_sky-night    shot-night

# ---- the 1200x630 link-preview card -----------------------------------------------------------
FONT_DIR="${TMPDIR:-/tmp}/guzh-og-fonts"
FONT="$FONT_DIR/Geist-var.ttf"
if [ ! -f "$FONT" ]; then
  mkdir -p "$FONT_DIR"
  curl -sL -o "$FONT" \
    "https://raw.githubusercontent.com/google/fonts/main/ofl/geist/Geist%5Bwght%5D.ttf"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# The icon's own three colours: #26303A ground, #EDF1F4 ink, #DFBD74 the degree sign.
magick "$ICON" -resize 200x200 "$TMP/icon.png"
magick -size 1200x630 xc:'#26303A' \
  "$TMP/icon.png" -gravity NorthWest -geometry +96+150 -composite \
  -font "$FONT" -gravity NorthWest \
  -fill '#EDF1F4' -stroke '#EDF1F4' -strokewidth 0.5 -pointsize 76 \
  -annotate +336+168 'Always Weather' \
  -stroke none -fill '#DFBD74' -pointsize 40 \
  -annotate +336+274 'Drag through the hours.' \
  -fill '#AFB8C0' -pointsize 28 \
  -annotate +336+352 'A calm, paid weather app. No ads, no account, no tracking.' \
  -strip assets/weather/og.png

echo "assets/weather/: $(ls assets/weather | tr '\n' ' ')"
