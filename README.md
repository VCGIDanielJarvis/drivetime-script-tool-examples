# drivetime-script-tool-examples

Four small, self-contained scripts that estimate the drive time between two
addresses and compare it against a manual Google Maps lookup. They exist to
demonstrate **why different routing methods produce different travel-time
estimates for the same trip** -- not to provide a production routing tool.

Each script computes the drive time from `1 Main St, Burlington, VT 05401` to
`1 National Life Drive, Montpelier, VT 05602` and prints a ready-to-click
Google Maps link for the same trip, so the result can be compared by hand.

## What's here

| Script | Language | Routing engine | Notes |
|---|---|---|---|
| [`drivetime_osrm.py`](drivetime_osrm.py) | Python | Public [OSRM](https://project-osrm.org/) demo server | Runs *two* sub-methods: geocoded addresses vs. hand-picked coordinates |
| [`drivetime_osrm.R`](drivetime_osrm.R) | R | Public OSRM demo server (via the `osrm` package) | Same two sub-methods as the Python version |
| [`drivetime_arcgis.py`](drivetime_arcgis.py) | Python | Local Esri Network Analyst dataset (via `arcpy`) | Requires a licensed ArcGIS Pro install and a local network dataset |
| [`drivetime_arcgis.R`](drivetime_arcgis.R) | R | Same local Network Analyst dataset | R has no native Network Analyst binding, so it calls `arcpy` via `reticulate` |

All four geocode addresses using OpenStreetMap's free [Nominatim](https://nominatim.org/)
service, so the geocoding step is identical across scripts -- any difference
in the final drive-time estimate comes from the routing engine itself.

## Why the results differ from Google Maps

- **OSRM** (`drivetime_osrm.*`) uses OpenStreetMap road data with a generic,
  static per-road-type speed profile. It has no live or historical traffic
  data, so its estimate reflects idealized free-flow driving at the engine's
  assumed speed for each road class -- not necessarily how people actually
  drive that road.
- **ArcGIS Network Analyst** (`drivetime_arcgis.*`) uses a commercial network
  dataset with modeled/historical speeds baked into the data itself, so its
  estimate tends to land closer to Google's than OSRM's does -- though still
  not an exact match, since Google also factors in live conditions at the
  moment you check.
- **Coordinate precision** matters too: the OSRM scripts also compare a
  precisely geocoded point against a hand-picked approximate coordinate for
  the same address, to show how that choice alone can shift a route's start
  point onto a different nearby road segment.

See the comments in each script for the specific limitations of its method
(e.g. Nominatim's public-use rate limits, lack of address validation for
hardcoded coordinates).

## Requirements

**OSRM scripts** (no account or API key needed -- call public free services):

- Python: `requests`
- R: `osrm`, `tmaptools`

**ArcGIS scripts** (require a licensed ArcGIS Pro install with the Network
Analyst extension, plus your own local network dataset):

- Python: run with the ArcGIS Pro Python environment (`arcpy` is bundled
  with ArcGIS Pro; `requests` is also needed)
- R: `reticulate`, `tmaptools`, and `reticulate::use_python()` pointed at
  your ArcGIS Pro Python environment

Before running `drivetime_arcgis.py` or `drivetime_arcgis.R`, replace the
placeholder path (`NETWORK_DATASET` / `network_dataset`) with the path to
your own network dataset.
