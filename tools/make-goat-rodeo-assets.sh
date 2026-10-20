#!/usr/bin/env bash
# Regenerate assets/goat-rodeo/* — the icon and the OG card for /goat-rodeo/privacy/.
#
# Like tools/make-weather-assets.sh, nothing is hand-made here. Both come from the game's own Google
# Play artwork in its repo, so the page, its link preview and the store listing always agree:
#
#   store/google-play/images/icon.svg           the launcher icon: the goat's face, amber horns,
#                                               on the dark brown square
#   store/google-play/images/featureGraphic.png the 1024x500 Play banner: the name, the line
#                                               "Build the trap course together. Then race through
#                                               it." and a canyon level with its traps and the flag
#
#   ./tools/make-goat-rodeo-assets.sh [path-to-goat-rodeo-repo]
#
# Requires ImageMagick and rsvg-convert (brew install imagemagick librsvg).
set -euo pipefail
cd "$(dirname "$0")/.."

APP="${1:-$HOME/dev/goat-rodeo}"
IMAGES="$APP/store/google-play/images"

[ -f "$IMAGES/icon.svg" ] || { echo "No icon at $IMAGES/icon.svg — pass the Goat Rodeo repo path." >&2; exit 1; }
[ -f "$IMAGES/featureGraphic.png" ] || { echo "No feature graphic at $IMAGES/featureGraphic.png." >&2; exit 1; }

mkdir -p assets/goat-rodeo

# ---- the icon ------------------------------------------------------------------------------------
# The game's own icon, unchanged: the tab icon, and drawn at 180 px for the home-screen icon.
cp "$IMAGES/icon.svg" assets/goat-rodeo/icon.svg
rsvg-convert -w 180 -h 180 assets/goat-rodeo/icon.svg -o assets/goat-rodeo/icon.png

# ---- the 1200x630 link-preview card --------------------------------------------------------------
# The Play banner is 2.05:1 and the card 1.90:1, so it is scaled to the card's height (1290x630) and
# trimmed on the right, where there is only sky: the goat, the name and the line on the left stay
# whole, and the flag, at 1115 px, stays in. Kept to 256 colours: in full colour the banner's sky
# makes a 370 KB card, over the 300 KB WhatsApp will show as a preview; this is under 200 KB.
magick "$IMAGES/featureGraphic.png" -resize x630 -gravity West -crop 1200x630+0+0 +repage \
  -dither FloydSteinberg -colors 256 -strip PNG8:assets/goat-rodeo/og.png

echo "assets/goat-rodeo/: $(ls assets/goat-rodeo | tr '\n' ' ')"
