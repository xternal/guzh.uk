#!/usr/bin/env bash
# Regenerate the packed IANA timezone -> coordinates table inside index.html.
#
# The page picks light or dark from the reader's local sunrise and sunset. It
# needs a latitude and longitude to do that, and takes them from the timezone
# name rather than the geolocation API: no permission prompt, no network call,
# nothing about the reader leaves the page.
#
# Run this when the tzdb ships new or renamed zones (a couple of times a year).
# Reads /usr/share/zoneinfo/zone.tab, which macOS and every Linux already have.
#
#   ./tools/make-tz.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - <<'PY'
import re, pathlib
from collections import defaultdict

TAB = pathlib.Path("/usr/share/zoneinfo/zone.tab")
if not TAB.exists():
    raise SystemExit("no %s — install tzdata" % TAB)

def parse(c):
    # ISO 6709, either +DDMM+DDDMM or +DDMMSS+DDDMMSS
    m = re.match(r'^([+-]\d{2})(\d{2})(\d{2})?([+-]\d{3})(\d{2})(\d{2})?$', c)
    s1 = 1 if m.group(1)[0] == '+' else -1
    s2 = 1 if m.group(4)[0] == '+' else -1
    return (round(int(m.group(1)) + s1*(int(m.group(2))/60 + int(m.group(3) or 0)/3600)),
            round(int(m.group(4)) + s2*(int(m.group(5))/60 + int(m.group(6) or 0)/3600)))

zones = {}
for line in TAB.read_text().splitlines():
    if line.startswith("#") or not line.strip():
        continue
    f = line.split("\t")
    zones[f[2].strip()] = parse(f[1])

# Zones browsers still report that zone.tab no longer carries a row for.
# Check with: node -e 'console.log(Intl.supportedValuesOf("timeZone").join("\n"))'
ALIAS = {
    "Africa/Asmera": "Africa/Asmara",
    "America/Buenos_Aires": "America/Argentina/Buenos_Aires",
    "America/Catamarca": "America/Argentina/Catamarca",
    "America/Coral_Harbour": "America/Atikokan",
    "America/Cordoba": "America/Argentina/Cordoba",
    "America/Godthab": "America/Nuuk",
    "America/Indianapolis": "America/Indiana/Indianapolis",
    "America/Jujuy": "America/Argentina/Jujuy",
    "America/Louisville": "America/Kentucky/Louisville",
    "America/Mendoza": "America/Argentina/Mendoza",
    "Asia/Calcutta": "Asia/Kolkata",
    "Asia/Katmandu": "Asia/Kathmandu",
    "Asia/Rangoon": "Asia/Yangon",
    "Asia/Saigon": "Asia/Ho_Chi_Minh",
    "Atlantic/Faeroe": "Atlantic/Faroe",
    "Europe/Kiev": "Europe/Kyiv",
    "Pacific/Enderbury": "Pacific/Kanton",
    "Pacific/Ponape": "Pacific/Pohnpei",
    "Pacific/Truk": "Pacific/Chuuk",
}
missing = [a for a, c in ALIAS.items() if c not in zones]
if missing:
    raise SystemExit("alias targets no longer in zone.tab: %s" % ", ".join(missing))
for a, c in ALIAS.items():
    zones[a] = zones[c]

# "Region:City lat lon,City lat lon|Region:..." — the region prefix repeats
# hundreds of times, so hoisting it out is most of the saving.
grouped = defaultdict(list)
for z, (la, lo) in sorted(zones.items()):
    head, _, rest = z.partition("/")
    grouped[head].append("%s %d %d" % (rest, la, lo))
blob = "|".join("%s:%s" % (k, ",".join(v)) for k, v in sorted(grouped.items()))

for bad in ('"', "\\", "<", "&"):
    if bad in blob:
        raise SystemExit("packed table contains %r, which would break the inline script" % bad)

page = pathlib.Path("index.html")
src = page.read_text()
pat = re.compile(r'(var PACKED = ")[^"]*(";)')
if not pat.search(src):
    raise SystemExit("could not find the PACKED table in index.html")
page.write_text(pat.sub(lambda m: m.group(1) + blob + m.group(2), src, count=1))
print("wrote %d zones (%d incl. aliases), %d bytes packed" % (len(zones) - len(ALIAS), len(zones), len(blob)))
PY
