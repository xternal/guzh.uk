#!/usr/bin/env bash
# Regenerate assets/today/* — the icon, the screenshots and the OG card for /today/.
#
# Like tools/make-weather-assets.sh, nothing is hand-made here. The mark is the Always Today logo
# (docs/logo/cut-reflect.svg in the app repo: a half-sun with the tick cut out of it, on a horizon,
# with its reflection), and the screenshots are the app's own headless renders, made in the app repo
# by its screenshot test:
#
#   ./gradlew --max-workers=4 :app:desktopTest --tests 'alwaystoday.app.ScreensTest'   (in the app repo)
#   ./tools/make-today-assets.sh [path-to-always-today-repo]
#
# Requires ImageMagick and rsvg-convert (brew install imagemagick librsvg).
set -euo pipefail
cd "$(dirname "$0")/.."

APP="${1:-$HOME/dev/always-today}"
SHOTS="$APP/app/build/screenshots"
LOGO="$APP/docs/logo/cut-reflect.svg"

[ -f "$LOGO" ] || { echo "No logo at $LOGO — pass the Always Today repo path." >&2; exit 1; }
[ -d "$SHOTS" ] || { echo "No screenshots at $SHOTS — run the ScreensTest in the app repo first." >&2; exit 1; }

mkdir -p assets/today

# ---- the icon ------------------------------------------------------------------------------------
# The logo in amber on the dark brown square, as guzh.uk's own favicon sits on it: the same two
# colours as the dark palette's --paper and --accent, so it reads on light and dark tabs alike.
# The logo's paths are drawn in currentColor on a 32-unit box starting one unit down (viewBox 0 1 32 32);
# here they are scaled to 76% and centred on a 32 square.
PATHS="$(sed -n '/<mask/,/<\/svg>/p' "$LOGO" | sed '/<\/svg>/d')"
cat > assets/today/icon.svg <<EOF
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="7" fill="#241F1A"/>
  <g color="#E2B26F" transform="translate(3.84 1) scale(.76)">
  $PATHS
  </g>
</svg>
EOF
rsvg-convert -w 512 -h 512 assets/today/icon.svg -o assets/today/icon.png

# ---- screenshots ---------------------------------------------------------------------------------
# The phone renders are 412x900 at 2x. The three shots are cut to the page's 9:16 frame from the top;
# the platform rows take whole screens: the phone at its own 9:19.5, the Googlebook's window cut to
# the drawn laptop's 16:10, and the desktop window as it is (1280x800, already 16:10).
shot() { magick "$SHOTS/$1.png" -gravity North -crop 824x1465+0+0 +repage -resize 600x1067 -quality 82 "assets/today/$2.webp"; }
shot phone-light             shot-today
shot phone-quick-entry-dark  shot-quick-entry
shot phone-upcoming-light    shot-upcoming

plat() { magick "$SHOTS/$1.png" "${@:3}" -quality 82 "assets/today/$2.webp"; }
plat phone-dark       platform-android    -gravity North -crop 824x1786+0+0 +repage -resize 520x
plat googlebook-light platform-googlebook -gravity North -crop 1800x1125+0+0 +repage -resize 1400x
plat desktop-light    platform-windows    -resize 1400x

# ---- the 1200x630 link-preview card --------------------------------------------------------------
FONT_DIR="${TMPDIR:-/tmp}/guzh-og-fonts"
FONT="$FONT_DIR/Geist-var.ttf"
if [ ! -f "$FONT" ]; then
  mkdir -p "$FONT_DIR"
  curl -sL -o "$FONT" \
    "https://raw.githubusercontent.com/google/fonts/main/ofl/geist/Geist%5Bwght%5D.ttf"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# The dark palette, as on the page in dark mode: #241F1A ground, #EFE7DA ink, #C0B5A4 body,
# #E2B26F the logo. On the right, the app itself in Brown Study: the desktop's Today, cut to the list.
rsvg-convert -w 168 -h 168 assets/today/icon.svg -o "$TMP/icon.png"
magick "$SHOTS/desktop-dark.png" -crop 1900x1120+0+0 +repage -resize 760x448! -alpha set \
  \( -size 760x448 xc:none -fill white -draw 'roundrectangle 0,0 759,447 14,14' \) \
  -compose DstIn -composite "$TMP/shot.png"
magick -size 1200x630 xc:'#241F1A' \
  "$TMP/shot.png" -gravity NorthWest -geometry +560+150 -compose Over -composite \
  "$TMP/icon.png" -geometry +80+86 -composite \
  -fill none -stroke 'rgba(239,231,218,0.16)' -strokewidth 2 -draw 'roundrectangle 560,150 1319,597 14,14' \
  -font "$FONT" -gravity NorthWest \
  -fill '#EFE7DA' -stroke '#EFE7DA' -strokewidth 0.5 -pointsize 60 \
  -annotate +80+290 'Always Today' \
  -stroke none -fill '#E2B26F' -pointsize 34 \
  -annotate +80+376 'What am I doing today?' \
  -fill '#C0B5A4' -pointsize 25 \
  -annotate +80+446 'A calm to-do list for phone, Googlebook,' \
  -annotate +80+482 'Windows and the Linux terminal.' \
  -annotate +80+530 'Free on one device. Sync from £18 a year.' \
  -depth 8 -strip assets/today/og.png

echo "assets/today/: $(ls assets/today | tr '\n' ' ')"
