"""Basic OSRM drive-time lookup for comparison against Google Maps.
Uses the public Nominatim geocoder and the public OSRM demo server via `requests`.
Runs two methods -- geocoded addresses vs. manually specified coordinates --
so the results (and their limitations) can be compared.
"""

from urllib.parse import quote

import requests

ORIGIN_ADDRESS = "1 Main St, Burlington, VT 05401"
DESTINATION_ADDRESS = "1 National Life Drive, Montpelier, VT 05602"

# Method 1: geocode addresses via OSM's free Nominatim service (same
# data source OSRM itself routes on) to get precise coordinates.
nominatim_url = "https://nominatim.openstreetmap.org/search"
headers = {"User-Agent": "drivetime-script"}
geocoded_origin = requests.get(nominatim_url, params={"q": ORIGIN_ADDRESS, "format": "json", "limit": 1}, headers=headers).json()[0]
geocoded_destination = requests.get(nominatim_url, params={"q": DESTINATION_ADDRESS, "format": "json", "limit": 1}, headers=headers).json()[0]

route_url = f"https://router.project-osrm.org/route/v1/driving/{geocoded_origin['lon']},{geocoded_origin['lat']};{geocoded_destination['lon']},{geocoded_destination['lat']}"
geocoded_route = requests.get(route_url, params={"overview": "false"}).json()["routes"][0]
geocoded_duration = geocoded_route["duration"] / 60
geocoded_distance = geocoded_route["distance"] / 1000

# Method 2: manually specified coordinates (approximate, hand-picked --
# no geocoding step, so Nominatim's usage-policy limits don't apply here).
manual_origin = {"lon": -73.2121, "lat": 44.4759}
manual_destination = {"lon": -72.5745, "lat": 44.2612}

route_url = f"https://router.project-osrm.org/route/v1/driving/{manual_origin['lon']},{manual_origin['lat']};{manual_destination['lon']},{manual_destination['lat']}"
manual_route = requests.get(route_url, params={"overview": "false"}).json()["routes"][0]
manual_duration = manual_route["duration"] / 60
manual_distance = manual_route["distance"] / 1000

google_url = (
    f"https://www.google.com/maps/dir/?api=1"
    f"&origin={quote(ORIGIN_ADDRESS)}"
    f"&destination={quote(DESTINATION_ADDRESS)}"
)

# Discrepancy & limitations:
# - Any gap between Method 1 and Method 2 comes from coordinate precision:
#   manual coordinates are hand-picked approximations and may snap to a
#   different nearby road segment than the geocoded point.
# - Both methods still rely on OSRM's generic per-road-type speed profile,
#   not real-world or live-traffic speeds like Google Maps uses -- so
#   neither will match Google's estimate exactly.
# - Method 1 depends on Nominatim's free public endpoint: rate-limited
#   (~1 request/sec), not meant for bulk use, and match quality varies by
#   region and address completeness.
# - Method 2 skips that limit but requires coordinates obtained some other
#   way, and has no address validation -- a wrong or stale coordinate
#   fails silently rather than erroring out.

print(f"Method 1 (geocoded address):   {geocoded_duration:.1f} minutes ({geocoded_distance:.1f} km)")
print(f"Method 2 (manual coordinates):  {manual_duration:.1f} minutes ({manual_distance:.1f} km)")
print(f"Compare to Google Maps: {google_url}")
