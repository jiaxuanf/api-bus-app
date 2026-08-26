#!/usr/bin/env python3
"""Distil data/rail.json from cheeaun/sgraildata.

The upstream GeoJSON is 1.1 MB of station points, exits, line geometry and platform
polygons. The app needs four fields per station, so this pulls out ~20 KB and vendors it
into the repo — same origin as the page, no third-party fetch at runtime, and the rail
network changes a few times a decade rather than a few times a day.

    python3 scripts/build-rail-data.py

LRT is deliberately excluded: the Bukit Panjang, Sengkang and Punggol lines are loops, and
station-code order does not describe a loop's travel direction. Including them would
produce confidently wrong journeys. Their MRT interchange stations are kept.
"""
import json, re, ssl, subprocess, sys, urllib.request
from datetime import datetime, timezone

SRC = "https://raw.githubusercontent.com/cheeaun/sgraildata/master/data/v1/sg-rail.geojson"
OUT = "data/rail.json"
MRT_LINES = {"NS", "EW", "CG", "NE", "CC", "CE", "DT", "TE", "JS", "JW", "JE", "CR", "CP"}

def fetch(url):
    """Some Python installs (notably python.org builds on macOS) ship without a CA
    bundle, so urllib raises on every HTTPS call. Fall back to curl, which has one."""
    try:
        return urllib.request.urlopen(url).read().decode()
    except (ssl.SSLError, urllib.error.URLError) as e:
        print(f"  urllib failed ({e.__class__.__name__}), falling back to curl")
        return subprocess.run(["curl", "-sSLf", url], capture_output=True,
                              check=True, text=True).stdout


def main():
    print(f"fetching {SRC}")
    raw = json.loads(fetch(SRC))

    seen, stations = set(), []
    for f in raw["features"]:
        p = f["properties"]
        if f["geometry"]["type"] != "Point" or p.get("stop_type") != "station":
            continue
        codes = [c for c in (p.get("station_codes") or "").split("-") if c]
        # Tanah Merah is the junction of the Changi branch; upstream writes it bare as "CG"
        codes = ["CG0" if c == "CG" else c for c in codes]
        codes = [c for c in codes if re.match(r"^([A-Z]{2})(\d+)([A-Z]?)$", c)
                 and re.match(r"^[A-Z]{2}", c).group(0) in MRT_LINES]
        if not codes:
            continue                      # LRT-only station, or an unnumbered code
        key = (p["name"], tuple(sorted(codes)))
        if key in seen:
            continue
        seen.add(key)
        lng, lat = f["geometry"]["coordinates"][:2]
        stations.append({"name": p["name"], "codes": sorted(codes),
                         "lat": round(lat, 6), "lng": round(lng, 6)})

    stations.sort(key=lambda s: s["name"])
    out = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source": SRC,
        "note": "MRT only. LRT loops are excluded - see the module docstring.",
        "stations": stations,
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, separators=(",", ":"))
    lines = {}
    for s in stations:
        for c in s["codes"]:
            lines.setdefault(re.match(r"^[A-Z]{2}", c).group(0), 0)
            lines[re.match(r"^[A-Z]{2}", c).group(0)] += 1
    print(f"wrote {OUT}: {len(stations)} stations across {len(lines)} lines")
    for ln, n in sorted(lines.items()):
        print(f"  {ln}: {n}")

if __name__ == "__main__":
    sys.exit(main())
